# SalesTelemetry

A lightweight sales analytics platform. Upload a CSV of your sales data and instantly explore KPIs and records through an interactive dashboard — no SQL or Python knowledge required.

Think of it as a minimal Tableau: bring your data, get filterable metrics and a clean UI backed by a real database and authenticated API.

---

## What It Does

1. **Upload your CSV** through the dashboard
2. Data is stored in a PostgreSQL database
3. Explore:
   - Total revenue, profit, cost, purchase count, and profit margin
   - Filter KPIs by country
   - Browse raw records filtered by country, product category, and date range

---

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI + async SQLAlchemy |
| Data processing | Pandas |
| Database | PostgreSQL |
| Frontend | Streamlit |
| Auth | API Key |
| Containerization | Docker |
| Hosting | Render (API) + Streamlit Cloud (dashboard) |

---

## Endpoints

All endpoints require an `X-API-Key` header.

### `POST /api/sales/upload`
Upload a CSV file. Validates required columns, parses dates with Pandas, and replaces all existing data in the database.

**Required columns:**
`Date`, `Country`, `State`, `Product_Category`, `Order_Quantity`, `Unit_Cost`, `Unit_Price`, `Profit`, `Revenue`

**Response:**
```json
{ "rows_loaded": 4823, "filename": "Sales.csv" }
```

### `GET /api/sales/`
Returns paginated sales records. Supports filtering by `country`, `product_category`, `date_from`, `date_to`. Max 1,000 records per request.

### `GET /api/sales/kpis`
Returns aggregated KPIs across the full dataset or scoped to a country.

**Response:**
```json
{
  "total_revenue": 15200000.0,
  "total_profit": 4800000.0,
  "total_cost": 10400000.0,
  "number_of_purchases": 4823,
  "profit_margin": 31.58
}
```

---

## Running Locally

Requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).

```bash
git clone https://github.com/Blast566/SalesTelemetry-API
cd SalesTelemetry-API

export API_KEY=your-secret-key

docker compose up
```

| Service | URL |
|---|---|
| Dashboard | http://localhost:8501 |
| API docs | http://localhost:8000/docs |

---

## CSV Format

Your CSV must include these columns (additional columns are ignored):

| Column | Type | Example |
|---|---|---|
| Date | YYYY-MM-DD | 2024-01-15 |
| Country | string | United States |
| State | string | California |
| Product_Category | string | Electronics |
| Order_Quantity | integer | 3 |
| Unit_Cost | float | 49.99 |
| Unit_Price | float | 79.99 |
| Profit | float | 90.00 |
| Revenue | float | 239.97 |

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `DATABASE_URL` | API | PostgreSQL connection string |
| `API_KEY` | API + Frontend | Shared secret for authentication |
| `API_BASE` | Frontend | Base URL of the API |
| `PORT` | Both | Port to run on (injected by host) |

---

## Note on Free Hosting

This project is hosted on Render's free tier. The API may take **20-30 seconds** to respond on the first request after a period of inactivity — this is expected. Subsequent requests will be fast.
