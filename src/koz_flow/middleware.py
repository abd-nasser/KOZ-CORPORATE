from django.utils import timezone

class LastActivityMiddleware:
    def __init__(self, get_response):
        # 1️⃣ get_response = la fonction qui génère la réponse HTTP
        #    Stockée pour être utilisée plus tard
        self.get_response = get_response
        
    def __call__(self, request):
        #  1️⃣ cette methode est appelée à chaque requête
        # "request" =  l'objet HTTP reçu par django
        
        # 2️⃣ si l'utilisateur est connecté (session ou JWT)
        if request.user.is_authenticated:
            # 3️⃣ on met à jour le champ last_activity avec l'heure acturlle
            request.user.last_activity = timezone.now()
            
            # 4️⃣ on sauvegarde UNIQUEMENT ce champs (optimisation)
            request.user.save(update_fields=['last_activity'])
            
        # 5️⃣ on continue le traitement de la requête
        #   (important ! sinon la page ne s'affiche pas)
        return self.get_response(request)