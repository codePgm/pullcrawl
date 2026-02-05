#!/usr/bin/env python3
"""
Doxygen Documentation Crawler - Command-line Version
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
import argparse
from pathlib import Path


class DoxygenCrawler:
    """Doxygen 문서 전용 크롤러"""
    
    DOXYGEN_PAGES = [
        'index.html', 'modules.html', 'namespaces.html', 'classes.html',
        'files.html', 'annotated.html', 'functions.html', 'globals.html', 'pages.html'
    ]
    
    def __init__(self, base_url, max_pages=500, delay=1.0, output_dir="doxygen_crawl"):
        self.base_url = base_url
        self.max_pages = max_pages
        self.delay = delay
        self.output_dir = output_dir
        self.visited_urls = set()
        self.pages_data = []
        
        parsed = urlparse(base_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"
        self.base_path = '/'.join(parsed.path.split('/')[:-1]) + '/'
        
        print(f"도메인: {self.domain}")
        print(f"기본 경로: {self.base_path}\n")
        
        self.create_directories()
    
    def create_directories(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir, "crawl_원문").mkdir(parents=True, exist_ok=True)
        Path(self.output_dir, "crawl_요약본").mkdir(parents=True, exist_ok=True)
        Path(self.output_dir, "crawlJson").mkdir(parents=True, exist_ok=True)
    
    def is_valid_url(self, url):
        if not url or url in self.visited_urls:
            return False
        if url.startswith('#') or url.startswith('javascript:') or url.startswith('mailto:'):
            return False
        
        parsed = urlparse(url)
        if parsed.netloc and parsed.netloc != urlparse(self.domain).netloc:
            return False
        
        full_url = urljoin(self.domain, url)
        if not full_url.startswith(f"{self.domain}{self.base_path}"):
            return False
        if not (full_url.endswith('.html') or full_url.endswith('.htm') or full_url.endswith('.pdf')):
            return False
        
        return True
    
    def find_all_html_files(self, soup, current_url):
        links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('#'):
                continue
            full_url = urljoin(current_url, href)
            if self.is_valid_url(full_url):
                links.add(full_url)
        return list(links)
    
    def get_common_doxygen_pages(self):
        pages = []
        for page_name in self.DOXYGEN_PAGES:
            url = f"{self.domain}{self.base_path}{page_name}"
            pages.append(url)
        return pages
    
    def extract_pdf_text(self, pdf_content):
        """Extract text from PDF content"""
        try:
            import io
            try:
                from pypdf import PdfReader
            except ImportError:
                try:
                    from PyPDF2 import PdfReader
                except ImportError:
                    print("    ⚠️  PDF 라이브러리 없음 (pip install pypdf)")
                    return None
            
            pdf_file = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            
            text = []
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"[페이지 {page_num}]\n{page_text}\n")
            
            return '\n'.join(text)
        
        except Exception as e:
            print(f"    ❌ PDF 추출 오류: {str(e)}")
            return None
    
    def extract_content(self, soup):
        content = {'title': '', 'headings': [], 'text': '', 'code_blocks': []}
        
        # Extract title - prioritize h1 over title tag for Doxygen
        h1_tag = soup.find('h1')
        title_tag = soup.find('title')
        
        if h1_tag:
            content['title'] = h1_tag.get_text(strip=True)
        elif title_tag:
            content['title'] = title_tag.get_text(strip=True)
        
        main_selectors = ['.contents', '#doc-content', 'main', 'article', '.textblock', 'body']
        main = None
        for selector in main_selectors:
            main = soup.select_one(selector)
            if main:
                break
        
        if not main:
            main = soup.find('body')
        
        if main:
            for heading in main.find_all(['h1', 'h2', 'h3', 'h4']):
                content['headings'].append({
                    'level': heading.name,
                    'text': heading.get_text(strip=True)
                })
            
            for code in main.find_all(['code', 'pre', '.fragment']):
                code_text = code.get_text(strip=True)
                if len(code_text) > 10:
                    content['code_blocks'].append(code_text)
            
            for element in main(['script', 'style', 'nav', 'header', 'footer', '.navpath']):
                element.decompose()
            
            content['text'] = main.get_text(separator='\n', strip=True)
        
        return content
    
    def crawl_page(self, url):
        print(f"  처리: {url.split('/')[-1]}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Check if PDF
            if url.endswith('.pdf'):
                print(f"    📄 PDF 파일 감지")
                pdf_text = self.extract_pdf_text(response.content)
                
                if pdf_text:
                    title = url.split('/')[-1].replace('.pdf', '')
                    print(f"    ✓ PDF 변환 완료: {title}")
                    
                    return {
                        'url': url,
                        'status': 'success',
                        'title': title,
                        'headings': [],
                        'text': pdf_text,
                        'code_blocks': [],
                        'file_type': 'pdf'
                    }
                else:
                    return {
                        'url': url,
                        'status': 'error',
                        'error': 'PDF 텍스트 추출 실패',
                        'file_type': 'pdf'
                    }
            
            # HTML processing
            soup = BeautifulSoup(response.content, 'html.parser')
            content = self.extract_content(soup)
            
            # If title is generic or empty, use filename from URL
            title = content.get('title', '')
            if not title or title == 'NVIDIA DRIVE OS Linux SDK API Reference':
                filename = url.split('/')[-1]
                if filename.endswith('.html'):
                    title = filename.replace('.html', '').replace('_', ' ')
                else:
                    title = filename
                content['title'] = title
            
            print(f"    ✓ {content.get('title', 'Untitled')}")
            
            return {'url': url, 'status': 'success', 'file_type': 'html', **content}
        except Exception as e:
            print(f"    ❌ {str(e)}")
            return {'url': url, 'status': 'error', 'error': str(e)}
    
    def crawl(self):
        print(f"\n{'='*80}")
        print("Doxygen 문서 크롤링")
        print(f"{'='*80}\n")
        
        print("1단계: 공통 Doxygen 페이지 확인 중...")
        
        seed_urls = self.get_common_doxygen_pages()
        seed_urls.insert(0, self.base_url)
        
        all_links = set()
        
        for url in seed_urls:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, timeout=10, headers=headers)
                
                if response.status_code == 200:
                    print(f"  ✓ {url.split('/')[-1]}")
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = self.find_all_html_files(soup, url)
                    all_links.update(links)
                    all_links.add(url)
                    time.sleep(0.5)
            except:
                pass
        
        print(f"\n✓ 발견된 HTML 페이지: {len(all_links)}개")
        
        if all_links:
            print("\n발견된 페이지 예시:")
            for idx, link in enumerate(sorted(all_links)[:10], 1):
                print(f"  {idx}. {link.split('/')[-1]}")
            if len(all_links) > 10:
                print(f"  ... 외 {len(all_links) - 10}개")
        
        print(f"\n2단계: 각 페이지 크롤링 (최대 {min(len(all_links), self.max_pages)}개)\n")
        
        sorted_links = sorted(all_links)
        for idx, url in enumerate(sorted_links[:self.max_pages], 1):
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            page_data = self.crawl_page(url)
            self.pages_data.append(page_data)
            
            print(f"  진행: {idx}/{min(len(all_links), self.max_pages)}\n")
            
            if idx < len(sorted_links):
                time.sleep(self.delay)
        
        return self.pages_data
    
    def save_json(self):
        json_file = Path(self.output_dir, "crawlJson", "crawl_results.json")
        results = {
            'base_url': self.base_url,
            'crawl_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_pages': len(self.pages_data),
                'successful_pages': sum(1 for p in self.pages_data if p['status'] == 'success'),
                'failed_pages': sum(1 for p in self.pages_data if p['status'] == 'error'),
            },
            'pages': self.pages_data
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return str(json_file)
    
    def save_txt(self):
        import re
        
        full_dir = Path(self.output_dir, "crawl_원문")
        summary_file = Path(self.output_dir, "crawl_요약본", "크롤링_요약.txt")
        
        # Get current timestamp
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save each page as individual file
        saved_files = []
        for idx, page in enumerate(self.pages_data, 1):
            if page['status'] != 'success':
                continue
            
            # Clean title for filename
            title = page.get('title', 'Untitled')
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
            
            # Check if PDF
            file_type = page.get('file_type', 'html')
            type_marker = '[PDF]_' if file_type == 'pdf' else ''
            
            # Create filename: 001_[PDF]_Title_20240205_143022.txt or 001_Title_20240205_143022.txt
            filename = f"{idx:03d}_{type_marker}{clean_title}_{timestamp}.txt"
            filepath = full_dir / filename
            
            # Write individual file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write(f"페이지 {idx}: {title}\n")
                if file_type == 'pdf':
                    f.write("[PDF 파일에서 변환됨]\n")
                f.write("="*80 + "\n")
                f.write(f"URL: {page['url']}\n")
                f.write(f"크롤링 시간: {timestamp}\n")
                f.write(f"파일 형식: {file_type.upper()}\n")
                f.write("="*80 + "\n\n")
                
                if page.get('headings'):
                    f.write("목차:\n" + "-"*80 + "\n")
                    for heading in page['headings']:
                        indent = "  " * (int(heading['level'][1]) - 1)
                        f.write(f"{indent}• {heading['text']}\n")
                    f.write("\n")
                
                if page.get('text'):
                    f.write("내용:\n" + "-"*80 + "\n")
                    f.write(page['text'] + "\n\n")
                
                if page.get('code_blocks'):
                    f.write(f"코드 블록 ({len(page['code_blocks'])}개):\n" + "-"*80 + "\n")
                    for code_idx, code in enumerate(page['code_blocks'], 1):
                        f.write(f"\n[코드 {code_idx}]\n{code}\n")
            
            saved_files.append(str(filepath))
        
        # Summary file
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("Doxygen 문서 크롤링 요약\n")
            f.write("="*80 + "\n")
            f.write(f"기준 URL: {self.base_url}\n")
            f.write(f"총 페이지: {len(self.pages_data)}\n")
            f.write(f"성공: {sum(1 for p in self.pages_data if p['status'] == 'success')}\n")
            f.write(f"HTML 파일: {sum(1 for p in self.pages_data if p.get('file_type') == 'html')}\n")
            f.write(f"PDF 파일: {sum(1 for p in self.pages_data if p.get('file_type') == 'pdf')}\n")
            f.write(f"저장된 파일: {len(saved_files)}개\n")
            f.write("="*80 + "\n\n")
            
            f.write("저장된 파일 목록:\n")
            f.write("-"*80 + "\n")
            for idx, page in enumerate(self.pages_data, 1):
                if page['status'] != 'success':
                    continue
                
                title = page.get('title', 'Untitled')
                clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:100]
                file_type = page.get('file_type', 'html')
                type_marker = '[PDF]_' if file_type == 'pdf' else ''
                filename = f"{idx:03d}_{type_marker}{clean_title}_{timestamp}.txt"
                
                f.write(f"\n{idx}. {filename}\n")
                f.write(f"   제목: {title}\n")
                f.write(f"   형식: {file_type.upper()}\n")
                f.write(f"   URL: {page['url']}\n")
                if page.get('headings'):
                    f.write(f"   섹션: {len(page['headings'])}개\n")
                if page.get('text'):
                    preview = page['text'][:200].replace('\n', ' ')
                    f.write(f"   미리보기: {preview}...\n")
        
        return f"{len(saved_files)}개 파일", str(summary_file)
    
    def print_summary(self):
        print(f"\n{'='*80}")
        print("크롤링 완료!")
        print(f"{'='*80}")
        print(f"총 페이지: {len(self.pages_data)}")
        print(f"성공: {sum(1 for p in self.pages_data if p['status'] == 'success')}")
        print(f"실패: {sum(1 for p in self.pages_data if p['status'] == 'error')}")
        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description='Doxygen 문서 크롤러')
    parser.add_argument('url', help='크롤링할 Doxygen 문서 URL')
    parser.add_argument('--max-pages', type=int, default=500, help='최대 페이지 수 (기본: 500)')
    parser.add_argument('--delay', type=float, default=1.0, help='요청 간격(초) (기본: 1.0)')
    parser.add_argument('--output-dir', default='doxygen_crawl', help='출력 폴더 (기본: doxygen_crawl)')
    
    args = parser.parse_args()
    
    crawler = DoxygenCrawler(
        base_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay,
        output_dir=args.output_dir
    )
    
    crawler.crawl()
    
    json_file = crawler.save_json()
    files_msg, summary_txt = crawler.save_txt()
    
    print(f"✓ JSON: {json_file}")
    print(f"✓ 원문 TXT: {files_msg}")
    print(f"✓ 요약 TXT: {summary_txt}")
    
    crawler.print_summary()


if __name__ == '__main__':
    main()
