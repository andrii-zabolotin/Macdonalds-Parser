from typing import Dict

from pydantic import BaseModel


class ProductDetails(BaseModel):
    description: str
    calories: str
    fats: str
    carbs: str
    proteins: str
    unsaturated_fats: str
    sugar: str
    salt: str
    portion: str


ProductCatalog = Dict[str, ProductDetails]
