### Configuration et exécution des tâches Celery

Ce projet utilise Celery et Celery Beat pour la planification des tâches asynchrones.

#### 1. Prérequis
- Assurez-vous que Redis est installé et en cours d'exécution. Vous pouvez le lancer via Docker : `docker run --name my-redis -d -p 6379:6379 redis:latest`.
- Installez les dépendances : `pip install -r requirements.txt`.

#### 2. Démarrage des services
Vous devez lancer 3 processus dans des terminaux séparés :

1. **Lancez le serveur Redis** :
   `redis-server` (si vous avez Redis installé localement) ou assurez-vous que votre conteneur Docker est en cours d'exécution.

2. **Lancez le Celery Worker** :
   Naviguez vers la racine du projet et exécutez :
   `celery -A crm worker -l info`

3. **Lancez Celery Beat (le planificateur)** :
   Naviguez vers la racine du projet et exécutez :
   `celery -A crm beat -l info`

#### 3. Vérification
- Une fois Celery Beat démarré, vous verrez une ligne indiquant que le rapport a été ajouté au planning.
- Pour vérifier l'exécution, consultez le fichier `/tmp/crm_report_log.txt` une fois que la tâche est censée s'être exécutée.
- Vous pouvez forcer l'exécution d'une tâche pour la tester immédiatement avec la commande suivante :
  `python manage.py shell -c "from crm.tasks import generate_crm_report; generate_crm_report.delay()"`

Pour arrêter les services, utilisez `Ctrl+C` dans chaque terminal.