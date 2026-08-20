from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from vehicul_app.models import Vehicul
from django.utils import timezone
from datetime import timedelta

# ---------- GESTIONNAIRE PERSONNALISÉ ----------
# C'est le chef d'orchestre qui va créer et gérer nos kozUsers
# BaseUserManager est la classe par défaut de Django, on la modifie
class kozUserManager(BaseUserManager):
    """
    Cette classe sait comment créer un kozUser (utilisateur) dans la base de données.
    Django a besoin de ça pour fonctionner avec notre modèle personnalisé.
    """
    
    def create_user(self, email, nom_complet, telephone, password=None, **extra_fields):
        """
        Crée un kozUser normal (pas un admin)
        
        Paramètres:
        - email: l'email du kozUser (obligatoire, sert d'identifiant)
        - nom_complet: son nom et prénom
        - telephone: son numéro de téléphone
        - password: son mot de passe (peut être None pour un compte sans mot de passe)
        - extra_fields: autres champs optionnels
        """
        
        # ÉTAPE 1: Vérifier que l'email est fourni
        # Si pas d'email, c'est une erreur (on ne peut pas avoir un kozUser anonyme)
        if not email:
            raise ValueError('Le kozUser doit avoir un email')
        
        # ÉTAPE 2: Nettoyer l'email (enlève les espaces, met en minuscules)
        # "  JEAN@GMAIL.COM  " devient "jean@gmail.com"
        email = self.normalize_email(email)
        
         # ÉTAPE 3: Créer l'objet kozUser (sans l'enregistrer encore en base)
        # **extra_fields permet de passer des champs comme est_actif, est_staff, etc.
        user = self.model(
            email=email,
            nom_complet=nom_complet,
            telephone=telephone,
            **extra_fields
        )
        
         # ÉTAPE 4: Hasher (crypter) le mot de passe
        # On ne stocke JAMAIS le mot de passe en clair, Django le transforme en hash
        
        if password:
            user.set_password(password)
        
          
        # ÉTAPE 5: Sauvegarder dans la base de données
        # using=self._db est pour la compatibilité multi-base de données
        user.save(using=self._db)
            
        # ÉTAPE 6: Retourner le kozUser créé
        return user    
    
    def create_superuser(self, email, nom_complet, telephone, password=None, **extra_fields):
        """
        Crée un superutilisateur (admin) qui a tous les droits
        Un superuser peut accéder à l'interface d'administration Django
        """
        #Un superUser doit avoir is_staff = True
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault("is_active",True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError('Le superuser doit avoir is_staff=True')
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True")
        
        return self.create_user(email, nom_complet, telephone, password=None, **extra_fields)


class  kozUser(AbstractBaseUser, PermissionsMixin):
    """
        Modèle unique pour:
        -authentication du site 
        -authentification CRM

    """
    ROLE_CHOICES = [
        ("client", "Client"),
        ("commercial", "Commercial"),
        ('directeur', "Directeur")
       ]
    
    GENDER_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
        ]
    
    PROFESSION_CHOICES = [
        ("employe", "Employé"), 
        ("chef_d_equipe", "Chef d'équipe"), 
        ("gerant", "Gérant"),
        ("etudiant", "Étudiant"),
        ("autre", "Autre")]
    
    # ----- CHAMPS IDENTITÉ -----
    email = models.EmailField(
        unique=True,
        verbose_name="Adresse Email")
    
    nom_complet = models.CharField(max_length=150, verbose_name='Nom et prenom')
    telephone = models.CharField(max_length=30, verbose_name="Numéro de telephone")
    adresse = models.TextField(null=True, blank=True, verbose_name="Adresse de livraison")
    pays = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pays de résidence")
    ville = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ville de résidence")
    genre = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="Genre")
    
     
    profession_choisie  = models.CharField(
        choices=PROFESSION_CHOICES,
        null=True,
        blank=True
    )
    
    profession = models.CharField(max_length=100, null=True, blank=True)
    
    
    #Une demande de financement appartient à un seul kozUser, mais un kozUser peut faire plusieurs demandes de financement au fil du temp
    #----- CHAMPS DE GESTION -----
    
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='client')
    
 
    assigned_commercial = models.ForeignKey(
                "self",
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name='clients_assignes',
                limit_choices_to={'role': 'commercial'},
                verbose_name="Commercial assigné"
            )
    
    date_inscription = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'inscription"
    )
    
    date_dernière_connexion = models.DateField(
        auto_now=True,
        verbose_name=" dernière connexion"
    )
    
    last_activity = models.DateTimeField(null=True, blank=True)
    
    est_actif = models.BooleanField(
        default=True,
        verbose_name='compte actif'
                                    )
     
    #----------------CONFIGURATION POUR DJANGO ----------------------
    # on dit à Django: ustilise 'email' comme identifiant, pas username
    USERNAME_FIELD = 'email'
    
    #les champs obligatoires en plus de l'email lors creation
    REQUIRED_FIELDS = ["nom_complet", 'telephone']
    
    #on attache note gestionnnaire personnalisé à ce modèle
    objects = kozUserManager()
    
     # ✅ AJOUTE CES CHAMPS (si pas déjà)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    #---------- METADONNEES----------------
    class Meta:
        #nom de la table dans la base de données
        db_table = 'kozUsers'
        ordering = ["-date_inscription"]
        verbose_name = 'kozUser'
        verbose_name_plural = "kozUsers"
    
    #------------PROPRIETE UTILES POUR LE MODELE KOZUSER ------------
    @property
    def est_en_ligne(self):
        if not self.last_activity:
            return False
        return timezone.now()- self.last_activity < timedelta(minutes=5)
    
    @property
    def est_hors_ligne(self):
        return not self.est_en_ligne
    
    
    @property
    def dernier_message(self):
        if self.role == "client":
            return  self.messages_envoyes.last() 
        return None
    
    @property
    def nb_messages_non_lus(self):
        if self.role == "client":
            return self.messages_envoyes.filter(lu=False, est_client=True).count()
        return 0
  
    
    
    #---------- METHODES UTILES POUR LE MODÈLE KOZUSER -------------
     
    def __str__(self):
        return f"{self.email} - {self.nom_complet} ({self.get_role_display()})"
    
    def get_nom_complet(self):
        return self.nom_complet
    
    def a_demande_financement(self):
        """Retourne True si l'utilisateur a fait une demande de financement"""
        return hasattr(self, 'demande_financement') and self.demande_financement is not None
    
    def get_panier(self):
        """Retourne l'objet Panier du client, le crée si inexistant"""
        if self.role != "client":
            return None  # Seuls les clients ont un panier
        
        from order_app.models import Panier
        panier, created = Panier.objects.get_or_create(client=self)
        return panier
    
    def get_commercial_assigned(self):
        """Retourne le commercial assigné au client, ou None s'il n'en a pas"""
        if self.role != "client":
            return None  # Seuls les clients ont un commercial assigné
        return self.assigned_commercial
    
    
    
    @property
    def derniere_connexion_formatee(self):
        """Retourne la date de dernière connexion formatée"""
        if self.last_login:
            return self.last_login.strftime('%Y-%m-%d %H:%M:%S')
        return "Jamais connecté"
    
    def get_role_display_fr(self):
        """Retourne le rôle en français"""
        roles = {
            'client': 'Client',
            'commercial': 'Commercial',
            'directeur': 'Directeur',
        }
        return roles.get(self.role, self.role)
    
    def get_absolute_url(self):
        return reverse('client_app:client-detail', kwargs={'pk': self.pk})