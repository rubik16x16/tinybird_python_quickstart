from tinybird_sdk import define_datasource, define_endpoint, engine, node, p, t

# --- Datasources ---

ecommerce_events = define_datasource(
    "ecommerce_events",
    {
        "description": "E-commerce events data",
        "schema": {
            "event_id": t.int32(),
            "user_id": t.int32(),
            "event_type": t.string(),
            "product_id": t.int32(),
            "timestamp": t.date_time(),
            "price": t.float32(),
            "country": t.string().low_cardinality().nullable(),
        },
        "engine": engine.merge_tree(
            {
                "sorting_key": ["event_id", "user_id"],
            }
        ),
    },
)

# --- Endpoints ---

ecommerce_summary = define_endpoint(
    "ecommerce_summary",
    {
        "description": "E-commerce summary metrics",
        "parameters": {
            "start_date": t.date_time(),
            "end_date": t.date_time(),
            "country": t.string().nullable(),
        },
        "nodes": [
            node(
                {
                    "name": "summary_metrics",
                    "sql": """
                        SELECT 
                            sumIf(price, event_type = 'purchase') as total_revenue,
                            countIf(event_type = 'purchase') as purchases,
                            countIf(event_type = 'product_view') as product_views,
                            countDistinct(user_id) as unique_users
                        FROM ecommerce_events
                        WHERE timestamp >= {{ DateTime(start_date) }}
                          AND timestamp <= {{ DateTime(end_date) }}
                          AND ({{ country }} IS NULL OR country = {{ country }})
                    """,
                }
            ),
        ],
        "output": {
            "total_revenue": t.float32(),
            "purchases": t.uint64(),
            "product_views": t.uint64(),
            "unique_users": t.uint64(),
        },
    },
)

ecommerce_top_products = define_endpoint(
    "ecommerce_top_products",
    {
        "description": "Top 5 products by purchase count",
        "parameters": {
            "start_date": t.date_time(),
            "end_date": t.date_time(),
            "country": t.string().nullable(),
        },
        "nodes": [
            node(
                {
                    "name": "top_products_list",
                    "sql": """
                        SELECT 
                            product_id,
                            count(*) as purchase_count,
                            sum(price) as revenue
                        FROM ecommerce_events
                        WHERE event_type = 'purchase'
                          AND timestamp >= {{ DateTime(start_date) }}
                          AND timestamp <= {{ DateTime(end_date) }}
                          AND ({{ country }} IS NULL OR country = {{ country }})
                        GROUP BY product_id
                        ORDER BY purchase_count DESC
                        LIMIT 5
                    """,
                }
            ),
        ],
        "output": {
            "product_id": t.int32(),
            "purchase_count": t.uint64(),
            "revenue": t.float32(),
        },
    },
)
