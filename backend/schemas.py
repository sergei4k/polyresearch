from pydantic import BaseModel, Field
from typing import Any
from enum import Enum


class AnalysisStep(BaseModel):
    """A single step in the analysis plan."""
    function: str = Field(..., description="Name of the function to execute")
    params: dict[str, Any] = Field(default_factory=dict, description="Parameters for the function")
    description: str = Field(..., description="Human-readable description of this step")


class AnalysisPlan(BaseModel):
    """The full plan generated from a hypothesis."""
    hypothesis: str = Field(..., description="Original user hypothesis")
    steps: list[AnalysisStep] = Field(..., description="Ordered list of analysis steps")
    required_data: list[str] = Field(default_factory=list, description="Data sources needed")


class ChartType(str, Enum):
    """Supported chart types for visualization."""
    SCATTER = "scatter"
    LINE = "line"
    BAR = "bar"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"


class ChartSpec(BaseModel):
    """Specification for rendering a chart on the frontend."""
    chart_type: ChartType
    title: str
    x_label: str
    y_label: str
    data: list[dict[str, Any]]
    options: dict[str, Any] = Field(default_factory=dict)


class HypothesisRequest(BaseModel):
    """Request body for analyzing a hypothesis."""
    hypothesis: str = Field(..., min_length=10, max_length=1000)


class AnalysisResult(BaseModel):
    """Response containing analysis results."""
    success: bool
    plan: AnalysisPlan | None = None
    charts: list[ChartSpec] = Field(default_factory=list)
    summary: str = ""
    raw_data: dict[str, Any] | None = None
    error: str | None = None