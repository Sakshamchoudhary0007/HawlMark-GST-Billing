from fastapi import APIRouter, Depends, Query
from app.auth.dependencies import get_current_user
from app.services.gst.factory import get_gst_provider
from app.services.gst.schemas import GSTLookupResponse
from app.services.gst.base import GSTProvider
from app.models.user import User

router = APIRouter(prefix="/gst", tags=["GST"])

@router.get("/lookup", response_model=GSTLookupResponse)
def lookup_gstin(
    gstin: str = Query(..., description="The GSTIN to look up"),
    current_user: User = Depends(get_current_user),
    provider: GSTProvider = Depends(get_gst_provider)
):
    """
    Look up details for a given GSTIN.
    """
    return provider.lookup(gstin)
