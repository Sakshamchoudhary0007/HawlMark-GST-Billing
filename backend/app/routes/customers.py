from __future__ import annotations
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
)
from app.services import customer_service
from app.auth.dependencies import get_current_user
from app.utils.exceptions import BadRequestError

router = APIRouter()


@router.get("/customers", response_model=CustomerListResponse)
def list_customers(
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.business_id:
        raise BadRequestError("User does not belong to a business")
    
    items, total = customer_service.list_customers(
        db=db,
        business_id=current_user.business_id,
        q=q,
        page=page,
        limit=limit,
        include_archived=include_archived
    )
    
    pages = math.ceil(total / limit) if limit else 1
    
    return CustomerListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.post("/customers", response_model=CustomerResponse)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.business_id:
        raise BadRequestError("User does not belong to a business")
        
    return customer_service.create_customer(db, current_user.business_id, data)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.business_id:
        raise BadRequestError("User does not belong to a business")
        
    return customer_service.get_customer(db, current_user.business_id, customer_id)


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.business_id:
        raise BadRequestError("User does not belong to a business")
        
    return customer_service.update_customer(db, current_user.business_id, customer_id, data)


@router.patch("/customers/{customer_id}/archive", response_model=CustomerResponse)
def archive_customer(
    customer_id: int,
    archive: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.business_id:
        raise BadRequestError("User does not belong to a business")
        
    return customer_service.archive_customer(db, current_user.business_id, customer_id, archive)


@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.business_id:
        raise BadRequestError("User does not belong to a business")
        
    customer_service.delete_customer(db, current_user.business_id, customer_id)
    return {"message": "Customer deleted successfully"}

