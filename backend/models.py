from pydantic import BaseModel
from typing import Optional, List

class VariantModel(BaseModel):
    variant_name: str
    html_content: str
    confidence_score: int

class JobStatusResponse(BaseModel):
    job_id: str
    status: str # "pending", "processing", "completed", "failed"
    current_step: str
    audit_passed: Optional[bool] = None
    variants: Optional[List[VariantModel]] = None