import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Query
from constants import DATA_PATH
from data_processing import DataExplorer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute heavy CSV read operations exactly once at server boot
    app.state.df = pd.read_csv(DATA_PATH / "Sales.csv", index_col=0, parse_dates=True)
    yield
    # Safely clear system memory when stopping the backend process
    del app.state.df

# Instantiate core application wrapper
app = FastAPI(lifespan=lifespan)

# Define clean router scoping for your data endpoints
router = APIRouter(prefix="/api/sales")

@router.get("/")
async def read_sales(limit: int = Query(100, ge=1, le=150000)):
    # Retrieve data stream according to limit parameters
    data = DataExplorer(app.state.df, limit=limit)
    return data.json_response()

@router.get("/summary")
async def read_summary():
    # Calculate statistical frame blocks via chained method invocation
    data = DataExplorer(app.state.df)
    return data.summary().json_response()

@router.get("/kpis")
async def read_kpis(country: str = Query(None)):
    # Deliver structured dictionary telemetry data directly
    data = DataExplorer(app.state.df)
    return data.kpis(country=country)

# Mount router definitions onto main app engine
app.include_router(router)
