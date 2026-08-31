from functools import cached_property

from page_perfect_boutique_lovable_app.items import NavigationItem, NavigationLink
from web_poet import Returns, WebPage, field, handle_urls


@handle_urls("page-perfect-boutique.lovable.app")
class NavigationPage(WebPage, Returns[NavigationItem]):

    @cached_property
    def _base_url(self) -> str:
        return str(self.response.url)

    @field
    def items(self) -> list[NavigationLink] | None:
        """Links to detail/item pages — in-body links that are not header nav or root."""
        result = []
        seen: set[str] = set()
        for a in self.css("main a[href], article a[href], section a[href]"):
            href = a.css("::attr(href)").get() or ""
            if not href or href == "/":
                continue
            abs_url = self.urljoin(href)
            if abs_url in seen or not abs_url.startswith("http"):
                continue
            seen.add(abs_url)
            text = " ".join(a.css("::text").getall()).strip() or None
            result.append(NavigationLink(url=abs_url, text=text))
        return result or None

    @field
    def next_page(self) -> str | None:
        """URL of the next pagination page, or None."""
        href = (
            self.css("a[rel='next']::attr(href)").get()
            or self.css("a.next::attr(href)").get()
            or self.css("[aria-label='Next page']::attr(href)").get()
            or self.css("[aria-label='Next']::attr(href)").get()
        )
        return self.urljoin(href) if href else None

    @field
    def subcategories(self) -> list[NavigationLink] | None:
        """Links to subcategory/sublisting pages from the header navigation."""
        result = []
        seen: set[str] = set()
        for a in self.css("header nav a[href]"):
            href = a.css("::attr(href)").get() or ""
            if not href or href == "/":
                continue
            abs_url = self.urljoin(href)
            if abs_url in seen:
                continue
            seen.add(abs_url)
            text = a.css("::text").get("").strip() or None
            result.append(NavigationLink(url=abs_url, text=text))
        return result or None
