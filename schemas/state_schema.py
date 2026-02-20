from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_id: Optional[int] = None


class ProductInfo(BaseModel):
    product_id: int
    name: str
    category: str
    base_price: float
    material: str
    finish_options: str
    dimensions_guide: str
    description: str


class HumanSpec(BaseModel):
    raw_answers: str
    dimensions: Optional[str] = None
    finish: Optional[str] = None
    material_preference: Optional[str] = None
    special_requests: Optional[str] = None
    quantity: int = 1


class TechnicalSpec(BaseModel):
    dimensions_mm: Optional[str] = None
    wood_species: Optional[str] = None
    finish_grade: Optional[str] = None
    joinery_method: Optional[str] = None
    weight_capacity_kg: Optional[str] = None
    hardware: Optional[str] = None
    surface_treatment: Optional[str] = None
    estimated_lead_days: Optional[int] = None
    summary: str


class PricingSummary(BaseModel):
    base_price: float
    customization_cost: float
    material_cost: float
    total_price: float
    breakdown: str


class StockStatus(BaseModel):
    available: bool
    quantity_in_stock: int
    requested_quantity: int
    sku: Optional[str] = None
    alternative_product_id: Optional[int] = None
    alternative_product_name: Optional[str] = None


class SupervisorDecision(BaseModel):
    next_agent: str
    reason: str
    suggested_product_id: Optional[int] = None
