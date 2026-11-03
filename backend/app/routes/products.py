from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.services import product_service
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/products", response_model=ProductListResponse)
def get_products(
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.list_products(
        db, current_user.business_id, q, page, limit, include_archived
    )

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.create_product(db, current_user.business_id, product)

@router.get("/products/{id}", response_model=ProductResponse)
def get_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.get_product(db, current_user.business_id, id)

@router.put("/products/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.update_product(db, current_user.business_id, id, product)

@router.patch("/products/{id}/archive", response_model=ProductResponse)
def archive_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return product_service.archive_product(db, current_user.business_id, id)
