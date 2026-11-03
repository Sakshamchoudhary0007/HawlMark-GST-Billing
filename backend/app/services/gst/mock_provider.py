import re
from app.services.gst.base import GSTProvider
from app.services.gst.schemas import GSTLookupResponse
from app.services.gst.exceptions import GSTInvalidFormatError, GSTNotFoundError, GSTTimeoutError

INDIAN_STATES = {
    "01": "Jammu and Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman and Diu",
    "26": "Dadra and Nagar Haveli",
    "27": "Maharashtra",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman and Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh"
}

GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

def validate_gstin(gstin: str) -> bool:
    return bool(GSTIN_REGEX.match(gstin))

class MockGSTProvider(GSTProvider):
    def lookup(self, gstin: str) -> GSTLookupResponse:
        if gstin.endswith("999"):
            raise GSTNotFoundError("GSTIN not found")
            
        if gstin.endswith("888"):
            raise GSTTimeoutError("Provider timeout")

        if not validate_gstin(gstin):
            raise GSTInvalidFormatError("Invalid GSTIN format")

        state_code = gstin[:2]
        state = INDIAN_STATES.get(state_code, "Unknown State")
        pan = gstin[2:12]
        
        return GSTLookupResponse(
            gstin=gstin,
            legal_name=f"{pan} LEGAL ENTITY PVT LTD",
            trade_name=f"{pan} ENTERPRISES",
            taxpayer_type="Regular",
            status="Active",
            address_line1="123 Mock Street",
            address_line2="Mock Area",
            city="Mock City",
            state=state,
            state_code=state_code,
            pincode="110001",
            is_verified=True
        )
