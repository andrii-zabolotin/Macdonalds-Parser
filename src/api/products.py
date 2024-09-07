import json
import os
from typing import List

from fastapi import APIRouter

from src.schemas.products import ProductDetails, ProductCatalog

router = APIRouter(
    tags=['products']
)

file_path = os.path.join(os.path.dirname(__file__), '..', 'parser', 'data.json')


@router.get('/all_products', response_model=List[ProductCatalog])
def product_list():
    with open(file_path, 'r') as f:
        products = json.load(f)

    return [products]


@router.get('/products/{product_name}', response_model=ProductDetails)
def get_product(
        product_name: str,
):
    with open(file_path, 'r') as f:
        products = json.load(f)

    return products[product_name]


@router.get('/products/{product_name}/{product_field}')
def get_product_field(
    product_name: str,
    product_field: str,
):
    with open(file_path, 'r') as f:
        products = json.load(f)

    return products[product_name][product_field]
