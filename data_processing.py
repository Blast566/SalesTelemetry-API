import json
import pandas as pd
from fastapi.responses import JSONResponse

class DataExplorer:
    def __init__(self, df, limit=100):
        # Store full dataframe for analytical calculations
        self.df_full = df
        # Store a lightweight preview slice for generic data retrieval
        self._df = df.head(limit)

    @property
    def df(self):
        return self._df

    def summary(self):
        # Transpose describe metrics (.T) and move row fields into an explicit index column
        summary_df = self.df_full.describe().T.reset_index()
        
        # Clean out index row noise and drop chronological columns from analytics layout
        summary_df = summary_df.set_index('index')
        summary_df = summary_df.drop('count', axis=0)
        summary_df = summary_df.drop(['Day', 'Year'], axis=0, errors='ignore')
        summary_df = summary_df.reset_index()
        
        self._df = summary_df
        return self  # Enables method chaining

    def kpis(self, country=None):
        df = self.df_full
        
        # Apply string casefolding for user-friendly query matching
        if country:
            df = df.query("Country.str.lower() == @country.lower()")
            
        return {
            "total_revenue": str(df["Revenue"].sum()),
            "total_profit": str(df["Profit"].sum()),
            "total_cost": str(df["Cost"].sum()),
            "number_of_purchases": len(df)
        }

    def json_response(self):
        # Convert the active class dataframe target straight to a record-oriented JSON array
        json_data = self._df.to_json(orient="records")
        return JSONResponse(content=json.loads(json_data))
