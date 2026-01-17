import pandas as pd
from typing import Any
from schemas import AnalysisPlan, AnalysisResult, ChartSpec, ChartType
from polymarketapi import PolymarketClient


class PlanExecutor:
    """Executes analysis plans safely using only allowed functions."""
    
    def __init__(self, polymarket_client: PolymarketClient):
        self.client = polymarket_client
        self._dataframes: dict[str, pd.DataFrame] = {}
        self._current_df: pd.DataFrame | None = None
    
    async def execute(self, plan: AnalysisPlan) -> AnalysisResult:
        """Execute an analysis plan and return results."""
        
        charts: list[ChartSpec] = []
        
        try:
            for step in plan.steps:
                result = await self._execute_step(step.function, step.params)
                
                # If the step produced a chart, collect it
                if isinstance(result, ChartSpec):
                    charts.append(result)
                elif isinstance(result, pd.DataFrame):
                    self._current_df = result
            
            # Generate summary
            summary = self._generate_summary(plan, charts)
            
            return AnalysisResult(
                success=True,
                plan=plan,
                charts=charts,
                summary=summary,
                raw_data=self._current_df.to_dict() if self._current_df is not None else None
            )
            
        except Exception as e:
            return AnalysisResult(
                success=False,
                plan=plan,
                error=str(e)
            )
    
    async def _execute_step(self, function: str, params: dict[str, Any]) -> Any:
        """Execute a single analysis step."""
        
        # Map function names to handlers
        handlers = {
            "fetch_markets": self._fetch_markets,
            "fetch_trades": self._fetch_trades,
            "fetch_price_history": self._fetch_price_history,
            "filter_df": self._filter_df,
            "group_aggregate": self._group_aggregate,
            "calculate_correlation": self._calculate_correlation,
            "calculate_win_rate": self._calculate_win_rate,
            "join_data": self._join_data,
            "time_bucket": self._time_bucket,
            "visualize": self._visualize,
        }
        
        handler = handlers.get(function)
        if not handler:
            raise ValueError(f"Unknown function: {function}")
        
        return await handler(params)
    
    # =========================================================================
    # Function Implementations (stubs - expand these)
    # =========================================================================
    
    async def _fetch_markets(self, params: dict) -> pd.DataFrame:
        """Fetch markets and convert to DataFrame."""
        markets = await self.client.get_gamma_markets(
            limit=params.get("limit", 100),
            active=params.get("active", True),
            closed=params.get("closed", False)
        )
        df = pd.DataFrame(markets)
        self._dataframes["markets"] = df
        return df
    
    async def _fetch_trades(self, params: dict) -> pd.DataFrame:
        """Fetch trades and convert to DataFrame."""
        trades = await self.client.get_trades(
            market_id=params.get("market_id"),
            maker=params.get("maker"),
            limit=params.get("limit", 100)
        )
        df = pd.DataFrame(trades)
        self._dataframes["trades"] = df
        return df
    
    async def _fetch_price_history(self, params: dict) -> pd.DataFrame:
        """Fetch price history for a token."""
        history = await self.client.get_prices_history(
            token_id=params["token_id"],
            interval=params.get("interval", "1d")
        )
        df = pd.DataFrame(history)
        self._dataframes["price_history"] = df
        return df
    
    async def _filter_df(self, params: dict) -> pd.DataFrame:
        """Filter the current DataFrame."""
        if self._current_df is None:
            raise ValueError("No DataFrame to filter")
        
        col = params["column"]
        op = params["operator"]
        val = params["value"]
        
        ops = {
            "eq": lambda df: df[col] == val,
            "gt": lambda df: df[col] > val,
            "lt": lambda df: df[col] < val,
            "gte": lambda df: df[col] >= val,
            "lte": lambda df: df[col] <= val,
            "contains": lambda df: df[col].str.contains(val, na=False),
        }
        
        mask = ops[op](self._current_df)
        return self._current_df[mask]
    
    async def _group_aggregate(self, params: dict) -> pd.DataFrame:
        """Group and aggregate the current DataFrame."""
        if self._current_df is None:
            raise ValueError("No DataFrame to aggregate")
        
        grouped = self._current_df.groupby(params["group_by"])
        agg_result = grouped.agg(params["aggregations"])
        return agg_result.reset_index()
    
    async def _calculate_correlation(self, params: dict) -> float:
        """Calculate correlation between two columns."""
        if self._current_df is None:
            raise ValueError("No DataFrame for correlation")
        
        return self._current_df[params["x_col"]].corr(self._current_df[params["y_col"]])
    
    async def _calculate_win_rate(self, params: dict) -> pd.DataFrame:
        """Calculate win rate."""
        # TODO: Implement based on actual data structure
        raise NotImplementedError("Win rate calculation needs implementation based on data structure")
    
    async def _join_data(self, params: dict) -> pd.DataFrame:
        """Join two DataFrames."""
        # TODO: Implement joining logic
        raise NotImplementedError("Join needs implementation")
    
    async def _time_bucket(self, params: dict) -> pd.DataFrame:
        """Bucket timestamps."""
        if self._current_df is None:
            raise ValueError("No DataFrame to bucket")
        
        col = params["date_col"]
        bucket = params["bucket"]
        
        self._current_df[col] = pd.to_datetime(self._current_df[col])
        
        freq_map = {"hour": "H", "day": "D", "week": "W", "month": "M"}
        self._current_df[f"{col}_bucket"] = self._current_df[col].dt.to_period(freq_map[bucket])
        
        return self._current_df
    
    async def _visualize(self, params: dict) -> ChartSpec:
        """Create a chart specification."""
        if self._current_df is None:
            raise ValueError("No DataFrame to visualize")
        
        # Convert DataFrame to chart-friendly format
        data = self._current_df.to_dict(orient="records")
        
        return ChartSpec(
            chart_type=ChartType(params["chart_type"]),
            title=params.get("options", {}).get("title", "Analysis Result"),
            x_label=params["x"],
            y_label=params["y"],
            data=data,
            options=params.get("options", {})
        )
    
    def _generate_summary(self, plan: AnalysisPlan, charts: list[ChartSpec]) -> str:
        """Generate a text summary of the analysis."""
        return f"Analysis complete. Executed {len(plan.steps)} steps and generated {len(charts)} visualizations."