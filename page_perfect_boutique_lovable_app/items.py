from dataclasses import dataclass


@dataclass
class NavigationLink:
    url: str | None = None
    text: str | None = None


@dataclass
class NavigationItem:
    items: list | None = None
    next_page: str | None = None
    subcategories: list | None = None


@dataclass
class ProductItem:
    item_name: str | None = None
    price: str | None = None
    rating: float | None = None
    colours: list | None = None
    product_id: str | None = None
    description: str | None = None
    gender: str | None = None
    brand: str | None = None
    sizes: list | None = None
