import os
from pathlib import Path

from dotenv import load_dotenv
from tinybird_sdk import Tinybird

from src.tinybird.tinybird_resources import (
    ecommerce_events,
    ecommerce_summary,
    ecommerce_top_products,
)

project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env.local"

if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"⚠️  Warning: {env_file} not found, using system environment variables")

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
