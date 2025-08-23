# crm/filters.py
import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    # Filtre texte pour le prénom (recherche insensible à la casse)
    first_name = django_filters.CharFilter(lookup_expr='icontains', label='Prénom contient')

    # Filtre texte pour le nom (recherche insensible à la casse)
    last_name = django_filters.CharFilter(lookup_expr='icontains', label='Nom contient')

    # Filtre exact pour l'email
    email = django_filters.CharFilter(lookup_expr='exact', label='Email exact')

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email']


class ProductFilter(django_filters.FilterSet):
    # Filtre texte pour le nom du produit
    name = django_filters.CharFilter(lookup_expr='icontains', label='Nom du produit contient')

    # Filtre pour les prix minimum et maximum
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Prix minimum')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Prix maximum')

    # Filtre pour les produits disponibles uniquement
    is_available = django_filters.BooleanFilter(field_name='is_available', label='Disponible uniquement')

    class Meta:
        model = Product
        fields = ['name', 'price', 'is_available']


class OrderFilter(django_filters.FilterSet):
    # Filtre par client (ID ou nom)
    customer = django_filters.ModelChoiceFilter(
        queryset=Customer.objects.all(),
        field_name='customer',
        label='Client'
    )

    # Filtre par statut de commande
    status = django_filters.ChoiceFilter(
        choices=Order.STATUS_CHOICES,  # Assurez-vous que ce champ existe dans votre modèle Order
        label='Statut de la commande'
    )

    # Filtre par date de commande
    order_date_min = django_filters.DateFilter(field_name='order_date', lookup_expr='gte', label='Date minimum')
    order_date_max = django_filters.DateFilter(field_name='order_date', lookup_expr='lte', label='Date maximum')

    # Filtre par montant total
    total_min = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte', label='Montant minimum')
    total_max = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte', label='Montant maximum')

    class Meta:
        model = Order
        fields = ['customer', 'status', 'order_date', 'total_amount']


