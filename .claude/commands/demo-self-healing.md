# Demo: Self-Healing Spider

Runs the full self-healing demo for `page-perfect-boutique.lovable.app`:

1. Restores the **healthy** spider, deploys it, runs a job, and waits to confirm it scrapes correctly.
2. Breaks the spider (simulates a site CSS redesign), deploys it, and runs a job — which the self-healing system will then pick up and fix automatically.

**Context:**
- This command file lives inside the git repo at `page_perfect_boutique_lovable_app/`
- Open Claude Code sessions from `page_perfect_boutique_lovable_app/` to use this command
- Scrapy Cloud project ID: `876217`, spider name: `self-healing`
- Credentials are in `.env` in this directory (`SHUB_APIKEY`, `ZYTE_API_KEY`) — loaded automatically by `shub`
- All commands run from this directory (the repo root)
- Helper scripts: `/Users/Zyte/.claude/plugins/cache/zyte-ai/zyte-web-data/0.2.3/skills/scrape-scrapy-cloud/scripts/`

---

## Step 1 — Restore the healthy spider

Write the following content verbatim to `page_perfect_boutique_lovable_app/pages/product.py`:

```python
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
```

Then commit and push:

```bash
git add page_perfect_boutique_lovable_app/pages/product.py
git commit -m "demo: restore healthy spider"
git push
```

---

## Step 2 — Deploy the healthy spider and run a job

```bash
uvx shub deploy
uvx shub schedule self-healing --tag demo
```

Note the job ID printed (format: `876217/1/N`). Wait for it to finish:

```bash
uv run /Users/Zyte/.claude/plugins/cache/zyte-ai/zyte-web-data/0.2.3/skills/scrape-scrapy-cloud/scripts/wait_for_job.py 876217/1/N
```

Confirm `close_reason: finished` and `items_scraped: 1`. Download the item and verify all 9 fields are non-null:

```bash
uv run /Users/Zyte/.claude/plugins/cache/zyte-ai/zyte-web-data/0.2.3/skills/scrape-scrapy-cloud/scripts/scrapy_cloud_api.py GET "https://storage.zyte.com/items/876217/1/N" -q count=1
```

Expected fields all populated: `item_name`, `price`, `rating`, `colours`, `product_id`, `description`, `gender`, `brand`, `sizes`.

If any field is null, do NOT proceed — the healthy baseline is broken and needs investigation.

---

## Step 3 — Break the spider

Write the following content verbatim to `page_perfect_boutique_lovable_app/pages/product.py` (four selectors are intentionally wrong, simulating a site CSS redesign):

```python
import re
from typing import Optional

from web_poet import Returns, WebPage, field, handle_urls

from page_perfect_boutique_lovable_app.items import ProductItem


@handle_urls("page-perfect-boutique.lovable.app")
class ProductPage(WebPage, Returns[ProductItem]):

    @field
    def item_name(self) -> Optional[str]:
        return self.css("h2.product-title::text").get()

    @field
    def price(self) -> Optional[str]:
        return self.css("span.product-price::text").get()

    @field
    def rating(self) -> Optional[float]:
        value = self.css("div.rating-value::text").get()
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @field
    def colours(self) -> Optional[list]:
        values = self.css("div.colour-swatches button::attr(data-colour)").getall()
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
```

Commit and push:

```bash
git add page_perfect_boutique_lovable_app/pages/product.py
git commit -m "demo: break spider (simulated CSS redesign)"
git push
```

---

## Step 4 — Deploy the broken spider and trigger monitoring

```bash
uvx shub deploy
uvx shub schedule self-healing --tag demo-broken
```

Tell the audience: the broken job is now running. The `field_coverage` monitor will fire because `item_name`, `price`, `rating`, and `colours` will all be `null` (0% < 0.95 threshold). The self-healing system will detect this, open an issue, and attempt a fix automatically.

Link to the project: https://app.zyte.com/p/876217/

Do NOT wait for this job — hand over to the self-healing system from here.

---

## Done

Summarise:
- Healthy job confirmed: all 9 fields populated ✓
- Broken job running: `item_name`, `price`, `rating`, `colours` → null → triggers `field_coverage` monitor
- Self-healing system will open an issue and apply a fix automatically
