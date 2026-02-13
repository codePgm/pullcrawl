"""Main Doxygen crawler class."""

import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config.constants import DOXYGEN_SEED_PAGES, USER_AGENT
from utils.url_utils import extract_domain, extract_base_path
from utils.text_utils import extract_title, extract_headings, extract_code_blocks, extract_text
from utils.pdf_utils import extract_pdf_text
from utils.file_utils import clean_filename, get_timestamp, ensure_directory


class DoxygenCrawler:
    """Crawler for Doxygen-generated API documentation."""
    
    def __init__(self, base_url: str, max_pages: int, delay: float, output_dir: str,
                 log_func=None, should_continue=None):
        self.base_url = base_url
        self.max_pages = max_pages
        self.delay = delay
        self.output_dir = output_dir
        self.log = log_func or print
        self.should_continue = should_continue or (lambda: True)
        
        self.visited_urls = set()
        self.pages_data = []
        
        # Parse base URL
        parsed = urlparse(base_url)
        self.domain = extract_domain(base_url)
        self.base_path = extract_base_path(base_url)
        
        # Create output directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary output directories."""
        ensure_directory(Path(self.output_dir))
    
    def _get_seed_urls(self) -> list[str]:
        """Get list of seed URLs to check."""
        seed_urls = []
        for page_name in DOXYGEN_SEED_PAGES:
            url = f"{self.domain}{self.base_path}{page_name}"
            seed_urls.append(url)
        
        # Add base URL if not already in list
        if self.base_url not in seed_urls:
            seed_urls.insert(0, self.base_url)
        
        return seed_urls
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL should be crawled.
        
        Uses a blacklist approach to block known non-HTML files
        while allowing modern URLs without extensions.
        """
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
        
        # File extension blacklist (block these types)
        BLOCKED_EXTENSIONS = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico', '.bmp',
            # Styles & Scripts
            '.css', '.js', '.json', '.xml', '.map',
            # Archives
            '.zip', '.tar', '.gz', '.rar', '.7z',
            # Media
            '.mp4', '.mp3', '.avi', '.mov', '.wmv', '.flv', '.wav',
            # Fonts
            '.woff', '.woff2', '.ttf', '.eot', '.otf',
            # Documents (non-HTML/PDF)
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Other
            '.txt', '.csv', '.log',
        }
        
        # Get filename from URL path
        path = urlparse(full_url).path
        if not path or path == '/':
            return True
        
        filename = path.split('/')[-1]
        
        # If filename has extension
        if '.' in filename:
            # Get extension (lowercase)
            ext = '.' + filename.split('.')[-1].lower()
            
            # Block if in blacklist
            if ext in BLOCKED_EXTENSIONS:
                return False
            
            # Explicitly allow HTML and PDF
            if ext in {'.html', '.htm', '.pdf'}:
                return True
            
            # Unknown extensions: allow (could be query params like ?v=1.0)
            return True
        
        # No extension: allow (modern URLs like /docs/guide/)
        return True

    
    def _find_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Find all valid HTML links in the page."""
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            if href.startswith('#'):
                continue
            
            full_url = urljoin(current_url, href)
            
            if self._is_valid_url(full_url):
                links.add(full_url)
        
        return list(links)
    
    def _extract_content(self, soup: BeautifulSoup) -> dict:
        """Extract content from HTML soup."""
        # Find main content area
        main_selectors = ['.contents', '#doc-content', 'main', 'article', '.textblock', 'body']
        main = None
        for selector in main_selectors:
            main = soup.select_one(selector)
            if main:
                break
        
        if not main:
            main = soup.find('body')
        
        content = {
            'title': extract_title(soup),
            'headings': extract_headings(main) if main else [],
            'code_blocks': extract_code_blocks(main) if main else [],
            'text': extract_text(main) if main else ''
        }
        
        return content
    
    def _crawl_page(self, url: str) -> dict:
        """Crawl a single page."""
        self.log(f"  처리: {url}")
        
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Check Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Handle PDF
            if 'application/pdf' in content_type or url.endswith('.pdf'):
                self.log(f"    📄 PDF 파일 감지")
                pdf_text = extract_pdf_text(response.content)
                
                if pdf_text:
                    title = url.split('/')[-1].replace('.pdf', '') or 'PDF Document'
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
            
            # Skip non-HTML content types
            if content_type and not any(t in content_type for t in ['text/html', 'application/xhtml', 'text/plain']):
                self.log(f"    ⊘ HTML 아님: {content_type}")
                return {
                    'url': url,
                    'status': 'skipped',
                    'error': f'Non-HTML content: {content_type}',
                    'file_type': content_type.split(';')[0]
                }
            
            # HTML processing
            soup = BeautifulSoup(response.content, 'html.parser')
            content = self._extract_content(soup)
            
            # Use filename from URL if title is generic or empty
            title = content.get('title', '')
            if not title or title == 'NVIDIA DRIVE OS Linux SDK API Reference':
                # Try to get meaningful name from URL
                path_parts = url.rstrip('/').split('/')
                filename = path_parts[-1] if path_parts else ''
                
                if filename.endswith('.html'):
                    title = filename.replace('.html', '').replace('_', ' ')
                elif filename:
                    title = filename.replace('_', ' ').replace('-', ' ')
                else:
                    # Use second-to-last part (like 'java' from /docs/vertx-core/java/)
                    title = path_parts[-2] if len(path_parts) > 1 else 'Untitled'
                
                content['title'] = title
            
            self.log(f"    ✓ {content.get('title', 'Untitled')}")
            
            return {
                'url': url,
                'status': 'success',
                'soup': soup,
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

    
    def crawl(self) -> list[dict]:
        """Main crawl method."""
        self.log(f"\n{'='*60}")
        self.log("1단계: 시작 페이지 및 공통 Doxygen 페이지 확인")
        self.log(f"{'='*60}\n")
        
        seed_urls = self._get_seed_urls()
        self.log(f"시드 URL {len(seed_urls)}개 확인 중...")
        
        all_links = set()
        
        # Check seed URLs and collect links
        for url in seed_urls:
            if not self.should_continue():
                break
            
            try:
                headers = {'User-Agent': USER_AGENT}
                response = requests.get(url, timeout=10, headers=headers)
                
                if response.status_code == 200:
                    self.log(f"  ✓ 발견: {url.split('/')[-1]}")
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = self._find_links(soup, url)
                    all_links.update(links)
                    all_links.add(url)
                    time.sleep(0.5)
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
            page_data = self._crawl_page(url)
            
            # Remove soup from stored data
            if 'soup' in page_data:
                del page_data['soup']
            
            self.pages_data.append(page_data)
            
            self.log(f"  진행: {idx}/{min(len(all_links), self.max_pages)}\n")
            
            if idx < len(sorted_links):
                time.sleep(self.delay)
        
        return self.pages_data
    
    def save_json(self) -> str:
        """Save results as JSONL (JSON Lines) format - one JSON per line."""
        # New path: crawl_output/simple_json/pages.jsonl
        json_dir = Path(self.output_dir, "simple_json")
        json_dir.mkdir(parents=True, exist_ok=True)
        json_file = json_dir / "pages.jsonl"
        
        # Write JSONL format (one JSON object per line)
        with open(json_file, 'w', encoding='utf-8') as f:
            for page in self.pages_data:
                if page['status'] != 'success':
                    continue
                
                # Convert to Scrapy-like format
                jsonl_item = {
                    'url': page['url'],
                    'title': page.get('title', ''),
                    'text': page.get('text', ''),
                    'headings': page.get('headings', []),
                    'code_blocks': page.get('code_blocks', []),
                    'file_type': page.get('file_type', 'html'),
                    'rendered': False,  # Simple crawler doesn't render
                    'depth': 0,
                    'out_links': [],  # Simple crawler doesn't track outlinks
                    'images': []  # Simple crawler doesn't collect images
                }
                
                # Write one JSON per line
                f.write(json.dumps(jsonl_item, ensure_ascii=False) + '\n')
        
        return str(json_file)
    
    def save_txt(self) -> str:
        """Save results as individual TXT files."""
        # New path: crawl_output/simple_crawler/
        txt_dir = Path(self.output_dir, "simple_crawler")
        txt_dir.mkdir(parents=True, exist_ok=True)
        timestamp = get_timestamp()
        
        saved_files = []
        for idx, page in enumerate(self.pages_data, 1):
            if page['status'] != 'success':
                continue
            
            # Clean title for filename
            title = page.get('title', 'Untitled')
            clean_title = clean_filename(title)
            
            # Check if PDF
            file_type = page.get('file_type', 'html')
            type_marker = '[PDF]_' if file_type == 'pdf' else ''
            
            # Create filename
            filename = f"{idx:03d}_{type_marker}{clean_title}_{timestamp}.txt"
            filepath = txt_dir / filename
            
            # Write file
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
        
        return f"{len(saved_files)}개 파일 저장됨"
