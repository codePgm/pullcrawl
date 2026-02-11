import hashlib
from datetime import datetime, timezone

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from site_crawler.items import PageItem
from site_crawler.utils.urlnorm import normalize_url
from site_crawler.utils.text import extract_main_text
from site_crawler.utils.cssbg import extract_urls_from_css_text, unique


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SiteSpider(CrawlSpider):
    name = "site"

    custom_settings = {
        # 브라우저 비용 제어 (필요 시 조정)
        "CONCURRENT_REQUESTS": 16,
        # playwright 페이지 동시성은 settings.py의 PLAYWRIGHT_MAX_PAGES_PER_CONTEXT로 제어
    }

    rules = ()

    def __init__(
        self,
        seed: str,
        allowed_domains: str,
        out_dir: str = "./dump",
        max_pages: int = 500,
        max_depth: int = 4,
        profile: str | None = None,
        include_css_bg: int = 1,
        render: int = 1,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.start_urls = [seed]
        self.allowed_domains = [d.strip() for d in allowed_domains.split(",") if d.strip()]
        self.out_dir = out_dir
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.profile = profile
        self.include_css_bg = bool(int(include_css_bg))
        self.render_default = bool(int(render))

        self.seen = set()  # canonical url visited
        self.page_count = 0

        le = LinkExtractor(allow_domains=self.allowed_domains)
        self.rules = (
            Rule(le, callback="parse_page", follow=True),
        )
        self._compile_rules()

    def start_requests(self):
        for url in self.start_urls:
            yield self._make_request(url=url, depth=0)

    def _make_request(self, url: str, depth: int, *, force_render: bool = False):
        meta = {"depth": depth}

        # storage_state profile
        if self.profile:
            meta["auth_profile"] = self.profile

        # playwright 조건부
        if self.render_default or force_render:
            meta["playwright"] = True
            meta["playwright_include_page"] = True
            # context options: storage_state is loaded by a custom context factory pattern
            meta["playwright_context"] = self._pw_context_name()

        return scrapy.Request(url, callback=self.parse_page, meta=meta, dont_filter=False,
                              errback=self.errback_close_page)

    async def errback_close_page(self, failure):
        request = getattr(failure, "request", None)

        # 1) 원인 로그를 남겨서 "왜 seed가 실패했는지" 바로 보이게 함
        try:
            self.logger.error(
                "Request failed: url=%s meta_playwright=%s err=%r",
                getattr(request, "url", None),
                bool(getattr(request, "meta", {}).get("playwright")) if request else None,
                failure.value,
            )
        except Exception:
            self.logger.error("Request failed (logging error): %r", failure)

        # 2) playwright 페이지가 열려있으면 닫기
        if request is not None:
            page = request.meta.get("playwright_page")
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

        # 3) Playwright가 죽는(TargetClosedError 등) 케이스면 1회만 non-render로 폴백 재시도
        if request is not None and request.meta.get("playwright") and not request.meta.get("_pw_fallback_tried"):
            meta = dict(request.meta)
            meta["_pw_fallback_tried"] = True
            meta.pop("playwright", None)
            meta.pop("playwright_include_page", None)
            meta.pop("playwright_context", None)
            meta.pop("playwright_page", None)

            self.logger.warning("Retrying without Playwright: %s", request.url)
            yield request.replace(meta=meta, dont_filter=True)

    def _pw_context_name(self) -> str:
        # context name key; handler will reuse per context
        # e.g., "example.com:corp"
        dom = self.allowed_domains[0] if self.allowed_domains else "default"
        prof = self.profile or "default"
        return f"{dom}:{prof}"

    def _needs_render(self, response: scrapy.http.Response, text: str) -> bool:
        # Heuristics: short text or SPA markers
        # if len(text.strip()) < 200:
        #     return True
        body = response.text.lower()
        if "__next_data__" in body or "id=\"__next\"" in body:
            return True
        if "data-reactroot" in body or "id=\"root\"" in body:
            return True
        return False

    def _is_text_response(self, response: scrapy.http.Response) -> bool:
        if not isinstance(response, scrapy.http.TextResponse):
            return False
        content_type = response.headers.get(b"Content-Type", b"").decode("latin-1").lower()
        if not content_type:
            return True
        return content_type.startswith("text/") or "html" in content_type or "xml" in content_type

    async def _extract_css_bg_via_playwright(self, page):
        # computed styles from DOM (candidate-based)
        # returns list of urls
        js = r"""
        () => {
          const urls = new Set();
          const els = Array.from(document.querySelectorAll('div,section,a,span,main,header'));
          // pick top N by area to reduce cost
          const scored = els.map(el => {
            const r = el.getBoundingClientRect();
            return { el, area: Math.max(0, r.width) * Math.max(0, r.height) };
          }).filter(x => x.area > 2500);
          scored.sort((a,b)=>b.area-a.area);
          const top = scored.slice(0, 400).map(x=>x.el);

          const rx = /url\((['\"]?)(.*?)\1\)/gi;
          for (const el of top) {
            const bg = getComputedStyle(el).backgroundImage;
            if (!bg || bg === 'none') continue;
            let m;
            while ((m = rx.exec(bg)) !== null) {
              const u = (m[2]||'').trim();
              if (u && !u.startsWith('data:')) urls.add(u);
            }
          }
          return Array.from(urls);
        }
        """
        return await page.evaluate(js)

    async def parse_page(self, response: scrapy.http.Response):
        # page limit - close spider when reached
        if self.page_count >= self.max_pages:
            self.logger.info(f"Reached max_pages limit ({self.max_pages}). Closing spider.")
            # Close the spider gracefully
            from scrapy.exceptions import CloseSpider
            raise CloseSpider(f'Reached max_pages limit: {self.max_pages}')
        
        url = response.url
        depth = int(response.meta.get("depth", 0))
        if depth > self.max_depth:
            return

        # canonical/normalize
        canon = normalize_url(url, url) or url
        if canon in self.seen:
            return
        self.seen.add(canon)

        # text 형태 데이터만 취급
        if not self._is_text_response(response):
            return

        # Extract main text (readability)
        title, text = extract_main_text(response.text, url=url)

        rendered = bool(response.meta.get("playwright"))

        # If not rendered but looks like SPA, re-request with playwright
        if (not rendered) and self._needs_render(response, text):
            yield self._make_request(url=url, depth=depth, force_render=True)
            return

        # Images from <img>
        images = []
        for img in response.css("img"):
            src = img.attrib.get("src") or ""
            if not src and img.attrib.get("srcset"):
                # pick last candidate (often largest)
                srcset = img.attrib.get("srcset")
                parts = [p.strip().split(" ")[0] for p in srcset.split(",") if p.strip()]
                if parts:
                    src = parts[-1]
            if not src:
                continue
            abs_src = normalize_url(response.url, src, strip_tracking=False)
            if not abs_src:
                continue
            images.append({"type": "img", "src": abs_src, "alt": img.attrib.get("alt")})

        # CSS background-image (static extraction)
        if self.include_css_bg:
            css_urls = []
            # inline style attrs
            for sel in response.css("*[style]"):
                st = sel.attrib.get("style")
                if st:
                    css_urls.extend(extract_urls_from_css_text(st))
            # <style> blocks
            for st in response.css("style::text").getall():
                css_urls.extend(extract_urls_from_css_text(st))
            css_urls = unique(css_urls)
            for u in css_urls:
                abs_u = normalize_url(response.url, u, strip_tracking=False)
                if abs_u:
                    images.append({"type": "css_bg", "src": abs_u, "alt": None})

        # CSS background-image (computed via Playwright) - only if rendered and include_css_bg
        if rendered and self.include_css_bg and response.meta.get("playwright_page") is not None:
            page = response.meta["playwright_page"]
            try:
                bg_urls = await self._extract_css_bg_via_playwright(page)
                for u in bg_urls:
                    abs_u = normalize_url(response.url, u, strip_tracking=False)
                    if abs_u:
                        images.append({"type": "css_bg", "src": abs_u, "alt": None})
            finally:
                # Important: close page to avoid leaks
                await page.close()

        # Dedup images by src
        seen_img = set()
        dedup_images = []
        for im in images:
            s = im.get("src")
            if not s or s in seen_img:
                continue
            seen_img.add(s)
            dedup_images.append(im)

        # Out links (internal)
        out_links = []
        for href in response.css("a::attr(href)").getall():
            nu = normalize_url(response.url, href)
            if not nu:
                continue
            # same-domain filter (simple)
            if self.allowed_domains and not any(d in nu for d in self.allowed_domains):
                continue
            out_links.append(nu)

        out_links = list(dict.fromkeys(out_links))

        self.page_count += 1
        page_key = sha1(canon)[:16]

        item = PageItem(
            url=canon,
            final_url=url,
            fetched_at=now_iso(),
            status=getattr(response, "status", None),
            rendered=rendered,
            title=title,
            text=text,
            images=dedup_images,
            out_links=out_links,
            depth=depth,
            auth_profile=response.meta.get("auth_profile"),
            page_key=page_key,
        )

        yield item

        # Follow links manually with depth control (CrawlSpider rules also follow, but this allows our depth limit)
        next_depth = depth + 1
        if next_depth <= self.max_depth:
            for u in out_links:
                if u not in self.seen:
                    yield self._make_request(url=u, depth=next_depth)
