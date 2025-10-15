# FASTAPI APPLICATION — Developer Documentation

## Overview
This application is a FastAPI-based web service for displaying and validating “Next Best Action (NBA)” event recommendations.

It combines:
- JSON API layer
- HTML-rendered pages (using Jinja2 templates)
- Cloud Object Storage (COS) integration for data retrieval

The architecture is modular, clean, and production-ready — designed for clear separation between routes, models, configuration, and infrastructure.


```
├── app.py                           → Entry point that starts the FastAPI server
├── app/
│   ├── main.py                      → Initializes the FastAPI app, static files, and routes
│   ├── models.py                    → Pydantic models for validating data structures
│   ├── routes/
│   │   ├── api_routes.py            → Machine-facing API routes (JSON)
│   │   └── html_routes.py           → Browser-facing routes (Jinja2 templates)
│   ├── templates/                   → HTML templates rendered by FastAPI
│   ├── static/                      → Static assets (CSS, JS, images)
│   ├── utils/                       → Helper functions (pagination, decorators, formatting)
│   ├── cos/
│   │   └── connector.py             → COS connector class for IBM Cloud Object Storage
│   └── config/
│       └── logger_config.py         → Centralized logging configuration

```

---

## 1. `app.py` — Application Starter

**Purpose:**  
Entry point for the entire FastAPI application. Loads environment variables, sets up logging, and launches the Uvicorn server.

**Main functions:**
- Loads environment configuration dynamically based on `ENV` (e.g., `.env.dev`, `.env.prod`)
- Initializes a consistent logger using `setup_logger()`
- Runs the FastAPI app using Uvicorn with appropriate host, port, and reload options

**Behavior:**
- `ENV=dev` → Development mode with verbose logging
- `ENV=prod` → Production-safe defaults

**Example:**

```
ENV=dev python app.py
ENV=prod python app.py
```



---

## 2. `main.py` — FastAPI Core Setup

**Purpose:**  
Defines and initializes the main FastAPI application instance.  
Acts as the central hub that connects routes, templates, and static assets.

**Key elements:**
- Creates a FastAPI instance with a descriptive title
- Mounts `/static` to serve CSS, JS, and image files
- Includes both `html_routes` and `api_routes` routers

**Structure:**

```
app = FastAPI(
title="Marketing Advisor – Post event Next Best Action (NBA) Recommendations Report"
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(html_routes.router)
app.include_router(api_routes.router)
```


This design keeps `main.py` lightweight and focused on application assembly.

---

## 3. `api_routes.py` — API Endpoints

**Purpose:**  
Provides machine-facing endpoints for programmatic access.

**Endpoints:**
- `/ping` → Health check (`{ "status": "ok" }`)
- `/fetch-data` → Fetches JSON from COS, validates with `EventsPayload`, stores cache locally  
  Accepts query parameter `?refresh=true` to force cache refresh

**Flow:**
1. Initialize `CloudStorageConnector`
2. Retrieve file keys from COS bucket
3. Download `RecoNBA.json` and validate schema
4. Update local cache under `app/data/`
5. Return JSON report of valid/invalid/error files

**Error Handling:**
- 404 → No files found
- 422 → Validation fails
- 500 → Unexpected errors

```
Example response:

{
"results": [
    {"file": "RecoNBA.json", "status": "ok"}
    ]
}
```

---

## 4. `html_routes.py` — HTML Pages and Views

**Purpose:**  
Handles browser-facing routes. Renders Jinja2 templates into HTML for human users.

**Key Routes:**
- `/` → Home page (`index.html`)
- `/events` → Lists available events
- `/events/{slug}/nba` → Event details and recommendations
- `/events/{slug}/search` → Search within event

**Supporting Features:**
- Uses `load_events()` to read & validate local JSON
- Utilities: `bulletify`, `paginate`, `mark_coverage_headers`
- Maps internal coverage codes to user-friendly names
- Paginates/filters before rendering templates (`events.html`, `nba.html`, `search.html`)

---

## 5. `models.py` — Pydantic Models

**Purpose:**  
Defines expected structure of event data (`EventsPayload` and nested models).

**Advantages:**
- Prevents invalid data from entering system
- Integrates with FastAPI OpenAPI docs
- Produces detailed schema mismatch errors

---

## 6. `cos/connector.py` — COS Connector

**Purpose:**  
Interface for IBM Cloud Object Storage (COS) using `ibm_boto3`.

**Responsibilities:**
1. Authenticate with COS (`COS_API_KEY_ID`, `COS_INSTANCE_CRN`, `COS_ENDPOINT`)
2. Retrieve object listings
3. Download and parse JSON files
4. Cache locally for performance
5. Handle API errors gracefully

**Core Methods:**
- `initialize_connection()` → Creates S3-compatible COS client
- `get_item(bucket, item)` → Fetch file and return contents
- `fetch_data(json_cache, bucket, key, update=False)` → Load from cache or fetch fresh
- `get_bucket_contents(bucket)` → List files in bucket

---

## 7. `config/logger_config.py` — Logging Configuration

**Purpose:**  
Centralizes log formatting, display, and writing.

**Features:**
- Info/debug logging based on environment
- Simple interface: `setup_logger(env_mode)`

---

## Final Notes
- Environment-based configuration via `ENV` variable
- Pydantic validation ensures data consistency
- COS integration safely encapsulated in connector
- Jinja2 templates keep front-end maintainable
- Logging ensures traceability

---

## 8. Summary of Responsibilities

- **`app.py`** → Loads config, sets up logging, starts server
- **`main.py`** → Initializes app, mounts static, includes routes
- **`api_routes.py`** → JSON API endpoints
- **`html_routes.py`** → HTML views
- **`models.py`** → Data validation
- **`cos/connector.py`** → COS integration
- **`utils/`** → Helper utilities
- **`config/logger_config.py`** → Logging setup




