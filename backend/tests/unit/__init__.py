"""Unit tests for input validation utilities."""

from app.utils.validators import (
    validate_gstin,
    validate_pan,
    validate_mobile,
    validate_pincode,
    validate_email,
    validate_state_code,
    INDIAN_STATES,
)


class TestValidateGSTIN:
    """Test GSTIN format validation."""

    def test_valid_gstin(self):
        assert validate_gstin("27AAPFU0939F1ZV") is True

    def test_valid_gstin_different_state(self):
        assert validate_gstin("07AAACH7409R1ZZ") is True

    def test_invalid_gstin_too_short(self):
        assert validate_gstin("27AAPFU0939F1Z") is False

    def test_invalid_gstin_too_long(self):
        assert validate_gstin("27AAPFU0939F1ZVX") is False

    def test_invalid_gstin_lowercase(self):
        assert validate_gstin("27aapfu0939f1zv") is False

    def test_invalid_gstin_empty(self):
        assert validate_gstin("") is False

    def test_invalid_gstin_missing_z(self):
        assert validate_gstin("27AAPFU0939F1AV") is False


class TestValidatePAN:
    """Test PAN format validation."""

    def test_valid_pan(self):
        assert validate_pan("AAPFU0939F") is True

    def test_valid_pan_different(self):
        assert validate_pan("BZTPS1234A") is True

    def test_invalid_pan_lowercase(self):
        assert validate_pan("aapfu0939f") is False

    def test_invalid_pan_too_short(self):
        assert validate_pan("AAPFU093") is False

    def test_invalid_pan_wrong_format(self):
        assert validate_pan("12345ABCDE") is False


class TestValidateMobile:
    """Test Indian mobile number validation."""

    def test_valid_mobile_starts_with_9(self):
        assert validate_mobile("9876543210") is True

    def test_valid_mobile_starts_with_6(self):
        assert validate_mobile("6123456789") is True

    def test_valid_mobile_starts_with_7(self):
        assert validate_mobile("7890123456") is True

    def test_valid_mobile_starts_with_8(self):
        assert validate_mobile("8765432109") is True

    def test_invalid_mobile_starts_with_5(self):
        assert validate_mobile("5876543210") is False

    def test_invalid_mobile_too_short(self):
        assert validate_mobile("987654321") is False

    def test_invalid_mobile_too_long(self):
        assert validate_mobile("98765432101") is False

    def test_invalid_mobile_with_country_code(self):
        assert validate_mobile("+919876543210") is False


class TestValidatePincode:
    """Test Indian pincode validation."""

    def test_valid_pincode(self):
        assert validate_pincode("400001") is True

    def test_valid_pincode_different(self):
        assert validate_pincode("110001") is True

    def test_invalid_pincode_starts_with_zero(self):
        assert validate_pincode("000001") is False

    def test_invalid_pincode_too_short(self):
        assert validate_pincode("40001") is False

    def test_invalid_pincode_too_long(self):
        assert validate_pincode("4000011") is False


class TestValidateEmail:
    """Test email format validation."""

    def test_valid_email(self):
        assert validate_email("user@example.com") is True

    def test_valid_email_with_dots(self):
        assert validate_email("first.last@example.com") is True

    def test_valid_email_with_plus(self):
        assert validate_email("user+tag@example.com") is True

    def test_invalid_email_no_at(self):
        assert validate_email("userexample.com") is False

    def test_invalid_email_no_domain(self):
        assert validate_email("user@") is False

    def test_invalid_email_empty(self):
        assert validate_email("") is False


class TestValidateStateCode:
    """Test Indian state code validation."""

    def test_valid_state_code_maharashtra(self):
        assert validate_state_code("27") is True

    def test_valid_state_code_delhi(self):
        assert validate_state_code("07") is True

    def test_valid_state_code_karnataka(self):
        assert validate_state_code("29") is True

    def test_invalid_state_code(self):
        assert validate_state_code("99") is False

    def test_invalid_state_code_empty(self):
        assert validate_state_code("") is False

    def test_indian_states_not_empty(self):
        """Ensure the states dictionary has reasonable coverage."""
        assert len(INDIAN_STATES) >= 28
