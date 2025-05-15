from rest_framework.exceptions import ValidationError

class TokenExpiredOrInvalid(ValidationError):
    default_detail = "Tasdiqlash tokeni noto‘g‘ri yoki muddati o‘tgan."
    default_code = "invalid_verification_token"