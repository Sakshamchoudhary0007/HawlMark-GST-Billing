from abc import ABC, abstractmethod
from app.services.gst.schemas import GSTLookupResponse

class GSTProvider(ABC):
    @abstractmethod
    def lookup(self, gstin: str) -> GSTLookupResponse:
        pass
