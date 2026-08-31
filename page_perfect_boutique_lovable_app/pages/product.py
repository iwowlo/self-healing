import re
from typing import Optional

from web_poet import Returns, WebPage, field, handle_urls

from page_perfect_boutique_lovable_app.items import ProductItem


@handle_urls("page-perfect-boutique.lovable.app")
class ProductPage(WebPage, Returns[ProductItem]):

    @field
    def item_name(self) -> Optional[str]:
        return self.css("h1::text").get()

    @field
    def price(self) -> Optional[str]:
        return self.css("p.font-display.text-2xl.font-semibold::text").get()

    @field
    def rating(self) -> Optional[float]:
        value = self.css("span.font-semibold.text-foreground::text").get()
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @field
    def colours(self) -> Optional[list]:
        values = self.css("div.mt-2.flex.gap-2 button.rounded-full::attr(aria-label)").getall()
        return values or None

    @field
    def product_id(self) -> Optional[str]:
        text = self.css("p.label-xs.mt-3::text").get()
        if text is None:
            return None
        match = re.search(r"Product ID:\s*(\S+)", text)
        return match.group(1) if match else None

    @field
    def description(self) -> Optional[str]:
        return self.css(
            "section.max-w-3xl p.mt-4.text-sm.leading-relaxed.text-muted-foreground::text"
        ).get()

    @field
    def gender(self) -> Optional[str]:
        return self.css("p.label-xs.mt-1::text").get()

    @field
    def brand(self) -> Optional[str]:
        return self.css("meta[name=\"author\"]::attr(content)").get()

    @field
    def sizes(self) -> Optional[list]:
        values = self.css("div.flex-wrap button::text").getall()
        return values or None
