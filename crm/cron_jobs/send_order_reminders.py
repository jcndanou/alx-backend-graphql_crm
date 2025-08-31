#!/usr/bin/env python3
"""
Script pour envoyer des rappels de commandes via GraphQL
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/order_reminders_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def fetch_recent_orders():
    """
    Récupère les commandes récentes via l'API GraphQL
    """
    # Configuration du transport GraphQL
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",  # Remplacez par votre endpoint
        verify=True,
        retries=3,
    )

    # Création du client GraphQL
    client = Client(
        transport=transport,
        fetch_schema_from_transport=True,
    )

    # Requête GraphQL pour récupérer les commandes récentes
    query = gql("""
    query GetRecentOrders($hours: Int!) {
        recentOrders(hours: $hours) {
            id
            orderNumber
            customer {
                id
                firstName
                lastName
                email
            }
            totalAmount
            status
            createdAt
            items {
                product {
                    name
                    sku
                }
                quantity
                price
            }
        }
    }
    """)

    # Variables pour la requête (commandes des dernières 24h)
    variables = {"hours": 24}

    try:
        logger.info("Début de la récupération des commandes récentes")

        # Exécution de la requête
        result = client.execute(query, variable_values=variables)

        logger.info(f"Nombre de commandes récupérées: {len(result.get('recentOrders', []))}")

        return result.get('recentOrders', [])

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des commandes: {str(e)}")
        return []


def process_orders(orders):
    """
    Traite les commandes et génère les rappels
    """
    if not orders:
        logger.info("Aucune commande récente à traiter")
        return

    logger.info(f"Début du traitement de {len(orders)} commandes")

    for order in orders:
        try:
            order_id = order.get('id', 'N/A')
            order_number = order.get('orderNumber', 'N/A')
            customer = order.get('customer', {})
            customer_name = f"{customer.get('firstName', '')} {customer.get('lastName', '')}".strip()
            customer_email = customer.get('email', 'N/A')
            total_amount = order.get('totalAmount', 0)
            status = order.get('status', 'N/A')

            logger.info(
                f"Traitement commande #{order_number} - Client: {customer_name} - Total: {total_amount} € - Statut: {status}")

            # Ici vous pouvez ajouter la logique d'envoi d'email/SMS
            # send_reminder_email(customer_email, order_number, total_amount)

        except Exception as e:
            logger.error(f"Erreur lors du traitement de la commande {order.get('id', 'N/A')}: {str(e)}")


def main():
    """
    Fonction principale
    """
    logger.info("=" * 50)
    logger.info("DÉMARRAGE DU SCRIPT DE RAPPEL DE COMMANDES")
    logger.info("=" * 50)

    # Récupération des commandes récentes
    orders = fetch_recent_orders()

    # Traitement des commandes
    process_orders(orders)

    logger.info("=" * 50)
    logger.info("FIN DU SCRIPT DE RAPPEL DE COMMANDES")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()