from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.catalog_use_cases import create_category, list_categories
from app.infrastructure.database import get_db

router = APIRouter()


class CategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]


@router.get("/", response_model=List[CategoryResponse])
def list_all(db: Session = Depends(get_db)):
    return [CategoryResponse(id=c.id, name=c.name, description=c.description)
            for c in list_categories(db)]


@router.post("/", response_model=CategoryResponse, status_code=201)
def create(req: CategoryRequest, db: Session = Depends(get_db)):
    c = create_category(db, req.name, req.description)
    return CategoryResponse(id=c.id, name=c.name, description=c.description)
