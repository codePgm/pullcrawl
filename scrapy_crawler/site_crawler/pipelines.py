import hashlib
import json
import os
from datetime import datetime, timezone
from urllib.parse import urlsplit

import scrapy
from scrapy.pipelines.images import ImagesPipeline


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ImageAndJsonlPipeline(ImagesPipeline): # X
    """Download images (img + css_bg) and write page.

    - Expects item['images'] entries with src
    - Adds local_path after download
    - Writes pages.jsonl to out_dir
    """

    def open_spider(self, spider):
        super().open_spider(spider)
        self.out_dir = getattr(spider, "out_dir", "./dump")
        os.makedirs(self.out_dir, exist_ok=True)
        
        self.limit = 495000
        self.current_file_idx = 1
        self.current_char_count = 0
        
        self.jsonl_path = self._get_jsonl_path(self.current_file_idx)
        self._fh = open(self.jsonl_path, "w", encoding="utf-8")

    def _get_jsonl_path(self, idx):
        if idx == 1:
            return os.path.join(self.out_dir, "pages.jsonl")
        else:
            return os.path.join(self.out_dir, f"pages_{idx}.jsonl")

    def close_spider(self, spider):
        try:
            self._fh.close()
        except Exception:
            pass

    def get_media_requests(self, item, info):
        imgs = item.get("images") or []
        for img in imgs:
            src = img.get("src")
            if not src:
                continue
            # svg는 pillow에서 처리 못해서 제외
            ext = os.path.splitext(urlsplit(src).path)[1].lower()
            if ext == ".svg":
                continue
            yield scrapy.Request(
                src,
                meta={
                    "page_key": item.get("page_key"),
                    "img_src": src,
                },
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        page_key = request.meta.get("page_key") or "unknown"
        img_src = request.meta.get("img_src") or request.url
        host = urlsplit(request.url).netloc.replace(":", "_")
        ext = os.path.splitext(urlsplit(request.url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            ext = ".bin"
        img_key = sha256(img_src)[:24]
        return os.path.join("images", host, page_key, f"{img_key}{ext}")

    def item_completed(self, results, item, info):
        # Map downloaded image local paths back into item['images']
        src_to_path = {}
        for ok, res in results:
            if not ok:
                continue
            src = res.get("url")
            path = res.get("path")
            if src and path:
                src_to_path[src] = path

        for img in item.get("images") or []:
            src = img.get("src")
            if src in src_to_path:
                img["local_path"] = src_to_path[src]

        # Write JSONL
        rec = dict(item)
        rec.setdefault("fetched_at", now_iso())
        
        item_str = json.dumps(rec, ensure_ascii=False) + "\n"
        item_len = len(item_str)
        
        # Check limit (495,000 chars)
        if self.current_char_count + item_len > self.limit and self.current_char_count > 0:
            self._fh.close()
            self.current_file_idx += 1
            self.jsonl_path = self._get_jsonl_path(self.current_file_idx)
            self._fh = open(self.jsonl_path, "w", encoding="utf-8")
            self.current_char_count = 0
            
        self._fh.write(item_str)
        self._fh.flush()
        self.current_char_count += item_len
        
        return item


class JsonlPipeline:
    """Write page JSONL and TXT files."""

    def open_spider(self, spider):
        self.out_dir = getattr(spider, "out_dir", "./dump")
        
        # Create directory structure: crawl_output/scrapy_json/ and crawl_output/scrapy_crawler/
        self.json_dir = os.path.join(self.out_dir, "scrapy_json")
        self.txt_dir = os.path.join(self.out_dir, "scrapy_crawler")
        
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.txt_dir, exist_ok=True)
        
        self.limit = 495000
        self.current_file_idx = 1
        self.current_char_count = 0
        
        self.jsonl_path = self._get_jsonl_path(self.current_file_idx)
        self._fh = open(self.jsonl_path, "w", encoding="utf-8")
        
        self.page_counter = 0

    def _get_jsonl_path(self, idx):
        if idx == 1:
            return os.path.join(self.json_dir, "pages.jsonl")
        else:
            return os.path.join(self.json_dir, f"pages_{idx}.jsonl")

    def close_spider(self, spider):
        try:
            self._fh.close()
        except Exception:
            pass

    def process_item(self, item, spider):
        # Save JSONL
        rec = dict(item)
        rec.setdefault("fetched_at", now_iso())
        
        item_str = json.dumps(rec, ensure_ascii=False) + "\n"
        item_len = len(item_str)
        
        # Check limit (495,000 chars)
        if self.current_char_count + item_len > self.limit and self.current_char_count > 0:
            self._fh.close()
            self.current_file_idx += 1
            self.jsonl_path = self._get_jsonl_path(self.current_file_idx)
            self._fh = open(self.jsonl_path, "w", encoding="utf-8")
            self.current_char_count = 0
            
        self._fh.write(item_str)
        self._fh.flush()
        self.current_char_count += item_len
        
        # Save TXT file
        self.page_counter += 1
        self._save_txt_file(item, self.page_counter)
        
        return item
    
    def _save_txt_file(self, item, page_num):
        """Save individual TXT file for each page."""
        from datetime import datetime
        
        # Clean title for filename
        title = item.get('title', 'Untitled')
        clean_title = self._clean_filename(title)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"{page_num:03d}_{clean_title}_{timestamp}.txt"
        filepath = os.path.join(self.txt_dir, filename)
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"페이지 {page_num}: {title}\n")
            f.write("="*80 + "\n")
            f.write(f"URL: {item.get('url', '')}\n")
            f.write(f"크롤링 시간: {timestamp}\n")
            f.write(f"렌더링: {'예' if item.get('rendered') else '아니오'}\n")
            f.write(f"깊이: {item.get('depth', 0)}\n")
            f.write("="*80 + "\n\n")
            
            # Main text
            text = item.get('text', '')
            if text:
                f.write("내용:\n" + "-"*80 + "\n")
                f.write(text + "\n\n")
            
            # Out links
            out_links = item.get('out_links', [])
            if out_links:
                f.write(f"외부 링크 ({len(out_links)}개):\n" + "-"*80 + "\n")
                for link in out_links[:20]:  # First 20 links
                    f.write(f"  • {link}\n")
                if len(out_links) > 20:
                    f.write(f"  ... 외 {len(out_links) - 20}개\n")
                f.write("\n")
            
            # Images
            images = item.get('images', [])
            if images:
                f.write(f"이미지 ({len(images)}개):\n" + "-"*80 + "\n")
                for img in images[:10]:  # First 10 images
                    f.write(f"  • {img.get('src', '')}\n")
                    if img.get('alt'):
                        f.write(f"    Alt: {img.get('alt')}\n")
                if len(images) > 10:
                    f.write(f"  ... 외 {len(images) - 10}개\n")
    
    def _clean_filename(self, title: str, max_length: int = 50) -> str:
        """Clean title for use as filename."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        
        # Limit length
        if len(title) > max_length:
            title = title[:max_length]
        
        # Remove trailing dots and spaces
        title = title.rstrip('. ')
        
        return title or 'Untitled'
