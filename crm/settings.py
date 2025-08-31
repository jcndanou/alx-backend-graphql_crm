INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'django_filters',
    'crm',
    'django_crontab'
]

# Configuration des tâches cron
CRONJOBS = [
    # Exécute la fonction log_crm_heartbeat toutes les heures
    ('0 * * * *', 'crm.cron.log_crm_heartbeat', '>> /tmp/crm_heartbeat.log 2>&1'),
    # Mise à jour du stock faible toutes les 12 heures
    ('0 */12 * * *', 'crm.cron.update_low_stock', '>> /tmp/stock_update.log 2>&1'),
]

# Optionnel : où stocker les fichiers PID
CRONTAB_COMMAND_PREFIX = 'export LANG=fr_FR.UTF-8;'
CRONTAB_COMMAND_SUFFIX = '2>&1'