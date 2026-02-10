"""GUI application for Doxygen crawler."""

import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

from crawler import DoxygenCrawler
from config.constants import DEFAULT_OUTPUT_DIR, DEFAULT_MAX_PAGES, DEFAULT_DELAY


class DoxygenCrawlerGUI:
    """GUI for Doxygen documentation crawler."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Doxygen 문서 크롤러")
        self.root.geometry("900x700")
        
        self.is_crawling = False
        self.crawler = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL input
        ttk.Label(main_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=70).grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="설정", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(options_frame, text="최대 페이지:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.max_pages_var = tk.StringVar(value=str(DEFAULT_MAX_PAGES))
        ttk.Entry(options_frame, textvariable=self.max_pages_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(options_frame, text="요청 간격 (초):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.delay_var = tk.StringVar(value=str(DEFAULT_DELAY))
        ttk.Entry(options_frame, textvariable=self.delay_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(options_frame, text="출력 폴더:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir_var = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        ttk.Entry(options_frame, textvariable=self.output_dir_var, width=30).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(options_frame, text="찾아보기", command=self._browse_output_dir).grid(row=1, column=3, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="크롤링 시작", command=self._start_crawl)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="중지", command=self._stop_crawl, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="결과 폴더 열기", command=self._open_output_folder).grid(row=0, column=2, padx=5)
        
        # Progress
        ttk.Label(main_frame, text="진행 상황:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.StringVar(value="대기 중...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Log
        ttk.Label(main_frame, text="로그:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, width=80, height=20, wrap=tk.WORD)
        self.log_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
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
    
    def _start_crawl(self):
        """Start crawling process."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력하세요.")
            return
        
        try:
            max_pages = int(self.max_pages_var.get())
            delay = float(self.delay_var.get())
        except ValueError:
            messagebox.showerror("오류", "최대 페이지 수와 요청 간격은 숫자여야 합니다.")
            return
        
        self.is_crawling = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(
            target=self._run_crawl,
            args=(url, max_pages, delay),
            daemon=True
        )
        thread.start()
    
    def _run_crawl(self, url, max_pages, delay):
        """Run crawl in background thread."""
        try:
            output_dir = self.output_dir_var.get()
            
            self._log(f"Doxygen 문서 크롤링 시작")
            self._log(f"URL: {url}")
            self._log(f"최대 페이지: {max_pages}")
            self._log("")
            
            self.crawler = DoxygenCrawler(
                url, max_pages, delay, output_dir,
                self._log, lambda: self.is_crawling
            )
            results = self.crawler.crawl()
            
            if self.is_crawling and results:
                self._log(f"\n{'='*60}")
                self._log("결과 저장 중...")
                
                json_file = self.crawler.save_json()
                files_msg = self.crawler.save_txt()
                
                self._log(f"✓ JSON: {json_file}")
                self._log(f"✓ 원문 TXT: {files_msg}")
                self._log(f"{'='*60}\n")
                self._log(f"완료! 총 {len(results)}개 페이지 수집")
                
                self.progress_var.set(f"완료! {len(results)}개 페이지")
                messagebox.showinfo("완료", f"크롤링 완료!\n{len(results)}개 페이지 수집")
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
    
    def _stop_crawl(self):
        """Stop crawling process."""
        self.is_crawling = False
        self.progress_var.set("중지 중...")
        self._log("\n크롤링 중지 요청됨...")


def main():
    """Run GUI application."""
    root = tk.Tk()
    app = DoxygenCrawlerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
