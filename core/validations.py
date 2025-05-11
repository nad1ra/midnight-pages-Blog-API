from rest_framework.exceptions import ValidationError

def validate_title(value):
    if not value.strip():
        raise ValidationError("Title bo'sh bo'lishi mumkin emas.")
    if len(value) < 5:
        raise ValidationError("Title kamida 5 ta belgidan iborat bo'lishi kerak.")
    return value

def validate_content(value):
    if not value.strip():
        raise ValidationError("Kontent bo'sh bo'lishi mumkin emas.")
    if len(value) < 10:
        raise ValidationError("Kontent kamida 10 ta belgidan iborat bo'lishi kerak.")
    return value