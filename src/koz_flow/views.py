from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError
import json

def health_check(request):
    """ 
    Endpoint de healthcheck pour Docker.
    Vérifie que django tourne et que la base de données est accessible.    
    """
    
    status_data = {
        "status": "healthy",
        "django":"ok",
        "database": "ok"
    }
    http_status = 200
    
    # Vérifie la base de données
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1") # Exécute une requête simple pour vérifier la connexion à la base de données
    except OperationalError:
        status_data["status"] = "unthealthy"
        status_data["database"] = "error"
        http_status = 503
    return JsonResponse(status_data, status=http_status)
        
   