import graphene
from django.db import transaction
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from .models import Customer, Product, Order, OrderItem
from crm.models import Product

# Type pour le modèle Customer
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"  # Inclut tous les champs du modèle

# Type pour le modèle Product
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

# Type pour le modèle Order
class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# Type pour le modèle OrderItem (optionnel mais utile)
class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = "__all__"


class Query(graphene.ObjectType):
    # Query pour récupérer tous les clients
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter
    )

    # Query pour récupérer tous les produits
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter
    )

    # Query pour récupérer toutes les commandes
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter
    )

    # Méthode pour résoudre la query des clients
    def resolve_all_customers(root, info):
        return Customer.objects.all()

    # Méthode pour résoudre la query des produits
    def resolve_all_products(root, info):
        return Product.objects.all()

    # Méthode pour résoudre la query des commandes
    def resolve_all_orders(root, info):
        return Order.objects.all()


# Mutation pour créer un client
class CreateCustomer(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)
        address = graphene.String(required=False)

    # Ce que la mutation retourne
    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, first_name, last_name, email, phone=None, address=None):
        try:
            # Validation simple pour l'email unique
            if Customer.objects.filter(email=email).exists():
                raise ValidationError("Un client avec cet email existe déjà")

            # Création du client
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone or "",
                address=address or ""
            )
            customer.full_clean()  # Validation Django
            customer.save()

            return CreateCustomer(customer=customer, success=True, errors=None)

        except ValidationError as e:
            return CreateCustomer(customer=None, success=False, errors=str(e))


# Mutation pour créer un produit
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        price = graphene.Float(required=True)
        stock_quantity = graphene.Int(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, name, price, stock_quantity, description=None):
        try:
            product = Product(
                name=name,
                description=description or "",
                price=price,
                stock_quantity=stock_quantity
            )
            product.full_clean()
            product.save()

            return CreateProduct(product=product, success=True, errors=None)

        except ValidationError as e:
            return CreateProduct(product=None, success=False, errors=str(e))


# Mutation pour créer une commande
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.Int(required=True)
        product_ids = graphene.List(graphene.Int, required=True)
        quantities = graphene.List(graphene.Int, required=True)

    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, customer_id, product_ids, quantities):
        try:
            # Vérifier que le client existe
            customer = Customer.objects.get(id=customer_id)

            # Vérifier que les produits existent
            products = Product.objects.filter(id__in=product_ids)
            if len(products) != len(product_ids):
                raise ValidationError("Un ou plusieurs produits n'existent pas")

            # Créer la commande
            order = Order(customer=customer, status='pending')
            order.save()

            # Ajouter les produits à la commande via OrderItem
            total_amount = 0
            for i, product_id in enumerate(product_ids):
                product = products.get(id=product_id)
                quantity = quantities[i] if i < len(quantities) else 1

                order_item = OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                order_item.save()
                total_amount += product.price * quantity

            # Mettre à jour le montant total
            order.total_amount = total_amount
            order.save()

            return CreateOrder(order=order, success=True, errors=None)

        except (Customer.DoesNotExist, ValidationError) as e:
            return CreateOrder(order=None, success=False, errors=str(e))


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        min_stock = graphene.Int(description="Seuil de stock minimum", default_value=10)
        increment_by = graphene.Int(description="Quantité à ajouter", default_value=50)

    success = graphene.Boolean()
    message = graphene.String()
    updated_count = graphene.Int()

    @transaction.atomic
    def mutate(self, info, min_stock=10, increment_by=50):
        try:
            # Trouver les produits avec stock faible
            low_stock_products = Product.objects.filter(stock_quantity__lt=min_stock)

            # Compter le nombre de produits à mettre à jour
            count = low_stock_products.count()

            if count == 0:
                return UpdateLowStockProducts(
                    success=True,
                    message="Aucun produit avec stock faible trouvé",
                    updated_count=0
                )

            # Mettre à jour le stock
            updated_products = []
            for product in low_stock_products:
                product.stock_quantity += increment_by
                updated_products.append(product)

            # Sauvegarder en bulk pour plus d'efficacité
            Product.objects.bulk_update(updated_products, ['stock_quantity'])

            return UpdateLowStockProducts(
                success=True,
                message=f"{count} produits avec stock faible mis à jour",
                updated_count=count
            )

        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Erreur lors de la mise à jour: {str(e)}",
                updated_count=0
            )

# Regroupe toutes les mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)