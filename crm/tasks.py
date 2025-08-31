# crm/tasks.py
import os
import logging
import time
from celery import shared_task
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

# Configuration du logger pour écrire dans un fichier
logging.basicConfig(filename='/tmp/crm_report_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

@shared_task
def generate_crm_report():
    """
    Génère un rapport CRM hebdomadaire en utilisant une requête GraphQL.
    """
    try:
        # Configuration du transport GraphQL
        transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Requête GraphQL pour récupérer les données du rapport
        query = gql("""
            query CrmReport {
                totalCustomers
                totalOrders
                totalRevenue
            }
        """)

        # Exécution de la requête
        result = client.execute(query)

        # Extraction des données
        customers = result.get('totalCustomers', 0)
        orders = result.get('totalOrders', 0)
        revenue = result.get('totalRevenue', 0.0)

        # Création du message de rapport
        report_message = (f"Report: {customers} customers, {orders} orders, "
                          f"{revenue:.2f} revenue.")

        # Enregistrement dans le fichier de log
        logging.info(report_message)
        print(report_message) # Pour le log du worker

    except Exception as e:
        # Log en cas d'erreur
        logging.error(f"Error generating CRM report: {e}")
        print(f"Error: {e}")

    return "CRM report generated."