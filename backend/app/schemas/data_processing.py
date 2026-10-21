"""
Stanleaf API — Data Processing Schemas
======================================
Pydantic schemas for the data engineering pipeline API endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from data_engine.pipeline import PipelineOutput, PIPELINE_VERSION


class DataProcessingResponse(PipelineOutput):
    """
    Response schema for POST /api/v1/businesses/{business_id}/data-processing.
    Inherits all fields from data_engine.PipelineOutput.
    """
    pass
