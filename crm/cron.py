
import os
import logging
from datetime import datetime
from django.utils import timezone
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configuration du logging
logger = logging.getLogger(__name__)


def log_crm_heartbeat():
    """
    Fonction de heartbeat qui log l'état du CRM toutes les heures
    Utilise le mode append ('a') pour ajouter aux logs existants
    """
    try:
        # Chemin du fichier de log
        log_file = '/tmp/crm_heartbeat_log.txt'

        # Heure actuelle
        now = timezone.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S %Z')

        # Message de heartbeat
        message = f"[{timestamp}] CRM Heartbeat - Système en fonctionnement normal"

        # Écriture dans le fichier en mode append
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')

        # Also log to Django logging system
        logger.info(message)

        return f"Heartbeat logged at {timestamp}"

    except Exception as e:
        error_message = f"Erreur lors de l'écriture du heartbeat: {str(e)}"
        logger.error(error_message)

        # Essayez d'écrire l'erreur dans le fichier log
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {error_message}\n")
        except:
            pass

        return error_message


def clean_inactive_customers():
    """
    une autre fonction cron pour nettoyer les clients inactifs
    """
    try:
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from datetime import timedelta

        User = get_user_model()

        # Clients inactifs depuis plus d'un an
        one_year_ago = timezone.now() - timedelta(days=365)
        inactive_customers = User.objects.filter(
            last_login__lt=one_year_ago,
            is_active=True
        )

        count = inactive_customers.count()

        # Désactiver les clients inactifs
        inactive_customers.update(is_active=False)

        message = f"{count} clients inactifs désactivés"
        logger.info(message)

        # Écrire dans le fichier log
        with open('/var/log/crm/cleanup.log', 'a', encoding='utf-8') as f:
            f.write(f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

        return message

    except Exception as e:
        error_message = f"Erreur lors du nettoyage des clients: {str(e)}"
        logger.error(error_message)
        return error_message


def update_low_stock():
    """
    Fonction cron pour mettre à jour les produits avec stock faible
    en utilisant la mutation GraphQL
    """
    try:
        # Configuration du transport GraphQL
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",  # Votre endpoint GraphQL
            verify=True,
            retries=3,
        )

        # Création du client GraphQL
        client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
        )

        # Mutation GraphQL pour mettre à jour les produits avec stock faible
        mutation = gql("""
        mutation UpdateLowStock {
            updateLowStockProducts(minStock: 10, incrementBy: 50) {
                success
                message
                updatedCount
            }
        }
        """)

        # Exécution de la mutation
        result = client.execute(mutation)

        # Log des résultats
        response = result.get('updateLowStockProducts', {})

        if response.get('success'):
            message = f"Stock mis à jour: {response.get('message')}"
            logger.info(message)
        else:
            message = f"Échec de la mise à jour: {response.get('message')}"
            logger.error(message)

        # Écrire dans le fichier log
        log_file = '/tmp/stock_update.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")

        return message

    except Exception as e:
        error_message = f"Erreur lors de la mise à jour du stock: {str(e)}"
        logger.error(error_message)

        # Écrire l'erreur dans le fichier log
        try:
            with open('/tmp/stock_update.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] ERROR: {error_message}\n")
        except:
            pass

        return error_message