from app.config.settings import get_settings
from app.services.gst.base import GSTProvider
from app.services.gst.mock_provider import MockGSTProvider
from app.services.gst.exceptions import GSTProviderError

def get_gst_provider() -> GSTProvider:
    settings = get_settings()
    if settings.GST_PROVIDER_TYPE == "mock":
        return MockGSTProvider()
    else:
        raise GSTProviderError(f"Unsupported GST provider type: {settings.GST_PROVIDER_TYPE}")
