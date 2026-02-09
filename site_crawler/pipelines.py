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
        self.jsonl_path = os.path.join(self.out_dir, "pages.jsonl")
        self._fh = open(self.jsonl_path, "a", encoding="utf-8")

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
        self._fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._fh.flush()
        return item


class JsonlPipeline:
    """Write page JSONL without downloading images."""

    def open_spider(self, spider):
        self.out_dir = getattr(spider, "out_dir", "./dump")
        os.makedirs(self.out_dir, exist_ok=True)
        self.jsonl_path = os.path.join(self.out_dir, "pages.jsonl")
        self._fh = open(self.jsonl_path, "a", encoding="utf-8")

    def close_spider(self, spider):
        try:
            self._fh.close()
        except Exception:
            pass

    def process_item(self, item, spider):
        rec = dict(item)
        rec.setdefault("fetched_at", now_iso())
        self._fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._fh.flush()
        return item
