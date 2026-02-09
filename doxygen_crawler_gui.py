#!/usr/bin/env python3
"""
Doxygen Documentation Crawler - GUI Version
Doxygen으로 생성된 API 문서 전용 크롤러
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import time
import json
import os
from pathlib import Path
import threading
import re


class DoxygenCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Doxygen Documentation Crawler")
        self.root.geometry("900x700")
        
        self.crawler = None
        self.is_crawling = False
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL Input
        ttk.Label(main_frame, text="문서 URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=70)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.url_entry.insert(0, "https://developer.nvidia.com/docs/drive/drive-os/6.0.10/public/drive-os-linux-sdk/api_reference/index.html")
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="옵션", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(options_frame, text="최대 페이지 수:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.max_pages_var = tk.StringVar(value="500")
        ttk.Entry(options_frame, textvariable=self.max_pages_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(options_frame, text="요청 간격(초):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.delay_var = tk.StringVar(value="1.0")
        ttk.Entry(options_frame, textvariable=self.delay_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(options_frame, text="출력 폴더:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir_var = tk.StringVar(value="doxygen_crawl")
        ttk.Entry(options_frame, textvariable=self.output_dir_var, width=30).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(options_frame, text="찾아보기", command=self.browse_output_dir).grid(row=1, column=3, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="크롤링 시작", command=self.start_crawl)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="중지", command=self.stop_crawl, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="결과 폴더 열기", command=self.open_output_folder).grid(row=0, column=2, padx=5)
        
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
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
    
    def open_output_folder(self):
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showwarning("경고", f"출력 폴더가 존재하지 않습니다: {output_dir}")
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_crawl(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요.")
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
            target=self.run_crawl,
            args=(url, max_pages, delay),
            daemon=True
        )
        thread.start()
    
    def run_crawl(self, url, max_pages, delay):
        try:
            output_dir = self.output_dir_var.get()
            
            self.log(f"Doxygen 문서 크롤링 시작")
            self.log(f"URL: {url}")
            self.log(f"최대 페이지: {max_pages}\n")
            
            self.crawler = DoxygenCrawler(
                url, max_pages, delay, output_dir,
                self.log, lambda: self.is_crawling
            )
            results = self.crawler.crawl()
            
            if self.is_crawling and results:
                self.log(f"\n{'='*60}")
                self.log("결과 저장 중...")
                
                json_file = self.crawler.save_json()
                files_msg, summary_txt = self.crawler.save_txt()
                
                self.log(f"✓ JSON: {json_file}")
                self.log(f"✓ 원문 TXT: {files_msg}")
                self.log(f"✓ 요약 TXT: {summary_txt}")
                self.log(f"{'='*60}\n")
                self.log(f"완료! 총 {len(results)}개 페이지 수집")
                
                self.progress_var.set(f"완료! {len(results)}개 페이지")
                messagebox.showinfo("완료", f"크롤링 완료!\n{len(results)}개 페이지 수집")
            else:
                self.log("\n중지됨")
                self.progress_var.set("중지됨")
        
        except Exception as e:
            self.log(f"\n오류: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            self.progress_var.set("오류 발생")
            messagebox.showerror("오류", f"크롤링 중 오류:\n{str(e)}")
        
        finally:
            self.progress_bar.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_crawling = False
    
    def stop_crawl(self):
        self.is_crawling = False
        self.log("\n중지 요청...")


class DoxygenCrawler:
    """Specialized crawler for Doxygen documentation"""
    
    # Common Doxygen file patterns
    DOXYGEN_PAGES = [
        'index.html',
        'modules.html',
        'namespaces.html',
        'classes.html',
        'files.html',
        'annotated.html',
        'functions.html',
        'globals.html',
        'pages.html',
    ]
    
    def __init__(self, base_url, max_pages, delay, output_dir, log_func, should_continue):
        self.base_url = base_url
        self.max_pages = max_pages
        self.delay = delay
        self.output_dir = output_dir
        self.log = log_func
        self.should_continue = should_continue
        self.visited_urls = set()
        self.pages_data = []
        
        parsed = urlparse(base_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"
        self.base_path = '/'.join(parsed.path.split('/')[:-1]) + '/'
        
        self.log(f"도메인: {self.domain}")
        self.log(f"기본 경로: {self.base_path}")
        
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
        
        # Must be HTML or PDF
        if not (full_url.endswith('.html') or full_url.endswith('.htm') or full_url.endswith('.pdf')):
            return False
        
        return True
    
    def find_all_html_files(self, soup, current_url):
        """Find all HTML file links in the page"""
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip anchors
            if href.startswith('#'):
                continue
            
            full_url = urljoin(current_url, href)
            
            if self.is_valid_url(full_url):
                links.add(full_url)
        
        return list(links)
    
    def get_common_doxygen_pages(self):
        """Get URLs for common Doxygen index pages"""
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
                    self.log("    ⚠️  PDF 라이브러리 없음 (pip install pypdf)")
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
            self.log(f"    ❌ PDF 추출 오류: {str(e)}")
            return None
    
    def extract_content(self, soup):
        content = {
            'title': '',
            'headings': [],
            'text': '',
            'code_blocks': []
        }
        
        # Extract title - prioritize h1 over title tag for Doxygen
        h1_tag = soup.find('h1')
        title_tag = soup.find('title')
        
        if h1_tag:
            content['title'] = h1_tag.get_text(strip=True)
        elif title_tag:
            content['title'] = title_tag.get_text(strip=True)
        
        # Doxygen usually has content in specific divs
        main_selectors = [
            '.contents',  # Doxygen main content class
            '#doc-content',
            'main',
            'article',
            '.textblock',
            'body'
        ]
        
        main = None
        for selector in main_selectors:
            main = soup.select_one(selector)
            if main:
                break
        
        if not main:
            main = soup.find('body')
        
        if main:
            # Headings
            for heading in main.find_all(['h1', 'h2', 'h3', 'h4']):
                content['headings'].append({
                    'level': heading.name,
                    'text': heading.get_text(strip=True)
                })
            
            # Code blocks
            for code in main.find_all(['code', 'pre', '.fragment']):
                code_text = code.get_text(strip=True)
                if len(code_text) > 10:
                    content['code_blocks'].append(code_text)
            
            # Remove unwanted elements
            for element in main(['script', 'style', 'nav', 'header', 'footer', '.navpath']):
                element.decompose()
            
            # Text
            content['text'] = main.get_text(separator='\n', strip=True)
        
        return content
    
    def crawl_page(self, url):
        self.log(f"  처리: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Check if PDF
            if url.endswith('.pdf'):
                self.log(f"    📄 PDF 파일 감지")
                pdf_text = self.extract_pdf_text(response.content)
                
                if pdf_text:
                    # Extract title from filename
                    title = url.split('/')[-1].replace('.pdf', '')
                    
                    self.log(f"    ✓ PDF 변환 완료: {title}")
                    
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
                # Extract filename from URL
                filename = url.split('/')[-1]
                if filename.endswith('.html'):
                    title = filename.replace('.html', '').replace('_', ' ')
                else:
                    title = filename
                content['title'] = title
            
            self.log(f"    ✓ {content.get('title', 'Untitled')}")
            
            return {
                'url': url,
                'status': 'success',
                'soup': soup,  # Keep for link extraction
                'file_type': 'html',
                **content
            }
        
        except Exception as e:
            self.log(f"    ❌ {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'soup': None
            }
    
    def crawl(self):
        self.log(f"\n{'='*60}")
        self.log("1단계: 시작 페이지 및 공통 Doxygen 페이지 확인")
        self.log(f"{'='*60}\n")
        
        # Start with common Doxygen pages
        seed_urls = self.get_common_doxygen_pages()
        
        # Add base URL if not already in list (avoid duplicates)
        if self.base_url not in seed_urls:
            seed_urls.insert(0, self.base_url)
        
        self.log(f"시드 URL {len(seed_urls)}개 확인 중...")
        
        all_links = set()
        
        # Check seed URLs and collect links
        for url in seed_urls:
            if not self.should_continue():
                break
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, timeout=10, headers=headers)
                
                if response.status_code == 200:
                    self.log(f"  ✓ 발견: {url.split('/')[-1]}")
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = self.find_all_html_files(soup, url)
                    all_links.update(links)
                    all_links.add(url)
                    
                    time.sleep(0.5)  # Short delay
            
            except:
                pass
        
        self.log(f"\n발견된 HTML 페이지: {len(all_links)}개")
        
        if all_links:
            self.log("\n발견된 페이지 예시:")
            for idx, link in enumerate(sorted(all_links)[:10], 1):
                filename = link.split('/')[-1]
                self.log(f"  {idx}. {filename}")
            if len(all_links) > 10:
                self.log(f"  ... 외 {len(all_links) - 10}개")
        
        self.log(f"\n{'='*60}")
        self.log(f"2단계: 각 페이지 크롤링 (최대 {min(len(all_links), self.max_pages)}개)")
        self.log(f"{'='*60}\n")
        
        # Crawl each page - prioritize base URL first
        sorted_links = sorted(all_links)
        
        # Move base URL to front if it exists
        if self.base_url in sorted_links:
            sorted_links.remove(self.base_url)
            sorted_links.insert(0, self.base_url)
        
        for idx, url in enumerate(sorted_links[:self.max_pages], 1):
            if not self.should_continue():
                break
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            page_data = self.crawl_page(url)
            
            # Remove soup from stored data
            if 'soup' in page_data:
                del page_data['soup']
            
            self.pages_data.append(page_data)
            
            self.log(f"  진행: {idx}/{min(len(all_links), self.max_pages)}\n")
            
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
        
        base_dir = Path(self.output_dir, "crawl_원문")
        summary_file = Path(self.output_dir, "crawl_요약본", "크롤링_요약.txt")
        
        # Get current timestamp
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save each page directly in crawl_원문 folder
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
            
            # Create filename: 001_[PDF]_Title_20240205_143022.txt
            filename = f"{idx:03d}_{type_marker}{clean_title}_{timestamp}.txt"
            filepath = base_dir / filename
            
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
        
        # Summary file (목록)
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("Doxygen 문서 크롤링 요약\n")
            f.write("="*80 + "\n")
            f.write(f"기준 URL: {self.base_url}\n")
            f.write(f"크롤링 날짜: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"총 페이지: {len(self.pages_data)}\n")
            f.write(f"성공: {sum(1 for p in self.pages_data if p['status'] == 'success')}\n")
            f.write(f"실패: {sum(1 for p in self.pages_data if p['status'] == 'error')}\n")
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
        
        return f"{len(saved_files)}개 파일 저장됨", str(summary_file)


def main():
    root = tk.Tk()
    app = DoxygenCrawlerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
