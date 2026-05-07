import os

from tinybird_sdk import Tinybird

from src.tinybird.tinybird_resources import (
    ecommerce_events,
    ecommerce_summary,
    ecommerce_top_products,
)

tinybird = Tinybird(
    {
        "datasources": {"ecommerce_events": ecommerce_events},
        "pipes": {
            "ecommerce_summary": ecommerce_summary,
            "ecommerce_top_products": ecommerce_top_products,
        },
        "base_url": os.getenv("TINYBIRD_API_URL", "https://api.tinybird.co"),
        "token": os.getenv("TINYBIRD_TOKEN"),
    }
)
