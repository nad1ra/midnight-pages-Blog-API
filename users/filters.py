import django_filters
from users.models import CustomUser


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains', label="Username")
    email = django_filters.CharFilter(lookup_expr='icontains', label="Email")
    role = django_filters.ChoiceFilter(choices=CustomUser._meta.get_field('role').choices)
    date_joined = django_filters.DateFromToRangeFilter(label="Joined date range")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'date_joined']