import scrapy
from scrapy_poet import DummyResponse

from page_perfect_boutique_lovable_app.pages.navigation import NavigationPage
from page_perfect_boutique_lovable_app.pages.product import ProductPage


class PagePerfectBoutiqueLovableApp(scrapy.Spider):
    name = "boutique"
    start_urls = ["https://page-perfect-boutique.lovable.app/"]

    async def parse(self, response: DummyResponse, nav: NavigationPage):
        nav_item = await nav.to_item()

        for link in nav_item.items or []:
            yield scrapy.Request(link["url"], callback=self.parse_item)

        if nav_item.next_page:
            yield scrapy.Request(nav_item.next_page, callback=self.parse)

        for link in nav_item.subcategories or []:
            yield scrapy.Request(link["url"], callback=self.parse)

        # This demo site renders a single product on the start page with no
        # navigable product links — extract it directly from the start URL.
        if not nav_item.items and not nav_item.subcategories:
            yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)

    async def parse_item(self, response: DummyResponse, page: ProductPage):
        yield await page.to_item()
