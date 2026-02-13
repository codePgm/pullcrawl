"""Unified Crawler Launcher - Choose between Simple and Advanced crawler."""

import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path


class CrawlerLauncher:
    """GUI launcher for selecting and running crawlers."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("통합 웹 크롤러")
        self.root.geometry("800x650")
        
        self.is_crawling = False
        self.process = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="통합 웹 크롤러", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Crawler Type Selection
        type_frame = ttk.LabelFrame(main_frame, text="크롤러 선택", padding="10")
        type_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.crawler_type = tk.StringVar(value="simple")
        
        simple_radio = ttk.Radiobutton(
            type_frame, 
            text="🚀 간단 크롤러 (추천) - Doxygen, Sphinx 등 정적 HTML 문서",
            variable=self.crawler_type, 
            value="simple",
            command=self._on_type_change
        )
        simple_radio.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        advanced_radio = ttk.Radiobutton(
            type_frame, 
            text="⚡ 고급 크롤러 - React, Vue, Angular 등 SPA 사이트 (느림, 복잡)",
            variable=self.crawler_type, 
            value="advanced",
            command=self._on_type_change
        )
        advanced_radio.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Description
        self.desc_label = ttk.Label(type_frame, text="", foreground="blue", wraplength=700)
        self.desc_label.grid(row=2, column=0, sticky=tk.W, padx=20, pady=5)
        
        # URL Input
        ttk.Label(main_frame, text="URL:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=70).grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Common Options
        common_frame = ttk.LabelFrame(main_frame, text="공통 설정", padding="10")
        common_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(common_frame, text="최대 페이지:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.max_pages_var = tk.StringVar(value="500")
        ttk.Entry(common_frame, textvariable=self.max_pages_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(common_frame, text="출력 폴더:").grid(row=0, column=2, sticky=tk.W, padx=20)
        self.output_dir_var = tk.StringVar(value="./crawl_output")
        ttk.Entry(common_frame, textvariable=self.output_dir_var, width=30).grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(common_frame, text="찾아보기", command=self._browse_output_dir).grid(row=0, column=4, padx=5)
        
        # Simple Crawler Options
        self.simple_frame = ttk.LabelFrame(main_frame, text="간단 크롤러 설정", padding="10")
        self.simple_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.simple_frame, text="요청 간격 (초):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.delay_var = tk.StringVar(value="1.0")
        ttk.Entry(self.simple_frame, textvariable=self.delay_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Advanced Crawler Options
        self.advanced_frame = ttk.LabelFrame(main_frame, text="고급 크롤러 설정", padding="10")
        self.advanced_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.advanced_frame, text="깊이 제한:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.depth_var = tk.StringVar(value="4")
        ttk.Entry(self.advanced_frame, textvariable=self.depth_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.render_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.advanced_frame, text="Playwright 렌더링 사용 (느리지만 SPA 지원)", 
                       variable=self.render_var).grid(row=0, column=2, sticky=tk.W, padx=20)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="크롤링 시작", command=self._start_crawl)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="중지", command=self._stop_crawl, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="결과 폴더 열기", command=self._open_output_folder).grid(row=0, column=2, padx=5)
        
        # Progress
        ttk.Label(main_frame, text="진행 상황:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.StringVar(value="대기 중...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=6, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Log
        ttk.Label(main_frame, text="로그:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, width=90, height=15, wrap=tk.WORD)
        self.log_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(9, weight=1)
        
        # Initial state
        self._on_type_change()
    
    def _on_type_change(self):
        """Handle crawler type change."""
        crawler_type = self.crawler_type.get()
        
        if crawler_type == "simple":
            # Show simple options, hide advanced
            self.simple_frame.grid()
            self.advanced_frame.grid_remove()
            
            self.desc_label.config(text="✓ 빠름 | ✓ 간단 | ✓ GUI | → NVIDIA, OpenCV, ROS 등 Doxygen/Sphinx 문서")
        else:
            # Show advanced options, hide simple
            self.simple_frame.grid_remove()
            self.advanced_frame.grid()
            
            self.desc_label.config(text="⚠ 느림 | ⚠ 복잡 | ⚠ 명령줄 | → Vert.x, React Docs 등 SPA 사이트")
    
    def _browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
    
    def _open_output_folder(self):
        """Open output folder in file explorer."""
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showwarning("경고", f"출력 폴더가 존재하지 않습니다:\n{output_dir}")
    
    def _log(self, message):
        """Add message to log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
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
    
    def _start_crawl(self):
        """Start crawling process."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력하세요.")
            return
        
        crawler_type = self.crawler_type.get()
        
        # Check prerequisites
        ok, error_msg = self._check_prerequisites(crawler_type)
        if not ok:
            messagebox.showerror("오류", error_msg)
            return
        
        try:
            max_pages = int(self.max_pages_var.get())
        except ValueError:
            messagebox.showerror("오류", "최대 페이지 수는 숫자여야 합니다.")
            return
        
        self.is_crawling = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.log_text.delete(1.0, tk.END)
        
        if crawler_type == "simple":
            thread = threading.Thread(
                target=self._run_simple_crawler,
                args=(url, max_pages),
                daemon=True
            )
            thread.start()
        else:
            thread = threading.Thread(
                target=self._run_advanced_crawler,
                args=(url, max_pages),
                daemon=True
            )
            thread.start()
    
    def _run_simple_crawler(self, url, max_pages):
        """Run simple crawler."""
        try:
            delay = float(self.delay_var.get())
            output_dir = self.output_dir_var.get()
            
            self._log("="*60)
            self._log("간단 크롤러 시작")
            self._log("="*60)
            self._log(f"URL: {url}")
            self._log(f"최대 페이지: {max_pages}")
            self._log(f"출력: {output_dir}")
            self._log("")
            
            # Import and run simple crawler
            sys.path.insert(0, str(Path(__file__).parent / "simple_crawler"))
            from crawler import DoxygenCrawler
            
            crawler = DoxygenCrawler(
                url, max_pages, delay, output_dir,
                self._log, lambda: self.is_crawling
            )
            results = crawler.crawl()
            
            if self.is_crawling and results:
                self._log(f"\n{'='*60}")
                self._log("결과 저장 중...")
                
                json_file = crawler.save_json()
                files_msg = crawler.save_txt()
                
                self._log(f"✓ JSONL: {json_file}")
                self._log(f"✓ TXT 파일: {files_msg}")
                self._log(f"{'='*60}\n")
                self._log(f"완료! 총 {len(results)}개 페이지 수집")
                self._log(f"\n출력 위치:")
                self._log(f"  - TXT: {output_dir}/simple_crawler/")
                self._log(f"  - JSON: {output_dir}/simple_json/pages.jsonl")
                
                self.progress_var.set(f"완료! {len(results)}개 페이지")
                messagebox.showinfo("완료", f"크롤링 완료!\n\n{len(results)}개 페이지 수집\n\n출력:\n- TXT: {output_dir}/simple_crawler/\n- JSON: {output_dir}/simple_json/pages.jsonl")
            else:
                self._log("\n중지됨")
                self.progress_var.set("중지됨")
        
        except Exception as e:
            self._log(f"\n오류: {str(e)}")
            import traceback
            self._log(traceback.format_exc())
            self.progress_var.set("오류 발생")
            messagebox.showerror("오류", f"크롤링 중 오류:\n{str(e)}")
        
        finally:
            self.is_crawling = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_bar.stop()
    
    def _run_advanced_crawler(self, url, max_pages):
        """Run advanced Scrapy crawler."""
        try:
            output_dir = self.output_dir_var.get()
            depth = int(self.depth_var.get())
            render = 1 if self.render_var.get() else 0
            
            # Convert to absolute path (important for Scrapy!)
            output_dir = os.path.abspath(output_dir)
            
            # Extract domain from URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            
            self._log("="*60)
            self._log("고급 크롤러 (Scrapy) 시작")
            self._log("="*60)
            self._log(f"URL: {url}")
            self._log(f"도메인: {domain}")
            self._log(f"최대 페이지: {max_pages}")
            self._log(f"깊이: {depth}")
            self._log(f"렌더링: {'사용' if render else '사용 안 함'}")
            self._log(f"출력: {output_dir}")
            self._log("")
            self._log("⚠️  Scrapy 실행 중... (별도 창에서 진행됩니다)")
            self._log("")
            
            # Build Scrapy command
            scrapy_dir = Path(__file__).parent / "scrapy_crawler"
            
            cmd = [
                "scrapy", "crawl", "site",
                "-a", f"seed={url}",
                "-a", f"allowed_domains={domain}",
                "-a", f"out_dir={output_dir}",  # Now absolute path!
                "-a", f"max_pages={max_pages}",
                "-a", f"max_depth={depth}",
                "-a", f"render={render}"
            ]
            
            # Run Scrapy
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
            
            for line in iter(self.process.stdout.readline, ''):
                if not self.is_crawling:
                    self.process.terminate()
                    break
                
                self._log(line.rstrip())
                
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
                if 'Spider opened' in line or 'Launching browser' in line:
                    last_activity = time.time()
                
                # Check if closing (give it 30 seconds to finish)
                if 'Closing spider' in line:
                    self._log("\n⚠️  Spider 종료 중... 30초 대기")
                    max_idle_time = 30  # Reduce timeout when closing
                
                # Force kill if idle too long
                idle_time = time.time() - last_activity
                if idle_time > max_idle_time:
                    self._log(f"\n⚠️  {int(idle_time)}초간 진행 없음. 강제 종료합니다...")
                    self.process.kill()  # KILL instead of terminate
                    break
            
            # Wait for process to finish
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._log("\n⚠️  프로세스가 응답하지 않음. 강제 종료...")
                self.process.kill()
                self.process.wait()
            
            if self.process.returncode == 0:
                self._log("\n✅ 크롤링 완료!")
                self.progress_var.set("완료!")
                messagebox.showinfo("완료", f"크롤링 완료!\n\n출력:\n- TXT: {output_dir}/scrapy_crawler/\n- JSON: {output_dir}/scrapy_json/pages.jsonl")
            elif self.process.returncode is None:
                # Process killed due to timeout
                self._log("\n⚠️  프로세스 강제 종료됨 (타임아웃)")
                self.progress_var.set("강제 종료됨")
                messagebox.showinfo("완료", f"크롤링 완료 (강제 종료)\n\n출력:\n- TXT: {output_dir}/scrapy_crawler/\n- JSON: {output_dir}/scrapy_json/pages.jsonl")
            else:
                self._log(f"\n❌ 오류 발생 (코드: {self.process.returncode})")
                self.progress_var.set("오류")
        
        except FileNotFoundError:
            self._log("\n❌ Scrapy를 찾을 수 없습니다.")
            self._log("\nscrapy_setup 폴더에서 setup.bat을 먼저 실행하세요!")
            messagebox.showerror("오류", "Scrapy가 설치되지 않았습니다.\n\nscrapy_setup/setup.bat을 실행하세요.")
        
        except Exception as e:
            self._log(f"\n오류: {str(e)}")
            import traceback
            self._log(traceback.format_exc())
            self.progress_var.set("오류 발생")
            messagebox.showerror("오류", f"크롤링 중 오류:\n{str(e)}")
        
        finally:
            self.is_crawling = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.progress_bar.stop()
    
    def _stop_crawl(self):
        """Stop crawling process."""
        self.is_crawling = False
        if self.process:
            self.process.terminate()
        self.progress_var.set("중지 중...")
        self._log("\n크롤링 중지 요청됨...")


def main():
    """Run unified crawler launcher."""
    root = tk.Tk()
    app = CrawlerLauncher(root)
    root.mainloop()


if __name__ == '__main__':
    main()
