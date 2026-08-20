 nasserdevtest@gmail.com : rbs4YRuKGw 
 spiritdigitagency@gmail.com : MLbLZiBDKt
# Breakpoint	Taille	Suffixe	Usage
XS	< 576px	sm:	Smartphone
SM	576px - 768px	md:	Smartphone large / Tablette
MD	768px - 1024px	lg:	Tablette / Petit desktop
LG	1024px - 1440px	xl:	Desktop standard
XL	1440px - 1920px	2xl:	Grand écran (27 pouces)
XXL	> 1920px	—	Ultra large (ton écran)




# 🚗 KOZ SERVICES - ERP & CRM Automobile

Plateforme complète de gestion pour concessionnaire automobile : demandes de financement, offres, ventes, maintenance, et e-commerce.

---

## 📦 Technologies utilisées

- **Backend** : Django 5.0, Django REST Framework
- **Frontend** : HTMX, TailwindCSS, DaisyUI, Chart.js
- **Base de données** : PostgreSQL (production), SQLite (dev)
- **Paiements** : Ligdicash (Mobile Money / Carte bancaire)
- **Conteneurisation** : Docker, Docker Compose

---

## 👥 Rôles & Fonctionnalités

### 👤 Client
- ✅ Inscription / Connexion sécurisée (JWT + sessions)
- ✅ Demande de financement de véhicule
- ✅ Upload de documents (CNI, quittance, relevé bancaire, etc.)
- ✅ Suivi du dossier (étapes : en attente, en cours, accordée, refusée)
- ✅ Consultation et acceptation/refus des offres
- ✅ Messagerie interne avec son commercial
- ✅ Gestion des maintenances (prochaines dates, historique)
- ✅ Simulation de crédit inversée (mensualité → prix accessible)
- ✅ Dashboard personnel avec indicateurs

