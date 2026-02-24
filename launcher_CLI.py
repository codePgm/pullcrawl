"""Unified Crawler CLI - Command Line Interface version."""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path
from urllib.parse import urlparse


class CrawlerCLI:
    """CLI launcher for selecting and running crawlers."""
    
    def __init__(self):
        self.is_crawling = False
        self.process = None
    
    def run(self, args):
        """Run crawler based on arguments."""
        # Validate inputs
        if not args.url:
            print("❌ Error: URL is required")
            return 1
        
        # Check prerequisites
        ok, error_msg = self._check_prerequisites(args.crawler_type)
        if not ok:
            print(f"❌ Error: {error_msg}")
            return 1
        
        # Convert output dir to absolute path
        output_dir = os.path.abspath(args.output_dir)
        
        # Run appropriate crawler
        if args.crawler_type == "simple":
            return self._run_simple_crawler(
                args.url, 
                args.max_pages, 
                args.delay, 
                output_dir
            )
        else:
            return self._run_advanced_crawler(
                args.url,
                args.max_pages,
                output_dir,
                args.depth,
                args.render
            )
    
    def _check_prerequisites(self, crawler_type):
        """Check if required tools are installed."""
        if crawler_type == "simple":
            # Check Python packages
            try:
                import requests
                import bs4
                return True, ""
            except ImportError as e:
                return False, f"필수 패키지 누락: {e.name}\n실행: pip install requests beautifulsoup4"
        
        else:  # advanced
            # Check Scrapy
            try:
                result = subprocess.run(["scrapy", "version"], capture_output=True, text=True)
                if result.returncode != 0:
                    return False, "Scrapy가 설치되지 않았습니다.\n\nsetup_advanced.bat을 먼저 실행하세요!"
                return True, ""
            except FileNotFoundError:
                return False, "Scrapy가 설치되지 않았습니다.\n\nsetup_advanced.bat을 먼저 실행하세요!"
            except Exception as e:
                return False, f"Scrapy 확인 중 오류: {str(e)}"
    
    def _run_simple_crawler(self, url, max_pages, delay, output_dir):
        """Run simple crawler."""
        try:
            print("="*60)
            print("간단 크롤러 시작")
            print("="*60)
            print(f"URL: {url}")
            print(f"최대 페이지: {max_pages}")
            print(f"출력: {output_dir}")
            print("")
            
            # Import and run simple crawler
            sys.path.insert(0, str(Path(__file__).parent / "simple_crawler"))
            from crawler import DoxygenCrawler
            
            def log_func(msg):
                print(msg)
            
            def should_continue():
                return True
            
            crawler = DoxygenCrawler(
                url, max_pages, delay, output_dir,
                log_func, should_continue
            )
            results = crawler.crawl()
            
            if results:
                print(f"\n{'='*60}")
                print("결과 저장 중...")
                
                json_file = crawler.save_json()
                files_msg = crawler.save_txt()
                
                print(f"✓ JSONL: {json_file}")
                print(f"✓ TXT 파일: {files_msg}")
                print(f"{'='*60}\n")
                print(f"✅ 완료! 총 {len(results)}개 페이지 수집")
                print(f"\n📁 출력 위치:")
                print(f"  - TXT: {output_dir}/simple_crawler/")
                print(f"  - JSON: {output_dir}/simple_json/pages.jsonl")
                
                return 0
            else:
                print("\n❌ 크롤링 실패")
                return 1
        
        except Exception as e:
            print(f"\n❌ 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    def _run_advanced_crawler(self, url, max_pages, output_dir, depth, render):
        """Run advanced Scrapy crawler."""
        try:
            # Extract domain from URL
            parsed = urlparse(url)
            domain = parsed.netloc
            
            print("="*60)
            print("고급 크롤러 (Scrapy) 시작")
            print("="*60)
            print(f"URL: {url}")
            print(f"도메인: {domain}")
            print(f"최대 페이지: {max_pages}")
            print(f"깊이: {depth}")
            print(f"렌더링: {'사용' if render else '사용 안 함'}")
            print(f"출력: {output_dir}")
            print("")
            
            # Build Scrapy command
            scrapy_dir = Path(__file__).parent / "scrapy_crawler"
            
            cmd = [
                "scrapy", "crawl", "site",
                "-a", f"seed={url}",
                "-a", f"allowed_domains={domain}",
                "-a", f"out_dir={output_dir}",
                "-a", f"max_pages={max_pages}",
                "-a", f"max_depth={depth}",
                "-a", f"render={1 if render else 0}"
            ]
            
            # Run Scrapy with real-time output
            self.process = subprocess.Popen(
                cmd,
                cwd=str(scrapy_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output with smart idle detection
            last_activity = time.time()
            max_idle_time = 180  # 3분간 진행 없으면 강제 종료
            last_page_count = 0
            
            # 숨길 로그 패턴 (더 포괄적으로)
            skip_patterns = [
                '[asyncio] ERROR',
                'AssertionError',
                'ScrapyDeprecationWarning',
                '[py.warnings] WARNING',
                'Traceback',
                'File "',
                'self._context.run',
                'assert f is self._write_fut',
                'handle: <Handle',
                '~~~~~~~~~~~~~~~~~',
                '^^^^^^^^^^^^',
                '[readability.readability] INFO',
                'ruthless removal',
                '_ProactorBaseWritePipeTransport',
                '_loop_writing()',
                'INFO: Scrapy',
                'INFO: Versions',
                'INFO: Enabled',
                'Telnet',
                'Started loop on separate thread',
                'download handler',
                'spider middlewares',
                'downloader middlewares',
                'item pipelines',
                'Overridden settings',
                "'lxml':",
                "'libxml2':",
                "'cssselect':",
                "'parsel':",
                "'w3lib':",
                "'Twisted':",
                "'Python':",
                "'pyOpenSSL':",
                "'cryptography':",
                "'Platform':"
            ]
            
            for line in iter(self.process.stdout.readline, ''):
                # 불필요한 로그 필터링
                if any(pattern in line for pattern in skip_patterns):
                    continue
                
                # 빈 줄이나 공백만 있는 줄도 스킵
                if not line.strip():
                    continue
                
                print(line.rstrip())
                
                # Check for ACTUAL progress (page count increasing)
                if 'Crawled' in line and 'pages' in line:
                    try:
                        # Extract page count: "Crawled 16 pages"
                        parts = line.split('Crawled')[1].split('pages')[0].strip()
                        current_pages = int(parts)
                        
                        # Only reset timer if pages increased
                        if current_pages > last_page_count:
                            last_activity = time.time()
                            last_page_count = current_pages
                    except:
                        pass
                
                # Also reset on other important events
                if 'Spider opened' in line or 'Launching browser' in line or '[✓]' in line:
                    last_activity = time.time()
                
                # Check if closing (give it 30 seconds to finish)
                if 'Closing spider' in line:
                    print("\n⚠️  Spider 종료 중... 30초 대기")
                    max_idle_time = 30  # Reduce timeout when closing
                
                # Force kill if idle too long
                idle_time = time.time() - last_activity
                if idle_time > max_idle_time:
                    print(f"\n⚠️  {int(idle_time)}초간 진행 없음. 강제 종료합니다...")
                    self.process.kill()
                    break
            
            # Wait for process to finish
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("\n⚠️  프로세스가 응답하지 않음. 강제 종료...")
                self.process.kill()
                self.process.wait()
            
            if self.process.returncode == 0:
                print("\n✅ 크롤링 완료!")
                print(f"\n📁 출력:")
                print(f"  - TXT: {output_dir}/scrapy_crawler/")
                print(f"  - JSON: {output_dir}/scrapy_json/pages.jsonl")
                return 0
            elif self.process.returncode is None:
                # Process killed due to timeout
                print("\n⚠️  프로세스 강제 종료됨 (타임아웃)")
                print(f"\n📁 출력:")
                print(f"  - TXT: {output_dir}/scrapy_crawler/")
                print(f"  - JSON: {output_dir}/scrapy_json/pages.jsonl")
                return 0
            else:
                print(f"\n❌ 오류 발생 (코드: {self.process.returncode})")
                return 1
        
        except FileNotFoundError:
            print("\n❌ Scrapy를 찾을 수 없습니다.")
            print("\nsetup_advanced.bat을 먼저 실행하세요!")
            return 1
        
        except Exception as e:
            print(f"\n❌ 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="통합 웹 크롤러 - CLI 버전",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 간단 크롤러 사용
  python launcher_CLI.py -t simple -u "https://example.com/docs/index.html" -m 100

  # 고급 크롤러 사용 (렌더링 없음)
  python launcher_CLI.py -t advanced -u "https://vertx.io/docs/" -m 50 --no-render

  # 출력 폴더 지정
  python launcher_CLI.py -t simple -u "https://example.com" -o ./my_output
        """
    )
    
    # Required arguments
    parser.add_argument(
        "-t", "--type",
        dest="crawler_type",
        choices=["simple", "advanced"],
        required=True,
        help="크롤러 타입: simple (빠름, 정적 HTML) 또는 advanced (느림, SPA)"
    )
    
    parser.add_argument(
        "-u", "--url",
        required=True,
        help="시작 URL"
    )
    
    # Optional arguments
    parser.add_argument(
        "-m", "--max-pages",
        type=int,
        default=500,
        help="최대 페이지 수 (기본값: 500)"
    )
    
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        default="./crawl_output",
        help="출력 디렉토리 (기본값: ./crawl_output)"
    )
    
    # Simple crawler options
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=1.0,
        help="요청 간격 (초, 간단 크롤러만 해당, 기본값: 1.0)"
    )
    
    # Advanced crawler options
    parser.add_argument(
        "--depth",
        type=int,
        default=4,
        help="최대 깊이 (고급 크롤러만 해당, 기본값: 4)"
    )
    
    parser.add_argument(
        "--no-render",
        dest="render",
        action="store_false",
        default=True,
        help="Playwright 렌더링 비활성화 (고급 크롤러만 해당)"
    )
    
    # Version
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 2.0"
    )
    
    args = parser.parse_args()
    
    # Run crawler
    cli = CrawlerCLI()
    exit_code = cli.run(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
