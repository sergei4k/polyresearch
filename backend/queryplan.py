import google.generativeai as genai
import json
from models.schemas import AnalysisPlan, AnalysisStep


# Define the available analysis functions that the AI can use
AVAILABLE_FUNCTIONS = """
Available analysis functions:

1. fetch_markets(filters: dict) -> DataFrame
   - Fetches market data
   - filters: {active: bool, closed: bool, limit: int, min_volume: float}

2. fetch_trades(filters: dict) -> DataFrame
   - Fetches trade history
   - filters: {market_id: str, maker: str, limit: int, after_date: str}

3. fetch_price_history(token_id: str, interval: str) -> DataFrame
   - Fetches historical prices for a market
   - interval: "1h", "1d", "1w"

4. filter_df(column: str, operator: str, value: any) -> DataFrame
   - Filters the current DataFrame
   - operator: "eq", "gt", "lt", "gte", "lte", "contains", "between"

5. group_aggregate(group_by: list[str], aggregations: dict) -> DataFrame
   - Groups and aggregates data
   - aggregations: {column: "sum" | "mean" | "count" | "min" | "max"}

6. calculate_correlation(x_col: str, y_col: str) -> float
   - Calculates Pearson correlation between two columns

7. calculate_win_rate(outcome_col: str, group_by: str | None) -> DataFrame
   - Calculates win rate, optionally grouped

8. join_data(left_key: str, right_key: str, how: str) -> DataFrame
   - Joins two DataFrames
   - how: "inner", "left", "right", "outer"

9. time_bucket(date_col: str, bucket: str) -> DataFrame
   - Buckets timestamps
   - bucket: "hour", "day", "week", "month"

10. visualize(chart_type: str, x: str, y: str, options: dict) -> ChartSpec
    - Creates a visualization
    - chart_type: "scatter", "line", "bar", "histogram", "heatmap"
    - options: {title: str, color_by: str, regression: bool, bins: int}
"""


SYSTEM_PROMPT = f"""You are an expert quantitative analyst helping users investigate hypotheses about Polymarket prediction markets.

Your job is to convert natural language hypotheses into structured analysis plans using the available functions.

{AVAILABLE_FUNCTIONS}

When given a hypothesis, output a JSON analysis plan with this structure:
{{
    "hypothesis": "the original hypothesis",
    "steps": [
        {{
            "function": "function_name",
            "params": {{}},
            "description": "what this step does"
        }}
    ],
    "required_data": ["markets", "trades", etc.]
}}

Rules:
1. Break complex hypotheses into logical sequential steps
2. Always end with a visualize step when the hypothesis implies a relationship to show
3. Use appropriate filters to focus on relevant data
4. Include correlation/statistical analysis when comparing relationships
5. Be conservative - only use functions that exist in the list above

Respond ONLY with valid JSON, no other text.
"""


class QueryPlanner:
    """Converts natural language hypotheses into analysis plans using Gemini."""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    async def create_plan(self, hypothesis: str) -> AnalysisPlan:
        """Convert a hypothesis into an executable analysis plan."""

        # Combine system prompt and user message for Gemini
        prompt = f"{SYSTEM_PROMPT}\n\nCreate an analysis plan for this hypothesis:\n\n{hypothesis}"

        response = await self.model.generate_content_async(prompt)

        # Extract the JSON from the response
        response_text = response.text
        
        # Parse the JSON
        try:
            plan_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON if there's extra text
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                raise ValueError(f"Could not parse plan from response: {response_text}")
        
        # Convert to our schema
        steps = [
            AnalysisStep(
                function=step["function"],
                params=step.get("params", {}),
                description=step.get("description", "")
            )
            for step in plan_data.get("steps", [])
        ]
        
        return AnalysisPlan(
            hypothesis=hypothesis,
            steps=steps,
            required_data=plan_data.get("required_data", [])
        )