### 💼 Commercial
- ✅ Dashboard avec liste des clients assignés
- ✅ Gestion des demandes de financement (changement d'étapes)
- ✅ Vérification et validation des documents clients
- ✅ Génération d’offres (liées à une demande ou simples)
- ✅ Gestion des ventes (statuts : conclue, perdue, en cours)
- ✅ Messagerie interne avec ses clients
- ✅ Planification des maintenances pour les clients
- ✅ Filtres avancés (HTMX) sur toutes les listes

### 👔 Directeur
- ✅ Dashboard KPI complet (cartes cliquables, graphiques)
- ✅ Graphique d’évolution du CA (Fidelis, Alios, KOZ, Cash)
- ✅ Création / gestion des utilisateurs (commerciaux, directeurs)
- ✅ Vue globale sur toutes les demandes, offres, ventes, maintenances
- ✅ Gestion du catalogue véhicules (CRUD)
- ✅ Gestion du catalogue produits (pièces détachées)
- ✅ Export des données (Excel - à venir)

---

## 🧩 Modules principaux

| Module | Description | Statut |
|--------|-------------|--------|
| **Authentification** | JWT + sessions, rôles client/commercial/directeur | ✅ 100% |
| **Demandes de financement** | Workflow complet (soumission, validation, étapes) | ✅ 100% |
| **Documents** | Upload, vérification, validation par le commercial | ✅ 100% |
| **Offres** | Génération, acceptation/refus, négociation, expiration auto | ✅ 100% |
| **Ventes** | Création auto (offres acceptées) + gestion manuelle | ✅ 100% |
| **Maintenances** | Suivi, rappels, priorité, origine véhicule (KOZ/externe) | ✅ 100% |
| **Messagerie** | Chat client ↔ commercial (HTMX) | ✅ 100% |
| **Dashboard DG** | KPI cliquables, graphique CA (4 courbes), filtres | ✅ 100% |
| **E-commerce** | Panier, commandes (APIs), Ligdicash en attente | 🔄 80% |
| **Produits / Véhicules** | CRUD complet côté ERP | ✅ 100% |
| **Notifications** | Email (SMTP) + WhatsApp Business | ⏳ 0% |

---

## 📊 Workflow métier principal





{% load static %}
{% load tailwind_tags %}
<!DOCTYPE html>
<html lang="fr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    {% tailwind_css %}
    <script src="{% static 'js/htmx.min.js' %}" defer></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="{% static 'css/directeur/directeur_style.css' %}">
    <title>Cockpit Direction - KOZ Services</title>
</head>
<body class="bg-blue-50 text-blue-600 font-inter min-h-screen selection:bg-cyan-500 selection:text-slate-950">

    <!-- Messages Flash Notification -->
    {% if messages %}
    <div class="fixed top-20 right-5 z-50 space-y-2 max-w-sm">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} shadow-2xl rounded-xl border border-slate-700 bg-slate-900/95 backdrop-blur-md text-sm p-4 animate-slide-in-right">
            <span>{{ message }}</span>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Top Navigation Executive -->
    <nav class="sticky top-0 z-40 bg-blue-400 backdrop-blur-xl border-b border-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <!-- Brand & Status -->
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-cyan-500 to-blue-400 p-0.5 shadow-lg shadow-cyan-500/20">
                        <div class="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                            <span class="text-transparent bg-clip-text bg-gradient-to-tr from-cyan-400 to-blue-500 font-extrabold text-xl">K</span>
                        </div>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-bold text-lg tracking-wide text-white">KOZ SERVICES</span>
                            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                Direction
                            </span>
                        </div>
                        <p class="text-[11px] text-slate-400 hidden sm:block">Console de Pilotage Général</p>
                    </div>
                </div>

                <!-- Fast Actions & Profil Header -->
                <div class="flex items-center gap-3">
                    <!-- Dropdown Action Rapide (Regroupement des Modales) -->
                    <div class="relative group">
                        <button class="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs sm:text-sm transition-all duration-200 shadow-lg shadow-cyan-500/20 active:scale-95">
                            <i class="fas fa-plus"></i>
                            <span class="hidden sm:inline">Créer / Ajouter</span>
                            <i class="fas fa-chevron-down text-xs ml-1 transition-transform group-hover:rotate-180"></i>
                        </button>

                        <!-- Menu déroulant des Modales -->
                        <div class="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 p-2 divide-y divide-slate-800/60">
                            <!-- Section Utilisateurs -->
                            <div class="py-1">
                                <span class="px-3 py-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase block">Administration</span>
                                <button onclick="document.getElementById('userregister_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-user-plus text-blue-400 w-4"></i> Ajouter un utilisateur
                                </button>
                                <button onclick="document.getElementById('change_pass_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-key text-slate-400 w-4"></i> Changer mot de passe
                                </button>
                            </div>
                            <!-- Section Flotte & Véhicules -->
                            <div class="py-1">
                                <span class="px-3 py-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase block">Flotte & Parc</span>
                                <button onclick="document.getElementById('vehicul_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-car text-emerald-400 w-4"></i> Ajouter un véhicule
                                </button>
                                <button onclick="document.getElementById('marque_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-trademark text-emerald-400 w-4"></i> Ajouter une marque
                                </button>
                                <button onclick="document.getElementById('type_vehicul_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-car-side text-teal-400 w-4"></i> Ajouter type de véhicule
                                </button>
                            </div>
                            <!-- Section Produits & Services -->
                            <div class="py-1">
                                <span class="px-3 py-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase block">Offre & Catalogue</span>
                                <button onclick="document.getElementById('create_product_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-box text-amber-400 w-4"></i> Ajouter un produit
                                </button>
                                <button onclick="document.getElementById('create_categorie_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-tags text-amber-400 w-4"></i> Ajouter une catégorie
                                </button>
                                <button onclick="document.getElementById('services_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-wrench text-purple-400 w-4"></i> Ajouter un service
                                </button>
                                <button onclick="document.getElementById('types_services_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-layer-group text-purple-400 w-4"></i> Ajouter type de service
                                </button>
                            </div>
                            <!-- Section Média & Actualités -->
                            <div class="py-1">
                                <span class="px-3 py-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase block">Communication</span>
                                <button onclick="document.getElementById('actualite_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-newspaper text-rose-400 w-4"></i> Publier une actualité
                                </button>
                                <button onclick="document.getElementById('avis_reseau_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-comment-medical text-pink-400 w-4"></i> Ajouter un avis réseau
                                </button>
                                <button onclick="document.getElementById('video_temoignage_modal').showModal()" class="w-full text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition flex items-center gap-2">
                                    <i class="fas fa-video text-pink-400 w-4"></i> Ajouter témoignage vidéo
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Déconnexion -->
                    <a href="{% url 'auth_app:logout-simple' %}" id="logoutBtn" class="bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-300 border border-slate-700/60 p-2 sm:px-3 sm:py-2 rounded-xl text-xs transition-all duration-200 flex items-center gap-2">
                        <i class="fas fa-sign-out-alt"></i>
                        <span class="hidden md:inline">Déconnexion</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Content Area -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        <!-- Banner Welcome Executive -->
        <div class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800 border border-slate-800 p-6 sm:p-8 shadow-2xl">
            <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div class="space-y-2">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        <span class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Opérationnel</span>
                    </div>
                    <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                        Bonjour, <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">{{ user.nom_complet }}</span>
                    </h1>
                    <p class="text-slate-400 text-sm max-w-xl">
                        Supervisez l'activité globale, les flux commerciaux et contrôlez la performance de KOZ Services en temps réel.
                    </p>
                </div>

                <!-- Info carte Directeur compacte -->
                <div class="flex items-center gap-4 bg-slate-950/60 backdrop-blur-md p-4 rounded-2xl border border-slate-800/80">
                    <div class="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 text-xl font-bold">
                        <i class="fas fa-user-shield"></i>
                    </div>
                    <div class="text-xs space-y-0.5">
                        <p class="text-slate-400">Compte : <strong class="text-white">{{ user.email }}</strong></p>
                        <p class="text-slate-400">Rôle : <span class="text-cyan-400 font-semibold">Directeur Général</span></p>
                        <p class="text-slate-500 text-[10px]"><i class="fas fa-calendar-alt mr-1"></i>{% now "l d F Y" %}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Section 1 : Dashboard KPI & Ventes (Priorité DG) -->
        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <h2 class="text-sm font-bold tracking-wider text-slate-400 uppercase flex items-center gap-2">
                    <i class="fas fa-chart-line text-cyan-400"></i> Pilotage Commercial & Analytique
                </h2>
                <a href="{% url 'dashboard_app:dashboard-view' %}" class="text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition flex items-center gap-1">
                    Vue détaillée <i class="fas fa-arrow-right text-[10px]"></i>
                </a>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- Card 1: Dashboard Analytics -->
                <a href="{% url 'dashboard_app:dashboard-view' %}" class="group relative bg-slate-900 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/50 transition-all duration-300 shadow-lg">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
                            <i class="fas fa-chart-pie text-lg"></i>
                        </div>
                        <span class="text-[10px] font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">KPIs</span>
                    </div>
                    <h3 class="text-base font-bold text-white group-hover:text-cyan-400 transition">Tableau des Métriques</h3>
                    <p class="text-slate-400 text-xs mt-1">Vue synthétique sur le chiffre d'affaires et la rentabilité.</p>
                </a>

                <!-- Card 2: Ventes & Contrats -->
                <a href="{% url 'commercial_app:vente-list' %}" class="group relative bg-slate-900 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-emerald-500/50 transition-all duration-300 shadow-lg">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                            <i class="fas fa-receipt text-lg"></i>
                        </div>
                        <span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">Revenus</span>
                    </div>
                    <h3 class="text-base font-bold text-white group-hover:text-emerald-400 transition">Journal des Ventes</h3>
                    <p class="text-slate-400 text-xs mt-1">Suivi des transactions conclues et des encaissements.</p>
                </a>

                <!-- Card 3: Offres Commerciales -->
                <a href="{% url 'commercial_app:offre-list' %}" class="group relative bg-slate-900 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-blue-500/50 transition-all duration-300 shadow-lg">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                            <i class="fas fa-file-signature text-lg"></i>
                        </div>
                        <span class="text-[10px] font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full border border-blue-500/20">Pipeline</span>
                    </div>
                    <h3 class="text-base font-bold text-white group-hover:text-blue-400 transition">Offres & Devis</h3>
                    <p class="text-slate-400 text-xs mt-1">Validation des propositions financières transmises.</p>
                </a>

                <!-- Card 4: Demandes & Financement -->
                <a href="{% url 'leads_app:list-demande-financement' %}" class="group relative bg-slate-900 hover:bg-slate-800/80 p-5 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all duration-300 shadow-lg">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                            <i class="fas fa-hand-holding-usd text-lg"></i>
                        </div>
                        <span class="text-[10px] font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">Leads</span>
                    </div>
                    <h3 class="text-base font-bold text-white group-hover:text-indigo-400 transition">Dossiers Financement</h3>
                    <p class="text-slate-400 text-xs mt-1">Demandes de crédit auto et dossiers clients à valider.</p>
                </a>
            </div>
        </div>

        <!-- Section 2 : Grille des Pôles Métiers (Modules d'Administration) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

            <!-- Pôle 1 : Operations, Planning & RDV -->
            <div class="bg-slate-900 rounded-3xl border border-slate-800 p-6 space-y-4 flex flex-col justify-between">
                <div class="space-y-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                            <i class="fas fa-calendar-check text-lg"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-white text-base">Agenda & Clientèle</h3>
                            <p class="text-slate-400 text-xs">Gestion du flux client et interventions</p>
                        </div>
                    </div>
                    <div class="space-y-2 pt-2">
                        <a href="{% url 'directeur_app:rendez-vous-list' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-calendar-alt text-blue-400"></i> Planning des Rendez-vous</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                        <a href="{% url 'leads_app:documents-list' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-folder-open text-blue-400"></i> GED / Documents Client</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                        <a href="{% url 'commercial_app:maintenance-list' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-tools text-blue-400"></i> Suivi des Maintenances</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                    </div>
                </div>
            </div>

            <!-- Pôle 2 : Gestion du Parc Automobile -->
            <div class="bg-slate-900 rounded-3xl border border-slate-800 p-6 space-y-4 flex flex-col justify-between">
                <div class="space-y-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                            <i class="fas fa-car text-lg"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-white text-base">Parc & Flotte Auto</h3>
                            <p class="text-slate-400 text-xs">Inventaire des véhicules en vente et réparation</p>
                        </div>
                    </div>
                    <div class="space-y-2 pt-2">
                        <a href="{% url 'vehicul_app:list-vehicul' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-car-side text-emerald-400"></i> Catalogue Véhicules</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                        <a href="{% url 'vehicul_app:list-marque' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-trademark text-emerald-400"></i> Marques Constructeurs</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                        <a href="{% url 'vehicul_app:type-vehicul-list' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-layer-group text-emerald-400"></i> Types de Véhicules</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                    </div>
                </div>
            </div>

            <!-- Pôle 3 : Catalogue Produits & Services -->
            <div class="bg-slate-900 rounded-3xl border border-slate-800 p-6 space-y-4 flex flex-col justify-between">
                <div class="space-y-4">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                            <i class="fas fa-boxes text-lg"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-white text-base">Offre & Services</h3>
                            <p class="text-slate-400 text-xs">Pièces détachées, prestations & tarifs</p>
                        </div>
                    </div>
                    <div class="space-y-2 pt-2">
                        <a href="{% url 'products_app:products-list' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-box text-amber-400"></i> Liste des Produits</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                        <a href="{% url 'products_app:categorie-products-list' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-tags text-amber-400"></i> Catégories Produits</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                        <a href="{% url 'services_app:services-list' %}" class="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition text-xs font-medium text-slate-200 hover:text-white">
                            <span class="flex items-center gap-2"><i class="fas fa-wrench text-purple-400"></i> Catalogue des Services</span>
                            <i class="fas fa-chevron-right text-[10px] text-slate-500"></i>
                        </a>
                    </div>
                </div>
            </div>

        </div>

        <!-- Section 3 : Communication & Avis Clients (Image de Marque) -->
        <div class="bg-slate-900 rounded-3xl border border-slate-800 p-6 space-y-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                        <i class="fas fa-bullhorn text-lg"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-white text-base">Communication & Reputation Digital</h3>
                        <p class="text-slate-400 text-xs">Avis, témoignages clients et publications du site</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
                <a href="{% url 'home_app:actualites-list' %}" class="p-4 rounded-2xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition flex items-center justify-between text-xs font-semibold text-slate-200 hover:text-white">
                    <span class="flex items-center gap-2.5"><i class="fas fa-newspaper text-rose-400 text-base"></i> Actualités Site</span>
                    <i class="fas fa-arrow-up-right-from-square text-[10px] text-slate-500"></i>
                </a>
                <a href="{% url 'home_app:avis-reseau-list' %}" class="p-4 rounded-2xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition flex items-center justify-between text-xs font-semibold text-slate-200 hover:text-white">
                    <span class="flex items-center gap-2.5"><i class="fas fa-comment-dots text-pink-400 text-base"></i> Avis Réseaux</span>
                    <i class="fas fa-arrow-up-right-from-square text-[10px] text-slate-500"></i>
                </a>
                <a href="{% url 'home_app:video-temoignages-list' %}" class="p-4 rounded-2xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition flex items-center justify-between text-xs font-semibold text-slate-200 hover:text-white">
                    <span class="flex items-center gap-2.5"><i class="fas fa-video text-purple-400 text-base"></i> Témoignages Vidéo</span>
                    <i class="fas fa-arrow-up-right-from-square text-[10px] text-slate-500"></i>
                </a>
                <a href="{% url 'home_app:temoignages-textuel-list' %}" class="p-4 rounded-2xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800/80 transition flex items-center justify-between text-xs font-semibold text-slate-200 hover:text-white">
                    <span class="flex items-center gap-2.5"><i class="fas fa-quote-left text-cyan-400 text-base"></i> Avis Textuels</span>
                    <i class="fas fa-arrow-up-right-from-square text-[10px] text-slate-500"></i>
                </a>
            </div>
        </div>

    </main>

    <!-- Inclusions des Modales (100% de tes modales conservées) -->
    {% include 'modals/auth/change_password.html' %}
    {% include 'modals/auth/userregister.html' %}
    {% include 'modals/vehicul/aj_marque.html' %}
    {% include 'modals/vehicul/aj_vehicul.html' %}
    {% include 'modals/vehicul/aj_type_vehicul.html' %}
    {% include 'modals/services/aj_services.html' %}
    {% include 'modals/services/aj_type_services.html' %}
    {% include 'modals/products/create_categorie_product.html' %}
    {% include 'modals/products/create_products.html' %}
    {% include 'modals/products/create_product_unite.html' %}
    {% include 'modals/products/create_marque_product.html' %}
    {% include 'modals/home/avis_reseau_form.html' %}
    {% include 'modals/home/video_temoignage_form.html' %}
    {% include 'modals/actualite/actualite_form.html' %}

    <!-- Footer Cockpit -->
    <footer class="bg-slate-950 border-t border-slate-800/80 py-8 mt-16 text-slate-500 text-xs">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-2">
                <span class="font-bold text-white">KOZ SERVICES</span>
                <span>— System Executive v3.0</span>
            </div>
            <p>&copy; {% now "Y" %} KOZ Services. Tous droits réservés.</p>
        </div>
    </footer>

</body>
</html>