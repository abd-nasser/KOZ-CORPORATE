<div id="result-toast-container" class="result-toast-container"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<!-- ============================================================ -->
<!-- MODAL : GESTION DES STATUTS DE VENTE                         -->
<!-- ============================================================ -->
<dialog id="gestion_statut_vente_modal" class="modal">
    <div class="modal-box bg-white rounded-2xl shadow-2xl max-w-md w-full p-0 overflow-hidden">
        
        <!-- En-tête -->
        <div class="bg-gradient-to-r from-blue-700 to-indigo-800 px-6 py-4 flex justify-between items-center">
            <div>
                <h3 class="text-xl font-bold text-white flex items-center gap-2">
                    <i class="fas fa-exchange-alt"></i>
                    Gérer le statut
                </h3>
                <p class="text-blue-100 text-sm mt-0.5">Vente #{{ vente.id }}</p>
            </div>
            <button type="button" class="text-white/80 hover:text-white text-3xl leading-none transition" 
                    onclick="document.getElementById('gestion_statut_vente_modal').close()">×</button>
        </div>

        <!-- Corps -->
        <div class="p-6">
            
            <!-- Statut actuel -->
            <div class="bg-gray-50 rounded-xl p-4 mb-4 border border-gray-100">
                <p class="text-sm text-gray-500">Statut actuel</p>
                <p class="text-lg font-bold text-gray-800 flex items-center gap-2">
                    {% if vente.statut == 'conclue' or vente.statut == 'conclue_par_acceptation_offre_financement' or vente.statut == 'conclue_par_acceptation_offre_simple' %}
                        <i class="fas fa-check-circle text-green-500"></i>
                    {% elif vente.statut == 'perdue' or vente.statut == 'perdue_par_offre_refusee' or vente.statut == 'perdue_par_refus_offre_simple' or vente.statut == 'perdue_par_refus_offre_financement' %}
                        <i class="fas fa-times-circle text-red-500"></i>
                    {% elif vente.statut == 'en_cours' %}
                        <i class="fas fa-spinner text-yellow-500"></i>
                    {% else %}
                        <i class="fas fa-circle text-gray-400"></i>
                    {% endif %}
                    {{ vente.get_statut_display }}
                </p>
            </div>

            <!-- Formulaire -->
            <form method="post" action="{% url 'commercial_app:changer-statut-vente' vente.id %}" id="gestion-statut-form">
                {% csrf_token %}
                
                <div class="space-y-4">
                    <!-- Sélection du statut -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            <i class="fas fa-tag text-blue-500 mr-1"></i> Nouveau statut
                        </label>
                        <select name="statut" id="statut-select" class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-sm">
                            <optgroup label="✅ Ventes conclues">
                                <option value="conclue" {% if vente.statut == 'conclue' %}selected{% endif %}>Conclue</option>
                                <option value="conclue_par_acceptation_offre_simple" {% if vente.statut == 'conclue_par_acceptation_offre_simple' %}selected{% endif %}>Conclue par offre simple</option>
                                <option value="conclue_par_acceptation_offre_financement" {% if vente.statut == 'conclue_par_acceptation_offre_financement' %}selected{% endif %}>Conclue par offre financement</option>
                            </optgroup>
                            <optgroup label="❌ Ventes perdues">
                                <option value="perdue" {% if vente.statut == 'perdue' %}selected{% endif %}>Perdue</option>
                                <option value="perdue_par_refus_offre_simple" {% if vente.statut == 'perdue_par_refus_offre_simple' %}selected{% endif %}>Perdue par refus offre simple</option>
                                <option value="perdue_par_refus_offre_financement" {% if vente.statut == 'perdue_par_refus_offre_financement' %}selected{% endif %}>Perdue par refus offre financement</option>
                            </optgroup>
                            <optgroup label="⏳ Autres">
                                <option value="en_cours" {% if vente.statut == 'en_cours' %}selected{% endif %}>En cours</option>
                                <option value="gestion_de_status" {% if vente.statut == 'gestion_de_status' %}selected{% endif %}>Gérer l'état</option>
                                <option value="non_classifie" {% if vente.statut == 'non_classifie' %}selected{% endif %}>Non classifié</option>
                            </optgroup>
                        </select>
                    </div>

                    <!-- Message de confirmation -->
                    <div class="bg-blue-50 rounded-xl p-3 border border-blue-100">
                        <p class="text-xs text-blue-700 flex items-start gap-2">
                            <i class="fas fa-info-circle mt-0.5"></i>
                            <span>Le changement de statut sera enregistré immédiatement.</span>
                        </p>
                    </div>
                </div>

                <!-- Boutons -->
                <div class="flex gap-3 mt-6 pt-4 border-t border-gray-100">
                    <button type="submit" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl transition font-semibold flex items-center justify-center gap-2">
                        <i class="fas fa-save"></i> Enregistrer
                    </button>
                    <button type="button" class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-2.5 rounded-xl transition font-semibold"
                            onclick="document.getElementById('gestion_statut_vente_modal').close()">
                        <i class="fas fa-times mr-2"></i> Annuler
                    </button>
                </div>

            </form>
        </div>

    </div>

    <!-- Fond pour fermer par clic extérieur -->
    <form method="dialog" class="modal-backdrop">
        <button type="submit">fermer</button>
    </form>
</dialog>

<!-- Script pour rouvrir le modal si formulaire invalide -->
{% if open_gestion_statut_vente_modal %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('gestion_statut_vente_modal').showModal();
    });
</script>
{% endif %}


<!-- ============================================================ -->
<!-- SECTION : POURQUOI CHOISIR KOZ SERVICES                      -->
<!-- ============================================================ -->
<section class="py-16 sm:py-20 relative bg-white overflow-hidden">
    
    <!-- Dégradé de fond subtil -->
    <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-0 right-0 w-96 h-96 bg-blue-50/50 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 w-96 h-96 bg-indigo-50/50 rounded-full blur-3xl"></div>
    </div>

    <div class="container relative z-10 mx-auto px-4 max-w-6xl">
        
        <!-- ===== EN-TÊTE ===== -->
        <div class="text-center mb-12 animate-fade-in-up">
            <span class="inline-block text-xs font-semibold text-blue-600 uppercase tracking-[0.2em] bg-blue-50 px-5 py-2 rounded-full mb-4 border border-blue-100">
                ✦ Pourquoi nous ?
            </span>
            <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800">
                Pourquoi choisir <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">KOZ Services</span>
            </h2>
            <div class="w-20 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 mx-auto mt-4 rounded-full"></div>
            <p class="text-gray-500 mt-4 max-w-2xl mx-auto text-sm sm:text-base">
                Une expérience automobile unique, transparente et à votre écoute.
            </p>
        </div>

        <!-- ===== GRILLE DES RAISONS ===== -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            
            <!-- Raison 1 : Expertise automobile -->
            <div class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100/50 hover:border-blue-200">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/25 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        <i class="fas fa-wrench text-xl text-white"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 text-lg">Expertise automobile</h3>
                    </div>
                </div>
                <p class="text-gray-500 text-sm leading-relaxed pl-1">
                    Une équipe de passionnés avec des années d'expérience dans le secteur automobile. Des conseils avisés pour vous guider vers le meilleur choix.
                </p>
                <div class="mt-4 flex items-center gap-2 text-blue-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span>En savoir plus</span>
                    <i class="fas fa-arrow-right text-xs"></i>
                </div>
            </div>

            <!-- Raison 2 : Inspection professionnelle -->
            <div class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100/50 hover:border-blue-200">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center shadow-lg shadow-emerald-500/25 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        <i class="fas fa-search text-xl text-white"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 text-lg">Inspection professionnelle</h3>
                    </div>
                </div>
                <p class="text-gray-500 text-sm leading-relaxed pl-1">
                    Chaque véhicule est inspecté par nos experts pour garantir sa fiabilité et sa sécurité. Une transparence totale sur l'état du véhicule.
                </p>
                <div class="mt-4 flex items-center gap-2 text-emerald-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span>En savoir plus</span>
                    <i class="fas fa-arrow-right text-xs"></i>
                </div>
            </div>

            <!-- Raison 3 : Véhicule contrôlé -->
            <div class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100/50 hover:border-blue-200">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/25 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        <i class="fas fa-clipboard-check text-xl text-white"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 text-lg">Véhicule contrôlé</h3>
                    </div>
                </div>
                <p class="text-gray-500 text-sm leading-relaxed pl-1">
                    Tous nos véhicules passent un contrôle technique rigoureux avant la mise en vente. Vous achetez en toute confiance.
                </p>
                <div class="mt-4 flex items-center gap-2 text-amber-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span>En savoir plus</span>
                    <i class="fas fa-arrow-right text-xs"></i>
                </div>
            </div>

            <!-- Raison 4 : Conseils honnêtes -->
            <div class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100/50 hover:border-blue-200">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center shadow-lg shadow-purple-500/25 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        <i class="fas fa-handshake text-xl text-white"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 text-lg">Conseils honnêtes</h3>
                    </div>
                </div>
                <p class="text-gray-500 text-sm leading-relaxed pl-1">
                    Pas de vente forcée, pas de mauvaises surprises. Nous vous donnons des conseils sincères pour que vous fassiez le bon choix.
                </p>
                <div class="mt-4 flex items-center gap-2 text-purple-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span>En savoir plus</span>
                    <i class="fas fa-arrow-right text-xs"></i>
                </div>
            </div>

            <!-- Raison 5 : Assistance jusqu'à l'achat -->
            <div class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100/50 hover:border-blue-200">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-rose-500 to-rose-700 flex items-center justify-center shadow-lg shadow-rose-500/25 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        <i class="fas fa-headset text-xl text-white"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 text-lg">Assistance jusqu'à l'achat</h3>
                    </div>
                </div>
                <p class="text-gray-500 text-sm leading-relaxed pl-1">
                    Nous vous accompagnons à chaque étape : du choix du véhicule à la finalisation de l'achat. Une équipe dédiée à votre service.
                </p>
                <div class="mt-4 flex items-center gap-2 text-rose-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span>En savoir plus</span>
                    <i class="fas fa-arrow-right text-xs"></i>
                </div>
            </div>

            <!-- Raison 6 : Clients satisfaits (bonus) -->
            <div class="group bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100/50 hover:border-blue-200">
                <div class="flex items-center gap-4 mb-3">
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-700 flex items-center justify-center shadow-lg shadow-cyan-500/25 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                        <i class="fas fa-smile text-xl text-white"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 text-lg">Clients satisfaits</h3>
                    </div>
                </div>
                <p class="text-gray-500 text-sm leading-relaxed pl-1">
                    La satisfaction de nos clients est notre priorité. Rejoignez la communauté des conducteurs KOZ Services.
                </p>
                <div class="mt-4 flex items-center gap-2 text-cyan-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <span>En savoir plus</span>
                    <i class="fas fa-arrow-right text-xs"></i>
                </div>
            </div>

        </div>

        <!-- ===== BANDEAU CTA ===== -->
        <div class="mt-12 p-6 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-center shadow-xl">
            <p class="text-white text-base md:text-lg font-medium leading-relaxed max-w-3xl mx-auto">
                <i class="fas fa-quote-left text-blue-200/50 mr-2"></i>
                Passez Nous rendre visite et trouvez la voiture de vos rêves, avec un service qui vous accompagne à chaque étape.
                <i class="fas fa-quote-right text-blue-200/50 ml-2"></i>
            </p>
        </div>

    </div>
