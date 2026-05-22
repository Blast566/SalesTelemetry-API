from fastapi import FastAPI, APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete
from contextlib import asynccontextmanager
from typing import List, Optional
import pandas as pd
import io

from database import engine, Base, get_db
from models import SaleModel
from schemas import SaleResponse, KPIResponse, UploadResponse
from auth import verify_key


REQUIRED_COLUMNS = {
    "Date", "Country", "State", "Product_Category",
    "Order_Quantity", "Unit_Cost", "Unit_Price", "Profit", "Revenue"
}


async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_tables()
    yield


app = FastAPI(
    title="SalesTelemetry API",
    description="Asynchronous Backend Service for Relational Retail Analytics",
    version="1.0.0",
    lifespan=lifespan,
)

router = APIRouter(
    prefix="/api/sales",
    tags=["Sales Operations"],
    dependencies=[Depends(verify_key)],  # all routes require API key
)


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(..., description="CSV file with sales data"),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV is missing required columns: {sorted(missing)}",
        )

    try:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not parse 'Date' column — expected YYYY-MM-DD.",
        )

    async with db.begin():
        await db.execute(delete(SaleModel))
        for _, row in df.iterrows():
            db.add(SaleModel(
                date=row["Date"],
                country=str(row["Country"]),
                state=str(row["State"]),
                product_category=str(row["Product_Category"]),
                order_quantity=int(row["Order_Quantity"]),
                unit_cost=float(row["Unit_Cost"]),
                unit_price=float(row["Unit_Price"]),
                profit=float(row["Profit"]),
                revenue=float(row["Revenue"]),
            ))

    return {"rows_loaded": len(df), "filename": file.filename}


@router.get("/", response_model=List[SaleResponse])
async def read_sales(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country: Optional[str] = Query(None, description="Filter by country"),
    product_category: Optional[str] = Query(None, description="Filter by product category"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    query = select(SaleModel)

    if country:
        query = query.where(func.lower(SaleModel.country) == country.lower())
    if product_category:
        query = query.where(func.lower(SaleModel.product_category) == product_category.lower())
    if date_from:
        query = query.where(SaleModel.date >= date_from)
    if date_to:
        query = query.where(SaleModel.date <= date_to)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/kpis", response_model=KPIResponse)
async def read_kpis(
    country: Optional[str] = Query(None, description="Filter KPIs by country"),
    db: AsyncSession = Depends(get_db),
):
    query = select(
        func.sum(SaleModel.revenue).label("total_revenue"),
        func.sum(SaleModel.profit).label("total_profit"),
        func.sum(SaleModel.unit_cost * SaleModel.order_quantity).label("total_cost"),
        func.count(SaleModel.id).label("number_of_purchases"),
    )

    if country:
        query = query.where(func.lower(SaleModel.country) == country.lower())

    result = await db.execute(query)
    kpis = result.first()

    total_revenue = float(kpis.total_revenue or 0.0)
    total_profit = float(kpis.total_profit or 0.0)
    total_cost = float(kpis.total_cost or 0.0)
    number_of_purchases = int(kpis.number_of_purchases or 0)
    profit_margin = round((total_profit / total_revenue * 100), 2) if total_revenue else 0.0

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_cost": total_cost,
        "number_of_purchases": number_of_purchases,
        "profit_margin": profit_margin,
    }


app.include_router(router)
