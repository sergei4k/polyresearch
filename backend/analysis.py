from fastapi import APIRouter, HTTPException, Depends
from models.schemas import HypothesisRequest, AnalysisResult
from services.query_planner import QueryPlanner
from services.executor import PlanExecutor
from services.polymarket_client import PolymarketClient
from core.config import get_settings, Settings

router = APIRouter(prefix="/api/v1", tags=["analysis"])


def get_polymarket_client(settings: Settings = Depends(get_settings)) -> PolymarketClient:
    """Dependency for Polymarket client."""
    return PolymarketClient(
        clob_base_url=settings.polymarket_api_base_url,
        gamma_base_url=settings.polymarket_gamma_api_url
    )


def get_query_planner(settings: Settings = Depends(get_settings)) -> QueryPlanner:
    """Dependency for query planner."""
    return QueryPlanner(api_key=settings.gemini_api_key)


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_hypothesis(
    request: HypothesisRequest,
    planner: QueryPlanner = Depends(get_query_planner),
    polymarket_client: PolymarketClient = Depends(get_polymarket_client)
):
    """
    Analyze a hypothesis about Polymarket data.
    
    Takes a natural language hypothesis and returns analysis results
    including charts and statistical findings.
    """
    try:
        # Step 1: Convert hypothesis to analysis plan
        plan = await planner.create_plan(request.hypothesis)
        
        # Step 2: Execute the plan
        executor = PlanExecutor(polymarket_client)
        result = await executor.execute(plan)
        
        # Cleanup
        await polymarket_client.close()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}