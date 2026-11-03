import math
from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductListResponse
from app.utils.exceptions import NotFoundError

def get_product(db: Session, business_id: int, product_id: int) -> Product:
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.business_id == business_id
    ).first()
    if not product:
        raise NotFoundError("Product not found")
    return product

def create_product(db: Session, business_id: int, product_data: ProductCreate) -> Product:
    product = Product(**product_data.model_dump(), business_id=business_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, business_id: int, product_id: int, product_data: ProductUpdate) -> Product:
    product = get_product(db, business_id, product_id)
    
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
        
    db.commit()
    db.refresh(product)
    return product

def archive_product(db: Session, business_id: int, product_id: int) -> Product:
    product = get_product(db, business_id, product_id)
    product.is_archived = not product.is_archived
    db.commit()
    db.refresh(product)
    return product

def list_products(
    db: Session, 
    business_id: int, 
    q: Optional[str] = None, 
    page: int = 1, 
    limit: int = 20, 
    include_archived: bool = False
) -> ProductListResponse:
    query = db.query(Product).filter(Product.business_id == business_id)
    
    if not include_archived:
        query = query.filter(Product.is_archived == False)
        
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term),
                Product.hsn_sac.ilike(search_term),
                Product.category.ilike(search_term)
            )
        )
        
    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(Product.name.asc()).offset(offset).limit(limit).all()
    pages = math.ceil(total / limit) if limit > 0 else 0
    
    return ProductListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )
