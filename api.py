from fastapi import FastAPI
from contextlib import asynccontextmanager
import pandas as pd
from constants import Data_Path 
import json
from fastapi.responses import JSONResponse



@asynccontextmanager
async def get_data():
    app.state.df = pd.read_csv(Data_Path / "Sales.csv", index_col=0, parse_dates=True)
    yield
    del app.state.df

app = FastAPI(get_data=get_data)

@app.get("/summary")
async def read_summary():
    data = app.state.df
    return JSONResponse(content=json.loads(data.describe().to_json()))


