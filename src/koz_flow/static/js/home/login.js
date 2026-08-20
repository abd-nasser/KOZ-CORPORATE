// À placer dans le footer ou dans un fichier JS dédié
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');
    const loginBtn = document.getElementById('loginBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // 1️⃣ Récupérer les données du formulaire
            const email = document.getElementById('login_email').value.trim();
            const password = document.getElementById('login_password').value.trim();

            // 2️⃣ Validation de base
            if (!email || !password) {
                showLoginError('Veuillez remplir tous les champs.');
                return;
            }

            // 3️⃣ Construire le body pour l'API
            const body = {
                email: email,
                password: password
            };
            console.log('🔵 Body envoyé:', body);

            // 4️⃣ Désactiver le bouton
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> En cours...';
            loginError.classList.add('hidden');

            try {
                // 5️⃣ Envoyer la requête à l'API
                //const apiBase = window.location.origin;
                const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') || '',
                        
                    },
                    credentials: 'include',  // ← AJOUTE CETTE LIGNE !
                    body: JSON.stringify(body)
                });
            
                const data = await response.json();
                console.log('🔵 Réponse API:', data);
                console.log('🔵 Statut de la réponse:', data.user);
                console.log('🔵 Headers de la réponse:', response.headers);
                console.log('🔵 Statut de la réponse:', response.status);
                console.log('🔵 Statut de la réponse (ok):', response.ok);
                
                // 6️⃣ Traiter la réponse
                if (response.ok) {
                    // ✅ Connexion réussie
                    console.log('✅ Connexion réussie !');
                    // Stocker les tokens
                    localStorage.setItem('access', data.access);
                    localStorage.setItem('refresh', data.refresh);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    // Fermer le modal
                    document.getElementById('login_modal').close();

                    // Redirection
    
                    window.location.href = "/";
                    

                } else {
                    // ❌ Erreur API
                    const errorMsg = data.error || data.errors || 'Email ou mot de passe incorrect.';
                    showLoginError(errorMsg);
                }
            } catch (error) {
                console.error('❌ Erreur réseau:', error);
                showLoginError('Erreur de connexion au serveur. Veuillez réessayer.');
            } finally {
                // 7️⃣ Réactiver le bouton
                loginBtn.disabled = false;
                loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Se connecter';
            }
        });
    }

    // Fonction d'affichage d'erreur
    function showLoginError(message) {
        const loginError = document.getElementById('loginError');
        if (loginError) {
            loginError.textContent = message;
            loginError.classList.remove('hidden');
        }
    }

    // Fonction pour récupérer le cookie CSRF (si pas déjà définie)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});