</section>

<!-- ============================================================ -->
<!-- SECTION : TÉMOIGNAGES & RÉSEAUX SOCIAUX                     -->
<!-- ============================================================ -->
<section class="py-16 sm:py-20 relative bg-gradient-to-br from-gray-50 to-white overflow-hidden">
    
    <!-- Dégradé de fond -->
    <div class="absolute inset-0 pointer-events-none">
        <div class="absolute top-0 right-0 w-96 h-96 bg-blue-50/30 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 w-96 h-96 bg-indigo-50/30 rounded-full blur-3xl"></div>
    </div>

    <div class="container relative z-10 mx-auto px-4 max-w-7xl">
        
        <!-- ===== EN-TÊTE ===== -->
        <div class="text-center mb-12">
            <span class="inline-block text-xs font-semibold text-blue-600 uppercase tracking-[0.2em] bg-blue-50 px-5 py-2 rounded-full mb-4 border border-blue-100">
                💬 Ils parlent de nous
            </span>
            <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800">
                Ce que disent nos <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">clients</span>
            </h2>
            <p class="text-gray-500 mt-3 max-w-2xl mx-auto text-sm sm:text-base">
                Des avis authentiques de clients satisfaits et des retours sur les réseaux sociaux.
            </p>
        </div>

        <!-- ===== TÉMOIGNAGES (scroll horizontal) ===== -->
        <div class="mb-12">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
                    <i class="fas fa-star text-yellow-500"></i> Témoignages clients
                </h3>
                <span class="text-sm text-gray-400">{{ temoignages|length }} avis</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {% for temoignage in temoignages|slice:":6" %}
                <div class="bg-white rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100">
                    <div class="flex items-center gap-3 mb-3">
                        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                            {% if temoignage.photo %}
                                <img src="{{ temoignage.photo.url }}" alt="{{ temoignage.prenom }}" class="w-full h-full rounded-full object-cover">
                            {% else %}
                                {{ temoignage.prenom|slice:":1" }}{{ temoignage.nom|slice:":1" }}
                            {% endif %}
                        </div>
                        <div>
                            <p class="font-semibold text-gray-800">{{ temoignage.prenom }} {{ temoignage.nom }}</p>
                            <div class="text-yellow-500 text-sm">
                                {% for i in "12345"|make_list %}
                                    {% if forloop.counter <= temoignage.note %}★{% else %}☆{% endif %}
                                {% endfor %}
                            </div>
                        </div>
                        <span class="ml-auto text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
                            {{ temoignage.get_source_display }}
                        </span>
                    </div>
                    <p class="text-gray-600 text-sm leading-relaxed">"{{ temoignage.message|truncatechars:120 }}"</p>
                </div>
                {% empty %}
                <p class="col-span-full text-center text-gray-400">Aucun témoignage pour le moment.</p>
                {% endfor %}
            </div>
        </div>

        <!-- ===== RÉSEAUX SOCIAUX (grille d'avis) ===== -->
        <div class="mb-12">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
                    <i class="fas fa-share-alt text-blue-500"></i> Sur les réseaux sociaux
                </h3>
                <span class="text-sm text-gray-400">{{ avis_reseaux|length }} avis</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                {% for avis in avis_reseaux|slice:":8" %}
                <div class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition border border-gray-100">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="text-lg">
                            {% if avis.reseau == 'facebook' %}
                                <i class="fab fa-facebook text-blue-600"></i>
                            {% elif avis.reseau == 'instagram' %}
                                <i class="fab fa-instagram text-pink-600"></i>
                            {% elif avis.reseau == 'google' %}
                                <i class="fab fa-google text-red-500"></i>
                            {% elif avis.reseau == 'whatsapp' %}
                                <i class="fab fa-whatsapp text-green-500"></i>
                            {% elif avis.reseau == 'twitter' %}
                                <i class="fab fa-twitter text-blue-400"></i>
                                {% elif avis.reseau == 'tiktok' %}
                                <i class="fab fa-tiktok text-black"></i>
                            {% else %}
                                <i class="fas fa-share-alt text-gray-500"></i>
                            {% endif %}
                        </span>
                        <span class="text-xs font-medium text-gray-600">{{ avis.nom_utilisateur }}</span>
                        <span class="ml-auto text-[10px] text-gray-400">{{ avis.date_publication|date:"d/m/Y" }}</span>
                    </div>
                    {% if avis.image %}
                        <img src="{{ avis.image.url }}" alt="Avis" class="w-full h-20 object-cover rounded-lg mb-2">
                    {% endif %}
                    <p class="text-xs text-gray-500 line-clamp-3">{{ avis.message|truncatechars:60 }}</p>
                </div>
                {% empty %}
                <p class="col-span-full text-center text-gray-400">Aucun avis sur les réseaux sociaux.</p>
                {% endfor %}
            </div>
        </div>

        <!-- ===== VIDÉOS ===== -->
        <div>
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
                    <i class="fas fa-video text-red-500"></i> Vidéos
                </h3>
                <span class="text-sm text-gray-400">{{ videos|length }} vidéos</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {% for video in videos|slice:":6" %}
                <div class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100">
                    <!-- Vidéo -->
                    <div class="relative aspect-video bg-gray-900 overflow-hidden">
                        {% if video.video_file %}
                            <video class="w-full h-full object-cover" poster="{% if video.thumbnail %}{{ video.thumbnail.url }}{% endif %}" controls>
                                <source src="{{ video.video_file.url }}" type="video/mp4">
                                Votre navigateur ne supporte pas la vidéo.
                            </video>
                        {% elif video.video_url %}
                            <iframe class="w-full h-full" src="{{ video.video_url }}" frameborder="0" allowfullscreen></iframe>
                        {% elif video.embed_code %}
                            {{ video.embed_code|safe }}
                        {% else %}
                            <div class="w-full h-full flex items-center justify-center bg-gray-800">
                                <i class="fas fa-video text-4xl text-gray-600"></i>
                            </div>
                        {% endif %}
                        
                        <!-- Badge durée -->
                        {% if video.duree %}
                        <div class="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-md">
                            {{ video.duree_formatee }}
                        </div>
                        {% endif %}
                        
                        <!-- Bouton play (overlay) -->
                        <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <div class="w-14 h-14 rounded-full bg-white/90 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                                <i class="fas fa-play text-blue-600 text-xl ml-1"></i>
                            </div>
                        </div>
                    </div>
                    <!-- Infos -->
                    <div class="p-4">
                        <h4 class="font-semibold text-gray-800 text-sm">{{ video.titre }}</h4>
                        <p class="text-xs text-gray-500 mt-1 line-clamp-2">{{ video.description|truncatechars:60 }}</p>
                    </div>
                </div>
                {% empty %}
                <p class="col-span-full text-center text-gray-400">Aucune vidéo disponible.</p>
                {% endfor %}
            </div>
        </div>

    </div>
</section>
    
    
    
    
    
    <!-- ============================================================ -->
    <!-- SECTION MISSION ET VALEURS                                   -->
    <!-- ============================================================ -->
    <section class="section_mission_valeurs relative bg-white py-20  overflow-hidden">

        <!-- ===== EN-TÊTE ===== -->
        <div class="text-center mb-16">
            <span class="inline-block text-xs font-semibold text-blue-600 uppercase tracking-[0.2em] bg-blue-50 px-5 py-2 rounded-full mb-4 border border-blue-100">
                ✦ Notre ADN
            </span>
            <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800">
                Mission & <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Valeurs</span>
            </h2>
            <div class="w-20 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 mx-auto mt-4 rounded-full"></div>
        </div>
        <!-- ===== CONTENEUR GAUCHE ET DROITE ===== -->
        <div class="left_and_right-conatiner min-w-full min-h-150">

                <!-- ===== CONTENEUR GAUCHE ===== -->
            <div class="left_container w-3xl min-h-100 ">
                
                <div class="relative p-8 shadow-lg  hover:shadow-2xl transition duration-500 bg-white/10 backdrop-blur-md" 
                     style="width: 30rem;">
                    <div class="flex items-center gap-4 mb-6">
                        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/25">
                            <i class="fas fa-flag text-2xl text-white"></i>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">Notre Mission</h3>
                            <p class="text-sm text-gray-400">Ce qui nous anime chaque jour</p>
                        </div>
                    </div>
                    
                    <p class="text-gray-600 leading-relaxed text-lg">
                        Chez <strong class="text-blue-600">KOZ Services</strong>, nous croyons que chaque 
                        personne mérite de rouler en toute sérénité. Notre mission est de 
                        <strong class="text-gray-800">rendre l'accession à la voiture plus simple, 
                        plus transparente et plus humaine</strong>, grâce à des solutions de 
                        financement flexibles et un accompagnement personnalisé.
                    </p>
                    
                    <div class="mt-6 pt-6 border-t border-gray-100 flex items-center gap-4">
                        <div class="flex items-center gap-2 text-sm text-gray-500">
                            <i class="fas fa-check-circle text-green-500"></i>
                            <span>Accessibilité</span>
                        </div>
                        <div class="flex items-center gap-2 text-sm text-gray-500">
                            <i class="fas fa-check-circle text-green-500"></i>
                            <span>Transparence</span>
                        </div>
                        <div class="flex items-center gap-2 text-sm text-gray-500">
                            <i class="fas fa-check-circle text-green-500"></i>
                            <span>Proximité</span>
                        </div>
                    </div>
               
            </div>
        </div>

            <!-- ===== CONTENEUR DROITE ===== -->
<div class="right_container w-full max-w-2xl lg:max-w-3xl">

    <!-- ===== TITRE VALEURS ===== -->
    <div class="mb-4 shadow-lg hover:shadow-2xl transition duration-500 bg-white/10 p-4 sm:p-5 backdrop-blur-md rounded-2xl">
        <div class="flex items-center gap-4">
            <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 flex-shrink-0">
                <i class="fas fa-heart text-xl sm:text-2xl text-white"></i>
            </div>
            <div>
                <h3 class="text-lg sm:text-xl font-bold text-gray-800">Nos Valeurs</h3>
                <p class="text-xs sm:text-sm text-gray-400">Ce qui nous guide au quotidien</p>
            </div>
        </div>
    </div>

    <!-- ===== GRILLE DES VALEURS ===== -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        
        <!-- Valeur 1 -->
        <div class="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 shadow-lg hover:shadow-2xl transition duration-500 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:border-blue-400/30 group">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition">
                <i class="fas fa-handshake text-blue-600 text-sm sm:text-base"></i>
            </div>
            <div>
                <h4 class="font-semibold text-gray-800 text-sm sm:text-base">1. La Confiance</h4>
                <p class="text-xs sm:text-sm text-gray-500 leading-relaxed">Bâtir une relation durable basée sur la transparence et l'intégrité.</p>
            </div>
        </div>

        <!-- Valeur 2 -->
        <div class="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 shadow-lg hover:shadow-2xl transition duration-500 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:border-blue-400/30 group">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition">
                <i class="fas fa-bolt text-blue-600 text-sm sm:text-base"></i>
            </div>
            <div>
                <h4 class="font-semibold text-gray-800 text-sm sm:text-base">2. L'Innovation</h4>
                <p class="text-xs sm:text-sm text-gray-500 leading-relaxed">Des solutions simples et modernes pour simplifier l'achat.</p>
            </div>
        </div>

        <!-- Valeur 3 -->
        <div class="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 shadow-lg hover:shadow-2xl transition duration-500 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:border-blue-400/30 group">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition">
                <i class="fas fa-users text-blue-600 text-sm sm:text-base"></i>
            </div>
            <div>
                <h4 class="font-semibold text-gray-800 text-sm sm:text-base">3. La Proximité</h4>
                <p class="text-xs sm:text-sm text-gray-500 leading-relaxed">À l'écoute et accompagner nos clients à chaque étape.</p>
            </div>
        </div>

        <!-- Valeur 4 -->
        <div class="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 shadow-lg hover:shadow-2xl transition duration-500 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:border-blue-400/30 group">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition">
                <i class="fas fa-shield-alt text-blue-600 text-sm sm:text-base"></i>
            </div>
            <div>
                <h4 class="font-semibold text-gray-800 text-sm sm:text-base">4. La Sécurité</h4>
                <p class="text-xs sm:text-sm text-gray-500 leading-relaxed">Des transactions sécurisées et des conseils fiables.</p>
            </div>
        </div>

    </div>

</div>
                
        </div>
       
    </section>
<div class="scroll-area">
    <div class="content-block">🚗 BIENVENUE CHEZ KOZ SERVICES</div>
    <div class="content-block">💳 CRÉDIT SANS BANQUE</div>
    <div class="content-block">🌍 DIASPORA, COMMANDEZ ICI</div>
    
    <div  class="content-block  ">
        <a href="#">📞 Catalogue</a></div>
</div>

<div class="frame-container">
    <img id="frame" src="{% static 'frames/frame-0001.jpg' %}" alt="">
</div>

<script>
    gsap.registerPlugin(ScrollTrigger);

    // REMPLACE PAR LE NOMBRE EXACT D'IMAGES
    const totalFrames = 120; // ← À MODIFIER !
    const basePath = "{% static 'frames/frame-' %}";
    const frameImg = document.getElementById('frame');

    ScrollTrigger.create({
        trigger: "body",
        start: "top top",
        end: "bottom bottom",
        scrub: 0.8,
        onUpdate: (self) => {
            let frameIndex = Math.floor(self.progress * (totalFrames - 1)) + 1;
            frameIndex = Math.min(frameIndex, totalFrames);
            const paddedIndex = String(frameIndex).padStart(4, '0');
            frameImg.src = `${basePath}${paddedIndex}.jpg`;
        }
    });
</script>


<!-- templates/includes/navbar.html -->
<nav class="navbar bg-base-100 shadow-md fixed top-0 z-50 w-full border-b border-gray-200/20 backdrop-blur-sm bg-white/80">
    <div class="container mx-auto px-4 flex justify-between items-center">
        
        <!-- Logo -->
        <div class="flex items-center gap-2">
            <div class="w-15 h-15 bg-gradient-to-br from-white to-blue-600 rounded-xl flex items-center justify-center shadow-md">
                <img src="{% static 'images/koz_logo_noBack.png' %}" alt="Logo" class="text-white font-bold text-xl">
            </div>
            <span class="text-xl font-bold text-gray-800 hidden sm:inline">KOZ Services</span>
        </div>

        <!-- Liens (centraux) -->
        <div class="hidden md:flex gap-6 text-gray-600 font-medium">
            <a href="#" class="hover:text-blue-600 transition">Accueil</a>
            <a href="#" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">A propos</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
        </div>

        <!-- Boutons droite -->
        <div class="flex items-center gap-3">
            {% if user.is_authenticated %}
                <a href="{% url 'client_app:client-view' %}" class="hidden sm:inline-block text-sm text-gray-600 hover:text-blue-600 transition">
                    <i class="fas fa-user mr-1"></i> Espace client
                </a>
                <button id="logoutBtn" class="btn btn-error btn-sm text-white">
                    <i class="fas fa-sign-out-alt"></i> Déconnexion
                </button>
            {% else %}
                <button onclick="document.getElementById('login_modal').showModal()" 
                        class="btn btn-ghost btn-sm hidden sm:inline-block">
                    Connexion
                </button>
                <button onclick="document.getElementById('register_modal').showModal()" 
                        class="btn bg-blue-600 btn-sm text-white">
                    <i class="fas fa-user-plus"></i> Inscription
                </button>
            {% endif %}
        </div>

        <!-- Menu burger (mobile) -->
        <div class="md:hidden">
            <button id="burgerBtn" class="btn btn-ghost btn-sm">
                <i class="fas fa-bars text-xl"></i>
            </button>
        </div>
    </div>

    <!-- Menu mobile (caché par défaut) -->
    <div id="mobileMenu" class="hidden md:hidden bg-white border-t border-gray-200 p-4">
        <div class="flex flex-col gap-3 text-gray-600">
            <a href="#" class="hover:text-blue-600">Accueil</a>
            <a href="#" class="hover:text-blue-600">Catalogue</a>
            <a href="#" class="hover:text-blue-600">Financement</a>
            <a href="#" class="hover:text-blue-600">A propos</a>
            <a href="#" class="hover:text-blue-600">Contact</a>
        </div>
    </div>
</nav>

<script>
    document.getElementById('burgerBtn')?.addEventListener('click', function() {
        const menu = document.getElementById('mobileMenu');
        menu.classList.toggle('hidden');
    });
</script>



<div class="absolute top-10 left-10 w-72 h-72 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-10 right-10 w-96 h-96 bg-blue-400 rounded-full blur-3xl"></div>
    

    {% load static %}
{% load tailwind_tags %}
{% load humanize %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    {% tailwind_css %}
    <title>KOZ Services - Votre voiture à crédit, vos pièces en ligne</title>
    <link rel="stylesheet" href="{% static 'css/home/home_style.css' %}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>

<!-- ========== NAVBAR ========== -->
<nav class="navbar bg-white/80 backdrop-blur-md shadow-sm fixed top-0 z-50 w-full border-b border-gray-200/40">
    <div class="container mx-auto px-4 flex justify-between items-center h-16">
        
        <!-- Logo -->
        <div class="flex items-center gap-3">
            <a href="{% url 'home_app:home-page' %}" class="flex items-center gap-2">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-md">
                    <img src="{% static 'images/koz_logo_noBack.png' %}" alt="KOZ" class="w-8 h-8 object-contain">
                </div>
                <span class="text-xl font-bold text-gray-800 hidden sm:inline">KOZ Services</span>
            </a>
        </div>

        <!-- Liens centraux -->
        <div class="hidden md:flex gap-6 text-gray-600 font-medium text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-4">
            {% if user.is_authenticated %}
                <a href="{% url 'client_app:client-view' %}" class="hidden sm:flex items-center gap-2 text-sm text-gray-700 hover:text-blue-600 transition font-medium">
                    <i class="fas fa-user-circle text-lg text-blue-600"></i>
                    {{ user.nom_complet }}
                </a>

                <a href="#" class="relative text-gray-700 hover:text-blue-600 transition">
                    <i class="fas fa-shopping-cart text-lg"></i>
                    <span class="absolute -top-2 -right-3 bg-blue-600 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full shadow-md">
                        {{ user.panier.nb_articles|default:0 }}
                    </span>
                </a>

                <button id="logoutBtn" class="btn btn-error btn-sm text-white hover:bg-red-700 transition shadow-sm flex items-center gap-1.5">
                    <i class="fas fa-sign-out-alt text-xs"></i>
                    <span class="hidden sm:inline">Déconnexion</span>
                </button>
            {% else %}
                <button onclick="document.getElementById('login_modal').showModal()" class="btn btn-ghost btn-sm hidden sm:inline-block hover:bg-gray-100">
                    Connexion
                </button>
                <button onclick="document.getElementById('register_modal').showModal()" class="btn btn-sm bg-blue-600 hover:bg-blue-700 text-white shadow-md flex items-center gap-2">
                    <i class="fas fa-user-plus"></i>
                    <span class="hidden sm:inline">Inscription</span>
                </button>
            {% endif %}

            <button id="burgerBtn" class="md:hidden btn btn-ghost btn-sm">
                <i class="fas fa-bars text-xl"></i>
            </button>
        </div>
    </div>

    <!-- Menu mobile -->
    <div id="mobileMenu" class="hidden md:hidden bg-white border-t border-gray-200 p-4 shadow-lg">
        <div class="flex flex-col gap-3 text-gray-600 text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
            <hr>
            <a href="#" class="text-blue-600 font-medium">
                <i class="fas fa-shopping-cart mr-2"></i> Panier ({{ user.panier.nb_articles|default:0 }})
            </a>
        </div>
    </div>
</nav>
<!-- ========== HERO IMMERSIVE (fond fixe) ========== -->
<div class="frame-container">
    <img id="frame" src="{% static 'frames/frame-0001.jpg' %}" alt="">
</div>

<section class="hero-section relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
    <!-- Ta navbar (déjà en fixed, ok) -->
    <!-- Ton contenu hero avec le titre et les boutons -->
    <div class="container mx-auto px-4 text-center text-white relative z-10">
        <h1 class="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Votre voiture à crédit.<br>
            <span class="text-blue-200">Vos pièces en ligne.</span>
        </h1>
        <p class="text-xl md:text-2xl text-blue-100 max-w-2xl mx-auto mb-8">
            KOZ Services vous accompagne dans l'achat de votre véhicule...
        </p>
        <div class="flex flex-wrap justify-center gap-4">
            <a href="#" class="btn btn-white btn-lg text-blue-700 hover:bg-blue-50 shadow-lg">
                Découvrir le catalogue
            </a>
            <a href="#" class="btn btn-outline btn-lg text-white border-white/50 hover:bg-white/10">
                Demander un financement
            </a>
        </div>
    </div>
</section>


<!-- ========== SECTION VÉHICULES EN VEDETTE ========== -->
<section class="py-16  bg-gray-50">
    <div class="container  mx-auto px-4">
        <div class="text-center  mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Nos véhicules en vedette</h2>
            <p class="text-gray-500 mt-2">Découvrez notre sélection de véhicules disponibles</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {% for vehicule in vehicules_vedette %}
            <div class="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition group">
                <div class="h-48 overflow-hidden">
                    <img src="{{ vehicule.image_principale.url }}" alt="{{ vehicule.marque.nom }} {{ vehicule.modele }}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                </div>
                <div class="p-4">
                    <h3 class="font-bold text-gray-800">{{ vehicule.marque.nom }} {{ vehicule.modele }}</h3>
                    <p class="text-sm text-gray-500">{{ vehicule.annee }} • {{ vehicule.kilometrage|intcomma }} km</p>
                    <p class="text-lg font-bold text-blue-600 mt-2">{{ vehicule.prix|intcomma }} FCFA</p>
                    <a href="{% url 'vehicul_app:detail-vehicul' vehicule.pk %}" class="btn btn-primary btn-sm w-full mt-3">Voir le détail</a>
                </div>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun véhicule disponible pour le moment.</p>
            {% endfor %}
        </div>
        <div class="text-center mt-8">
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="btn btn-outline btn-primary">Voir tout le catalogue</a>
        </div>
    </div>
</section>

<!-- ========== SECTION PRODUITS EN VEDETTE ========== -->
<section class="py-16 bg-white">
    <div class="container mx-auto px-4">
        <div class="text-center mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Pièces et accessoires</h2>
            <p class="text-gray-500 mt-2">L'équipement qu'il vous faut pour votre véhicule</p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            {% for produit in produits_vedette %}
            <div class="bg-gray-50 rounded-xl p-4 text-center hover:shadow-md transition">
                <div class="w-full h-32 bg-gray-200 rounded-lg mb-3 overflow-hidden">
                    <img src="{{ produit.image_principale.url }}" alt="{{ produit.nom }}" class="w-full h-full object-cover">
                </div>
                <h4 class="font-semibold text-gray-800">{{ produit.nom }}</h4>
                <p class="text-blue-600 font-bold">{{ produit.prix|intcomma }} FCFA</p>
                <button class="btn btn-primary btn-sm w-full mt-2">Ajouter au panier</button>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun produit disponible.</p>
            {% endfor %}
        </div>
    </div>
</section>

<!-- ========== CTA FINAL ========== -->
<section class="py-16 bg-gradient-to-r from-blue-700 to-indigo-800 text-white">
    <div class="container mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">Prêt à rouler avec KOZ ?</h2>
        <p class="text-blue-100 text-lg mb-6">Créez votre compte et faites votre demande de financement en quelques minutes.</p>
        <button onclick="document.getElementById('register_modal').showModal()" class="btn btn-white btn-lg text-blue-700 hover:bg-blue-50 shadow-lg">
            <i class="fas fa-user-plus mr-2"></i> Créer un compte
        </button>
    </div>
</section>

<!-- ========== FOOTER ========== -->
<footer class="bg-gray-800 text-gray-400 py-8">
    <div class="container mx-auto px-4 text-center text-sm">
        <p>&copy; {% now "Y" %} KOZ Services. Tous droits réservés.</p>
        <p class="mt-1">Conçu avec ❤️ pour les passionnés d'automobile.</p>
    </div>
</footer>

<!-- ========== MODALES ========== -->
{% include 'modals/home/register.html' %}
{% include 'modals/home/login.html' %}

<!-- ========== SCRIPTS ========== -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
<script src="{% static 'js/home/register.js' %}"></script>
<script src="{% static 'js/home/login.js' %}"></script>
<script src="{% static 'js/home/logout.js' %}"></script>

<script>
    gsap.registerPlugin(ScrollTrigger);

    const totalFrames = 120;
    const basePath = "{% static 'frames/frame-' %}";
    const frameImg = document.getElementById('frame');

    ScrollTrigger.create({
        trigger: ".hero-section",   // ← Le déclencheur
        start: "top top",           // Début du scroll
        end: "bottom bottom",       // Fin du scroll
        scrub: 0.8,
        onUpdate: (self) => {
            let frameIndex = Math.floor(self.progress * (totalFrames - 1)) + 1;
            frameIndex = Math.min(frameIndex, totalFrames);
            const paddedIndex = String(frameIndex).padStart(4, '0');
            frameImg.src = `${basePath}${paddedIndex}.jpg`;
        }
    });

    // Faire apparaître les sections avec un fondu
const sections = document.querySelectorAll('.fade-section');
sections.forEach((section, index) => {
    gsap.from(section, {
        scrollTrigger: {
            trigger: section,
            start: "top 80%",
            toggleActions: "play none none none"
        },
        opacity: 0,
        y: 50,
        duration: 1,
        delay: index * 0.15
    });
});
</script>

<script>
    // Burger menu
    document.getElementById('burgerBtn')?.addEventListener('click', function() {
        document.getElementById('mobileMenu').classList.toggle('hidden');
    });
</script>

</body>
</html>







{% load static %}
{% load tailwind_tags %}
{% load humanize %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    {% tailwind_css %}
    <title>KOZ Services - Votre voiture à crédit, vos pièces en ligne</title>
    <link rel="stylesheet" href="https://unpkg.com/splitting/dist/splitting.css" />
    <link rel="stylesheet" href="{% static 'css/home/home_style.css' %}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>

<!-- ========== NAVBAR ========== -->
<nav class="navbar bg-white/80 backdrop-blur-md shadow-sm fixed top-0 z-50 w-full border-b border-gray-200/40">
    <div class="container mx-auto px-4 flex justify-between items-center h-16">
        
        <!-- Logo -->
        <div class="flex items-center gap-3">
            <a href="{% url 'home_app:home-page' %}" class="flex items-center gap-2">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-md">
                    <img src="{% static 'images/koz_logo_noBack.png' %}" alt="KOZ" class="w-8 h-8 object-contain">
                </div>
                <span class="text-xl font-bold text-gray-800 hidden sm:inline">KOZ Services</span>
            </a>
        </div>

        <!-- Liens centraux -->
        <div class="hidden md:flex gap-6 text-gray-600 font-medium text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-4">
            {% if user.is_authenticated %}
                <a href="{% url 'client_app:client-view' %}" class="hidden sm:flex items-center gap-2 text-sm text-gray-700 hover:text-blue-600 transition font-medium">
                    <i class="fas fa-user-circle text-lg text-blue-600"></i>
                    {{ user.nom_complet }}
                </a>

                <a href="#" class="relative text-gray-700 hover:text-blue-600 transition">
                    <i class="fas fa-shopping-cart text-lg"></i>
                    <span class="absolute -top-2 -right-3 bg-blue-600 text-white text-[10px] font-bold w-5 h-5 flex items-center justify-center rounded-full shadow-md">
                        {{ user.panier.nb_articles|default:0 }}
                    </span>
                </a>

                <button id="logoutBtn" class="btn btn-error btn-sm text-white hover:bg-red-700 transition shadow-sm flex items-center gap-1.5">
                    <i class="fas fa-sign-out-alt text-xs"></i>
                    <span class="hidden sm:inline">Déconnexion</span>
                </button>
            {% else %}
                <button onclick="document.getElementById('login_modal').showModal()" class="btn btn-ghost btn-sm hidden sm:inline-block hover:bg-gray-100">
                    Connexion
                </button>
                <button onclick="document.getElementById('register_modal').showModal()" class="btn btn-sm bg-blue-600 hover:bg-blue-700 text-white shadow-md flex items-center gap-2">
                    <i class="fas fa-user-plus"></i>
                    <span class="hidden sm:inline">Inscription</span>
                </button>
            {% endif %}

            <button id="burgerBtn" class="md:hidden btn btn-ghost btn-sm">
                <i class="fas fa-bars text-xl"></i>
            </button>
        </div>
    </div>

    <!-- Menu mobile -->
    <div id="mobileMenu" class="hidden md:hidden bg-white border-t border-gray-200 p-4 shadow-lg">
        <div class="flex flex-col gap-3 text-gray-600 text-sm">
            <a href="{% url 'home_app:home-page' %}" class="hover:text-blue-600 transition">Accueil</a>
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="hover:text-blue-600 transition">Catalogue</a>
            <a href="#" class="hover:text-blue-600 transition">Financement</a>
            <a href="#" class="hover:text-blue-600 transition">Contact</a>
            <hr>
            <a href="#" class="text-blue-600 font-medium">
                <i class="fas fa-shopping-cart mr-2"></i> Panier ({{ user.panier.nb_articles|default:0 }})
            </a>
        </div>
    </div>
</nav>
<!-- ========== HERO IMMERSIVE (fond fixe) ========== -->
<div class="frame-container">
    <img id="frame" src="{% static 'frames/frame-0001.jpg' %}" alt="">
</div>

<section class="hero-section fade-section relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
    <div class="container mx-auto px-4 text-center text-white relative z-10">
        <h1 class="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Votre voiture à crédit.<br>
            <span class="text-blue-200">Vos pièces en ligne.</span>
        </h1>
        <p class="text-xl md:text-2xl text-blue-100 max-w-2xl mx-auto mb-8">
            KOZ Services vous accompagne dans l'achat de votre véhicule, avec des solutions de financement simples et rapides.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
            <a href="#" class="btn btn-white btn-lg text-blue-700 hover:bg-blue-50 shadow-lg">
                Découvrir le catalogue
            </a>
            <a href="#" class="btn btn-outline btn-lg text-white border-white/50 hover:bg-white/10">
                Demander un financement
            </a>
        </div>

        <!-- ========== TEXTE QUI SE DÉVOILE ========== -->
        <div class="mt-16 max-w-3xl mx-auto">
            <p class="text-lg text-blue-100/80 font-light reveal-text" data-splitting>
                Des véhicules de qualité, un financement accessible, un accompagnement personnalisé.
                <br><span class="text-blue-200 font-medium">KOZ Services, votre partenaire automobile.</span>
            </p>
        </div>
    </div>
</section>

<!-- ========== CONTENU SUIVANT (scrollable) ========== -->
<div class="relative z-10 bg-white">

    <!-- ========== SECTION VÉHICULES EN VEDETTE ========== -->
    <section class=" py-16 section-vehicule fade-section ">
       
        <div class="container  mx-auto px-4">
        <div class="text-center  mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Nos véhicules en vedette</h2>
            <p class="text-gray-500 mt-2">Découvrez notre sélection de véhicules disponibles</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {% for vehicule in vehicules_vedette %}
            <div class="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition group">
                <div class="h-48 overflow-hidden">
                    <img src="{{ vehicule.image_principale.url }}" alt="{{ vehicule.marque.nom }} {{ vehicule.modele }}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                </div>
                <div class="p-4">
                    <h3 class="font-bold text-gray-800">{{ vehicule.marque.nom }} {{ vehicule.modele }}</h3>
                    <p class="text-sm text-gray-500">{{ vehicule.annee }} • {{ vehicule.kilometrage|intcomma }} km</p>
                    <p class="text-lg font-bold text-blue-600 mt-2">{{ vehicule.prix|intcomma }} FCFA</p>
                    <a href="{% url 'vehicul_app:detail-vehicul' vehicule.pk %}" class="btn btn-primary btn-sm w-full mt-3">Voir le détail</a>
                </div>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun véhicule disponible pour le moment.</p>
            {% endfor %}
        </div>
        <div class="text-center mt-8">
            <a href="{% url 'vehicul_app:list-vehicul' %}" class="btn btn-outline btn-primary">Voir tout le catalogue</a>
        </div>
    </div>
    </section>

    <!-- ========== SECTION PRODUITS EN VEDETTE ========== -->
    <section class="py-16 section-produits fade-section bg-white">
     
        <div class="container mx-auto px-4">
        <div class="text-center mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-800">Pièces et accessoires</h2>
            <p class="text-gray-500 mt-2">L'équipement qu'il vous faut pour votre véhicule</p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            {% for produit in produits_vedette %}
            <div class="bg-gray-50 rounded-xl p-4 text-center hover:shadow-md transition">
                <div class="w-full h-32 bg-gray-200 rounded-lg mb-3 overflow-hidden">
                    <img src="{{ produit.image_principale.url }}" alt="{{ produit.nom }}" class="w-full h-full object-cover">
                </div>
                <h4 class="font-semibold text-gray-800">{{ produit.nom }}</h4>
                <p class="text-blue-600 font-bold">{{ produit.prix|intcomma }} FCFA</p>
                <button class="btn btn-primary btn-sm w-full mt-2">Ajouter au panier</button>
            </div>
            {% empty %}
            <p class="text-gray-400 col-span-full text-center">Aucun produit disponible.</p>
            {% endfor %}
        </div>
        </div>
    </section>
    
    <section class="py-16  fade-section bg-gradient-to-r from-blue-700 to-indigo-800 text-white">
        
         
    </section>

    <!-- ========== FOOTER ========== -->
    <footer class="bg-gray-800 text-gray-400 py-8">
        <div class="container mx-auto px-4 text-center text-sm">
        <p>&copy; {% now "Y" %} KOZ Services. Tous droits réservés.</p>
        <p class="mt-1">Conçu avec ❤️ pour les passionnés d'automobile.</p>
        </div>
    </footer>
</div>

<!-- ========== MODALES ========== -->
{% include 'modals/home/register.html' %}
{% include 'modals/home/login.html' %}

<!-- ========== SCRIPTS ========== -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
<script src="https://unpkg.com/splitting/dist/splitting.min.js"></script>
<script src="{% static 'js/home/register.js' %}"></script>
<script src="{% static 'js/home/login.js' %}"></script>
<script src="{% static 'js/home/logout.js' %}"></script>

<script>
    gsap.registerPlugin(ScrollTrigger);

// ========== 1. HERO FRAMES ==========
const totalFrames = 76;
const basePath = "{% static 'frames/ECO_SYS_PROJECTKoz_Flowsrckoz_flowstaticframesframe-' %}";
const frameImg = document.getElementById('frame');

ScrollTrigger.create({
    trigger: ".hero-section",
    start: "top top",
    end: "bottom bottom",
    scrub: 0.8,
    onUpdate: (self) => {
        let frameIndex = Math.floor(self.progress * (totalFrames - 1)) + 1;
        frameIndex = Math.min(frameIndex, totalFrames);
        const paddedIndex = String(frameIndex).padStart(4, '0');
        frameImg.src = `${basePath}${paddedIndex}.jpg`;
    }
});

// ========== 2. SPLITTING : TEXTE QUI S'ÉCRIT AU SCROLL ==========
let splits = Splitting({ target: '.reveal-text' });

splits.forEach(split => {
    const chars = split.chars;
    
    gsap.from(chars, {
        scrollTrigger: {
            trigger: split.el,
            start: "top 80%",
            toggleActions: "play none none reverse",
        },
        opacity: 0,
        y: 40,
        rotationX: -20,
        duration: 1.2,
        ease: "back.out(1.7)",
        stagger: {
            amount: 1.2,
            from: "start"
        }
    });
});

// ========== 3. FADE-IN DES SECTIONS ==========
const sections = document.querySelectorAll('.fade-section');
sections.forEach((section, index) => {
    gsap.from(section, {
        scrollTrigger: {
            trigger: section,
            start: "top 80%",
            toggleActions: "play none none none",
        },
        opacity: 0,
        y: 60,
        duration: 1,
        delay: index * 0.15,
        ease: "power3.out"
    });
});
</script>

<script>
    // Burger menu
    document.getElementById('burgerBtn')?.addEventListener('click', function() {
        document.getElementById('mobileMenu').classList.toggle('hidden');
    });
</script>

</body>
</html>


Le W-586 est le pneu hiver d'Ovation développé pour les véhicules de tourisme.
- Améliore le freinage, l'adhérence en courbe ainsi que l'évacuation de l'eau et de la neige fondue
- Traction d'excellent niveau et résistance au roulement réduite
- Améliore l'évacuation de l'eau et la stabilité par forte neige
- Offre une excellente adhérence et réduit la friction ainsi que la résistance au roulement


 <script>
    // ============================================================
    // 1. Gestion de la déconnexion
    // ============================================================
    document.getElementById('logoutBtn').addEventListener('click', async () => {
        const accessToken = localStorage.getItem('access');
        const refreshToken = localStorage.getItem('refresh');
        
        // Si refresh token présent, on le blacklist
        if (refreshToken && accessToken) {
            try {
                await fetch('/api/auth/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({refresh: refreshToken})  // ✅ Envoie REFRESH
                });
            } catch (e) {
                console.warn('Logout serveur échoué:', e);
            }
        }
        
        // Nettoyage local
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user');
        window.location.href = '/';
    });

    // ============================================================
    // 2. Rafraîchissement du token access
    // ============================================================
    async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh');
    if (!refreshToken) return false;
    
    try {
        const response = await fetch('/api/auth/token/refresh/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({refresh: refreshToken})
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access', data.access);
            
            // ✅ Stocke le NOUVEAU refresh token
            if (data.refresh) {
                localStorage.setItem('refresh', data.refresh);
            }
            return true;
        }
        return false;
    } catch (error) {
        console.error('Refresh failed:', error);
        return false;
    }
}
    // ============================================================
    // 3. Vérification périodique du token (toutes les 60s)
    // ============================================================
    setInterval(async () => {
        const token = localStorage.getItem('access');
        if (!token) {
            window.location.href = '/';
            return;
        }
        
        try {
            const response = await fetch('/api/auth/me/', {
                headers: {'Authorization': `Bearer ${token}`}
            });
            
            if (response.status === 401) {
                const refreshed = await refreshToken();
                if (!refreshed) {
                    localStorage.clear();
                    window.location.href = '/';
                }
            }
        } catch (error) {
            console.error('Erreur vérification token:', error);
        }
    }, 60000); // 60 secondes
</script>


import django
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse


#REST_FRAMEWORK
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

#MODELS
from .models import Paiement
from order_app.models import Commande

#PACKAGE
import json
import hashlib
import hmac
import requests
import logging

logger = logging.getLogger(__name__)



class ApiPaiementView(APIView):
    """ 
    API pour initier un paiement via LigdiCASH (Orange Money BF),
    POST /api/paiements/Initier
    
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1️⃣ Récuperer les données du clients
        commande_id = request.data.get("commande_id")
        telephone = request.data.get("telephone")
        otp = request.data.get('otp')
        montant = request.data.get('montant')
        
        
        # 2️⃣ Vérification de base
        if not all([commande_id, telephone, otp, montant]):
            return Response({"error":"commande_id, telephone, otp, montant sont requis"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 3️⃣ Vérifier que la commande existe et appartient au client
        commande  = get_object_or_404(Commande,
                                      id=commande_id,
                                      panier__client=request.user
                                      )
        
        
        # 4️⃣ Vérifier que le montant correspond
        if int(montant) != commande.panier.total_panier():
            return Response({"error":"Le montant ne correspond pas au total du panier"}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
        
        # 5️⃣Construire le payload Ligdicash
        payload = {
            "commande":{
                "invoice":{
                    "total_amount": int(montant),
                    "devise": "XOF",
                    "description":f"Commande KOZ SERVICES #{commande.id}",
                    "customer":telephone,
                    "customer_firstname":request.user.nom_complet.split[0] if request.user.nom_complet else "Client",
                    "customer_lasttname":request.user.nom_complet.split[1] if request.user.nom_complet else "KOZ",
                    "customer_email":request.user.email,
                    "otp":otp
                },
                "store":{
                    "name":"KOZ Services",
                    "website_url":"https//www.koz-corporate.pro"
                },
                "actions":{
                    "callback_url": request.build.absolute_uri(
                        reverse("paiement_app:callback-ligdicash")
                        )
                },
                "custom_data":{
                    "commande_id":commande.id,
                    "client_id": request.user.id,
                }
            }
        }
        
        # 6️⃣ Envoyer la requet à Ligdicash
        try:
            response = requests.post(
                "https://app.ligdicash.com/pay/v01/straight/checkout-invoice/create",
                headers={
                    "Apikey":settings.LIGDICASH_API_KEY,
                    "Authorization":f'Bearer {settings.LIGDICASH_API_TOKEN}',
                    "Accept":"application/json",
                    "Content-Type":"application/json"
                },
                json=payload,
                timeout=30
                )
            data = response.json()
            if response.status_code == 200 and data.get('response_code') == '00':
                # 7️⃣ Créer le transaction en base
                paiement = Paiement.objects.create(
                    commande=commande,
                    client = request.user,
                    token = data.get('token'),
                    statut= "en_attente"
                )
                
                return Response({
                    "message":"Paiement initié avec succès",
                    "token": data.get("token"),
                    "paiement_id": paiement.id,
                    "status": paiement.statut,
                    "response_text": data.get("response_text"), 
                }, status=status.HTTP_200_OK)
            else:
                # Erreur Ligdicash
                return Response({
                    "error":data.get('response_text', "Erreur inconnue"),
                    "code": data.get("response_code"),
                    
                }, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.Timeout:
            return Response({
                "error":"le paiement à expiré. Veuillez réessayer"
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        except Exception as e:
            return Response({
                "error":f"Erreur serveur: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                

 # Token csrf impossible
@require_POST
def callback_ligdicash(request):
    """
    Webhook reçu de ligdicash pour confirmer le paiement,
    Ligdicash envoie une requete Post à cette URL 
    
    """
    try:
        #1️⃣ Récuperer le payload JSON
        payload = json.loads(request.body)
        logger.info(f"Callback reçu de ligdiCash: {payload}")
        
        #2️⃣ Extraire les données essentielles
        token = payload.get("token"),
        status = payload.get("status"),
        transaction_id = payload.get('transaction_id')
        montant = payload.get("amount")
        
        #3️⃣ Vérifier que le token existe
        if not token :
            logger.error("Callback sans token")
            return JsonResponse({"error":"Token manquant"}, status=400)
        
        #4️⃣ Récupere le paiement correspondant
        paiement = get_object_or_404(Paiement, token=token)
        
        #5️⃣ Verification de sécurité : le montant doit correspondre
        if montant and int(montant) != paiement.montant:
            logger.error(f"Montant incoherent: reçu {montant}, attendu {paiement.montant}")
            return JsonResponse({"error":"Montant incohérent"}, status=400)
        
        #6️⃣ Verification de sécurité: la commande est bien liée
        commande = paiement.commande
        if not commande:
            return JsonResponse({"error":"commande introuvable"}, status=400)
        
        #7️⃣ Mettre à jour le statut du paiement
        if status == 'success':
            paiement.statut = "reussi"
            paiement.ligdicash_transaction_id = transaction_id
            paiement.methode = "mobile_ligdicash"
            paiement.save()
            
            # ✅ Mettre à jour la commande
            commande.statut = "payee"
            commande.save()
            logger.info(f'✅ Paiement {paiement.id} confirmé pour la commande {commande.id}')

            send_mail(
                subject="Paiement confirmé",
                message=f"Votre paiement pour la commande {commande.id} a été confirmé.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commande.panier.client.email],
            )
            
            return JsonResponse({
                "message":"Paiement confirmé",
                "paiement_id": paiement.id,
                "commande_id": commande.id,
                "status": paiement.statut
            })
            
        elif status == 'failed':
            paiement.statut = "echec" 
            paiement.save()
            logger.warning(f'❌ Paiement {paiement.id} échoué pour la commande {commande.id}')
            return JsonResponse({
                "message":"Paiement échoué",
                "paiement_id": paiement.id,
                "commande_id": commande.id,
                "status": paiement.statut
            })
        else:
            logger.warning(f'⚠️ Callback reçu avec un statut inconnu: {status}')
            return JsonResponse({
                "message":"Statut inconnu",
                "paiement_id": paiement.id,
                "commande_id": commande.id,
                "status": paiement.statut
            })
    except json.JSONDecodeError:
        logger.error("Payload JSON invalide")
        return JsonResponse({"error":"Payload JSON invalide"}, status=400)  
            
            
    except Exception as e:
        logger.exception(f"Erreur lors du traitement du callback: {str(e)}")
        return JsonResponse({"error":f"Erreur serveur: {str(e)}"}, status=500)
    
    
    
def verifier_signature(request, payload):
    """
    Vérifie que le callback vient bien de LigdiCash.
    La signature est généralement dans un header X-Signature.
    """
    signature = request.headers.get('X-Signature')
    if not signature:
        logger.warning("Aucune signature dans le callback")
        return False

    # Générer la signature avec la clé secrète
    secret = settings.LIGDICASH_SECRET_KEY
    computed = hmac.new(
        secret.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, signature)




        gsap.registerPlugin(ScrollTrigger);

        // Faire apparaître les sections avec un fondu
        const sections = document.querySelectorAll(".fade-section-actualité");
        sections.forEach((section, index) => {
            gsap.from(section, {
                scrollTrigger: {
                    trigger: section,
                    start: "top 80%",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 50,
                duration: 1,
                delay: index * 0.15
            });
        });

        

        gsap.from(".fade-text",  {
                scrollTrigger: {
                    trigger: ".services-section",
                    start: "top -210%",
                    end: "top -150%",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

        gsap.from(".services-contain",  {
                scrollTrigger: {
                    trigger: ".services-section",
                    start: "top -230%",
                    end: "top -150%",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

        gsap.from(".fade-section", {
                scrollTrigger: {
                    trigger: ".fade-section",
                    start: "top -500%",
                    end: "top -150%",
                    toggleActions: "play none none reverse",
                   
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

        gsap.from(".fade-hero-contain", {
                scrollTrigger: {
                    trigger: ".hero-section",
                    toggleActions: "play none none reverse"
                },
                opacity: 0,
                y: 100,
                duration: 1.5,
            
            });


        // NAVBAR PREMIUM
        // ============================================
        const navbar = document.querySelector('.navbar');

        // 1. Apparition au scroll (pure JS)
        window.addEventListener('scroll', () => {
            if (window.scrollY > 30) {
                navbar.classList.add('visible');
            } else {
                navbar.classList.remove('visible');
            }
            
            // Fond qui s'intensifie
            if (window.scrollY > 200) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });

        // 2. Survol (pour rendre plus réactif)
        navbar.addEventListener('mouseenter', () => {
            navbar.classList.add('visible');
        });

        navbar.addEventListener('mouseleave', () => {
            navbar.classList.remove('visible');
        });


        // ============================================
        // BOXES LATÉRALES : apparition au scroll
        // ============================================
        gsap.registerPlugin(ScrollTrigger);

        // Box 1 : vient de gauche
        gsap.from(".box-left", {
            scrollTrigger: {
                trigger: ".trigger-box",
                start: "top 50%" ,
                end: "top 10%",
                scrub: 1.2,
                toggleActions: "play none none reverse",
                id: "box-left"
            },
            x: -300,
            opacity: 0,
            rotationY: 8,
            duration: 1.5,
            ease: "power3.out"
            
        });

        // Box 2 : vient de droite
        gsap.from(".box-right", {
            scrollTrigger: {
                trigger: ".trigger-box",
                start: "top 30%",
                end: "bottom",
                scrub: 1.2,
                toggleActions: "play none none reverse",
                id: "box-right"
            },
            x: 300,
            opacity: 0,
            rotationX: 8,
            duration: 1.5,
            ease: "power3.out",
            

        });

        // Box 3 : vient du bas
        gsap.from(".box-bottom", {
            scrollTrigger:{
                trigger: ".box-right",
                start: "top 50%",
                end:"bottom 50%",
                scrub: 1.2,
                toggleActions: "play none none reverse",
                id: "box-bottom"

            },
            y: 300,
            opacity: 0,
            rotationX: 8,
            duration: 1.5,
            ease: "power3.out",
        });


        // GSAP text-nouveau et details
        gsap.from(".text-nouveau", {
                    scrollTrigger:{
                        trigger: ".campaign-card",
                        start: "top 65%",
                        end: "top 45%",
                        toggleActions: "play none none reverse",
                    },
                    opacity: 0,
                    x: 300,
                    duration: 2,
                    ease: "power3.out"
                });


        // --- ÉTAPE 2 : PIN DE LA SECTION (le scroll reste bloqué) ---
        ScrollTrigger.create({
            trigger: ".pin-trigger",
            start: "top 9%",
            end: "+=300%",  // La section reste "épinglée" pendant 300% de la hauteur d'écran
            pin: true,
            pinSpacing: true,

        });


                
        // ============================================
        // CARTES ACTUALITÉS : apparition au scroll
        // ============================================
        // 2. Définir campaignCards
        const campaignCards = document.querySelectorAll('.campaign-card');
                gsap.from('.campaign-card',{
                    scrollTrigger: {
                        trigger: ".actualite-containt",
                        start: "top 60%",
                        end: "top 50%",
                        toggleActions: "play none none reverse",
                    },
                    opacity: 0,
                    x: -300,
                    duration: 1.5,
                    ease: "power3.out"
                });
        
            // Animation de survol supplémentaire (flottement)
            campaignCards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    gsap.to(card, {
                        y: -8,
                        duration: 0.4,
                        ease: "power2.out"
                    });
                });
                card.addEventListener('mouseleave', () => {
                    gsap.to(card, {
                        y: 0,
                        duration: 0.4,
                        ease: "power2.out"
                    });
                });
            });




gsap.registerPlugin(ScrollTrigger);

        // 1️⃣ Splitting pour découper les caractères
       let selection = Splitting();
        console.log(selection)
        // 2️⃣ Animation GSAP
        gsap.from(selection[0].chars, {
            y : 100,
            scaleY:0,
            rotation: 90,
            color: "rgb(255,255,255)",
            stagger: 0.05,
            opacity:0,
            scrollTrigger:{
                trigger :".pin-trigger",
                start :"top 9%",
                end: '+=250%',
                scrub: true,
            }
            
        });

// ============================================================
// SERVICES – PINNED SCROLL ANIMATION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    
    gsap.registerPlugin(ScrollTrigger);

    const services = document.querySelectorAll('.service-item');
    const totalServices = services.length;
    
    if (totalServices === 0) return;
    console.log('Total services:', totalServices);

    // Éléments à mettre à jour
    const mainImage = document.getElementById('services-main-image');
    const step = document.getElementById('services-step');
    const typeBadge = document.getElementById('services-type-badge');
    const title = document.getElementById('services-title');
    const description = document.getElementById('services-description');
    const price = document.getElementById('services-price');
    const link = document.querySelector('.services-link');
    const dots = document.querySelectorAll('.services-dot');

    // 1️⃣ Récupérer les données du premier service
    const firstData = services[0]?.querySelector('.service-item-data');
    if (firstData) {
        mainImage.src = firstData.dataset.image;
        step.textContent = `01 / ${String(totalServices).padStart(2, '0')}`;
        typeBadge.textContent = `${firstData.dataset.type}`;
        title.textContent = firstData.dataset.title;
        description.textContent = firstData.dataset.description;
        price.textContent = firstData.dataset.price;
        if (link) link.href = firstData.dataset.link;
    }

    // ============================================================
    // 2️⃣ PIN TRIGGER : la section reste fixe
    // ============================================================
    ScrollTrigger.create({
        trigger: ".services-section",
        start: "top 8%",
        end: "+=300%",  // ← Plus de hauteur pour voir tous les services
        pin: true,
        pinSpacing: true,
        // ← Passe à false après test
    });

    // ============================================================
    // 3️⃣ UPDATE TRIGGERS : chaque service change le contenu
    // ============================================================
    services.forEach((service, index) => {
        const data = service.querySelector('.service-item-data');
        if (!data) return;

        ScrollTrigger.create({
            trigger: service,  // ← LE SERVICE, PAS LE LIEN !
            start: "top center",
            end: "center center",
            onEnter: () => updateService(index),
            onEnterBack: () => updateService(index),
           
            
        }
      
    );


    });

    // ============================================================
    // 4️⃣ FONCTION DE MISE À JOUR
    // ============================================================
    function updateService(index) {
        const data = services[index].querySelector('.service-item-data');
        if (!data) return;

        // Mettre à jour l'image avec fade
        gsap.to(mainImage, {
            opacity: 0,
            duration: 0.4,
            onComplete: () => {
                mainImage.src = data.dataset.image;
                gsap.to(mainImage, { opacity: 1, duration: 0.4 });
            }
        });

        // Mettre à jour les textes
        step.textContent = `${String(index + 1).padStart(2, '0')} / ${String(totalServices).padStart(2, '0')}`;
        typeBadge.textContent = `🔧 ${data.dataset.type}`;
        title.textContent = data.dataset.title;
        description.textContent = data.dataset.description;
        price.textContent = data.dataset.price;
        if (link) link.href = data.dataset.link;

        // Mettre à jour les dots
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
    }
});


// ============================================================
// ANIMATION : TYPES DE VÉHICULES (ESCALIER PREMIUM)
// ============================================================
document.addEventListener('DOMContentLoaded', function() {

   
    gsap.registerPlugin(ScrollTrigger);


     // ============================================================
    // 2️⃣ PIN TRIGGER : la section reste fixe
    // ============================================================
   // ScrollTrigger.create({
      //  trigger: ".section_type_vehicul",
      //  start: "top 8%",
       // end: "+=80%",  // ← Plus de hauteur pour voir tous les services
     //   pin: true,
     //   pinSpacing: true,
        // ← Passe à false après test
   // });
    

    // ===== SUV (vient de la gauche) =====
    gsap.from(".suv", {
        x: -200,           // Vient de la gauche
        opacity: 0,
        scale: 0.8,
        rotation: -8,      // Légère rotation
        duration: 1.2,
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".suv",
            start: "top 85%",
            end: "top 40%",
            toggleActions: "play none none reverse",
              // ← Passe à false après test
        }
    });

    // ===== BERLINE (vient du centre) =====
    gsap.from(".berline", {
        y: 80,             // Monte du bas
        opacity: 0,
        scale: 0.9,
        rotation: 2,
        duration: 1.2,
        delay: 0.15,       // Un peu après le SUV
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".berline",
            start: "center 85%",
            end: "top 40%",
            toggleActions: "play none none reverse",
            
        }
    });

    // ===== TRUCK (vient de la droite) =====
    gsap.from(".truck", {
        x: 200,            // Vient de la droite
        opacity: 0,
        scale: 0.8,
        rotation: 8,
        duration: 1.2,
        delay: 0.3,        // Dernier à apparaître
        ease: "power3.out",
        scrollTrigger: {
            trigger: ".truck",
            start: "bottom 85%",
            end: "top 40%",
            toggleActions: "play none none reverse",
            
        }
    });

     gsap.from(".text-anim",{
            x: -150,
            opacity: 0,
            duration: 1.2,
            ease: "power3.out",
        scrollTrigger: {
            trigger: ".truck",
            start: "bottom 80%",
            end: "top 40%",
            toggleActions: "play none none reverse",
            
        }

    });

     gsap.from(".fleche_anim",{
            x: -400,
            opacity: 0,
            duration: 1.5,
            ease: "power3.out",
        scrollTrigger: {
            trigger: ".truck",
            start: "bottom 80%",
            end: "top 40%",
            toggleActions: "play none none reverse",
           
        }

    });

});

// ============================================================
// ANIMATION : GALLERY DE VÉHICULES VEDETTE
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".fade-gallery", {
                scrollTrigger: {
                    trigger: ".section_vehicule_vedette",
                    start: "top 60%",
                    end: "top 40%",
                    toggleActions: "play none none reverse", 
                },
                opacity: 0,
                y: 100,
                duration: 1,
            
            });

});

// ============================================================
// STAT ANIME – COUNTER ANIMATION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    
    const stats = document.querySelectorAll('.stat-number');
    
    if (stats.length === 0) return;
    
    // Fonction d'animation du compteur
    function animateCounter(el) {
        const target = parseInt(el.getAttribute('data-target'));
        const duration = 2000; // 2 secondes
        const startTime = performance.now();
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // easing cubic-out
            
            const currentValue = Math.floor(eased * target);
            el.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                el.textContent = target.toLocaleString();
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
    
    // Utiliser IntersectionObserver pour déclencher l'animation
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                animateCounter(el);
                observer.unobserve(el); // Une seule fois
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => observer.observe(stat));
});



// Initialize a new Lenis instance for smooth scrolling
const lenis = new Lenis();

// Synchronize Lenis scrolling with GSAP's ScrollTrigger plugin
lenis.on('scroll', ScrollTrigger.update);

// Add Lenis's requestAnimationFrame (raf) method to GSAP's ticker
// This ensures Lenis's smooth scroll animation updates on each GSAP tick
gsap.ticker.add((time) => {
  lenis.raf(time * 500); // Convert time from seconds to milliseconds
});

// Disable lag smoothing in GSAP to prevent any delay in scroll animations
gsap.ticker.lagSmoothing(0);