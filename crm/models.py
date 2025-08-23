from django.db import models


class Customer(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="prénom")
    last_name = models.CharField(max_length=100, verbose_name="nom")
    email = models.EmailField(unique=True, verbose_name="adresse email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="téléphone")
    address = models.TextField(blank=True, verbose_name="adresse")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="date de création")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="nom")
    description = models.TextField(blank=True, verbose_name="description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="prix")
    stock_quantity = models.IntegerField(default=0, verbose_name="quantité en stock")
    is_available = models.BooleanField(default=True, verbose_name="disponible")

    def __str__(self):
        return self.name


class Order(models.Model):
    # Relation ForeignKey: Une commande est liée à UN SEUL client
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,  # Si on supprime le client, ses commandes sont supprimées
        related_name='orders',
        verbose_name="client"
    )

    # Relation ManyToManyField: Une commande peut avoir PLUSIEURS produits
    products = models.ManyToManyField(
        Product,
        through='OrderItem',  # Table intermédiaire personnalisée
        verbose_name="produits"
    )

    order_date = models.DateTimeField(auto_now_add=True, verbose_name="date de commande")
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('shipped', 'Expédié'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="statut"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="montant total"
    )

    def __str__(self):
        return f"Commande #{self.id} - {self.customer}"


class OrderItem(models.Model):
    # Relation ForeignKey: Un item appartient à UNE commande
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Relation ForeignKey: Un item concerne UN produit
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1, verbose_name="quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="prix unitaire")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"