#!/bin/bash

cd ../../

python manage.py shell << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from alx_backend_graphql.models import Customer
from django.utils import timezone
from datetime import timedelta

inactive_customers = Customer.objects.filter(
    last_login__lt=timezone.now() - timedelta(days=365),
    is_active=False
)
count = inactive_customers.count()
inactive_customers.delete()

print(f"Nombre de clients inactifs supprimés : {count}")
EOF >> /var/log/crm/customer_cleanup.log 2>&1