import scrapy


class PageItem(scrapy.Item):
    url = scrapy.Field()
    final_url = scrapy.Field()
    fetched_at = scrapy.Field()
    status = scrapy.Field()
    rendered = scrapy.Field()

    title = scrapy.Field()
    text = scrapy.Field()

    # [{type: 'img'|'css_bg', src: str, alt: str|None, local_path: str|None}]
    images = scrapy.Field()

    # 내부 링크
    out_links = scrapy.Field()

    depth = scrapy.Field()
    auth_profile = scrapy.Field()

    # 내부용
    page_key = scrapy.Field()  # hash key
