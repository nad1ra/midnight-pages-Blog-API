from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelf(BasePermission):
    """
    Faqat o'z profilini ko'rish yoki o'zgartirishga ruxsat beradi.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerOrReadOnly(BasePermission):
    """
    Ob'ekt egasi bo'lsa, o'zgartirishi mumkin. Aks holda faqat o'qish mumkin.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        # Avval author, owner, user qatoriga qaraymiz.
        for attr in ['author', 'owner', 'user']:
            if hasattr(obj, attr):
                return getattr(obj, attr) == request.user
        return False


class IsOwner(BasePermission):
    """
    Faqat ob'ekt egasiga ruxsat beradi.
    """
    def has_object_permission(self, request, view, obj):
        for attr in ['author', 'owner', 'user']:
            if hasattr(obj, attr):
                return getattr(obj, attr) == request.user
        return False
