from pydantic import BaseModel, Field
from typing import Optional


class SupplierInfo(BaseModel):
    service_provider_name: Optional[str] = None
    client_name: Optional[str] = None
    agreement_date: Optional[str] = None
    contract_duration: Optional[str] = None
    model_config = {"extra": "forbid"}

class UptimeCommitments(BaseModel):
    guaranteed_uptime_percent: Optional[float] = None
    measurement_period: Optional[str] = None
    excluded_downtime: Optional[str] = None
    model_config = {"extra": "forbid"}

class PenaltyClause(BaseModel):
    clause_id: Optional[str] = None
    trigger_condition: Optional[str] = None
    penalty_type: Optional[str] = None
    penalty_amount: Optional[str] = None
    model_config = {"extra": "forbid"}

class TerminationClauses(BaseModel):
    termination_for_cause: Optional[str] = None
    notice_period_days: Optional[float] = None
    termination_for_convenience: Optional[str] = None
    model_config = {"extra": "forbid"}

class ForceMajeure(BaseModel):
    clause_id: Optional[str] = None
    covered_events: Optional[str] = None
    notification_requirement: Optional[str] = None
    model_config = {"extra": "forbid"}

class DisputeResolution(BaseModel):
    governing_law: Optional[str] = None
    resolution_mechanism: Optional[str] = None
    model_config = {"extra": "forbid"}

class SLADocument(BaseModel):
    supplier_info: Optional[SupplierInfo] = None
    uptime_commitments: Optional[UptimeCommitments] = None
    penalty_clauses: Optional[list[PenaltyClause]] = None
    termination_clauses: Optional[TerminationClauses] = None
    force_majeure: Optional[ForceMajeure] = None
    dispute_resolution: Optional[DisputeResolution] = None
    model_config = {"extra": "forbid"}