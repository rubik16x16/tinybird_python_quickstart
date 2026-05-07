# Tinybirdtest

This is an awesome tinybird test

## Features

- **Event Ingestion** - Validate and store e-commerce events (product views, add-to-cart, purchases)
- **Analytics Metrics** - Retrieve revenue, conversion rates, and top-selling products
- **Data Validation** - Automatic validation using Pydantic models with error reporting
- **Duplicate Detection** - Identifies duplicate events based on event_id
- **Country Filtering** - Filter metrics by country
- **Date Range Queries** - Flexible time period analysis

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

## Installation

### 1. Clone the repository

```bash
git clone <https://github.com/rubik16x16/tinybird_python_quickstart.git>
cd <https://github.com/rubik16x16/tinybird_python_quickstart.git>
```

### 2. Install dependencies

```bash
make install
```

## Usage

```bash
make runserver
```

## API Endpoints

### POST `/api/events`

Ingest batch e-commerce events.

**Request Body Example:**

```json
{
  "events": [
    {
      "event_id": 1,
      "user_id": 1001,
      "event_type": "product_view",
      "product_id": 5001,
      "timestamp": "2026-01-15T10:30:00",
      "price": 29.99,
      "country": "US"
    },
    {
      "event_id": 2,
      "user_id": 1001,
      "event_type": "add_to_cart",
      "product_id": 5001,
      "timestamp": "2026-01-15T10:32:00",
      "price": 29.99,
      "country": "US"
    },
    {
      "event_id": 3,
      "user_id": 1001,
      "event_type": "purchase",
      "product_id": 5001,
      "timestamp": "2026-01-15T10:35:00",
      "price": 29.99,
      "country": "US"
    }
  ]
}
```

### GET `/api/get_metrics`

Retrieve analytics metrics (supports `start_date`, `end_date`, `country` query parameters)
