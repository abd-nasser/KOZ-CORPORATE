// ============================================================
// 1. Gestion de la déconnexion (version robuste)
// ============================================================
(function initLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (!logoutBtn) return; // Sortie silencieuse si bouton absent
    
    logoutBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        
        const accessToken = localStorage.getItem('access');
        const refreshToken = localStorage.getItem('refresh');
        
        // Blacklist du refresh token côté serveur
        if (refreshToken && accessToken) {
            try {
                await fetch('/api/auth/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({refresh: refreshToken})
                });
            } catch (err) {
                console.warn('Logout serveur:', err.message);
            }
        }
        
        // Nettoyage local
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user');
        
        // Redirection propre
        window.location.href = '/';
    });
})();