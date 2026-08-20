// static/js/vehicule/vehicule_script.js

function init3DCards() {
    const cards = document.querySelectorAll(".card");
    
    cards.forEach(card => {
        // Éviter les doublons d'écouteurs (optionnel mais propre)
        if (card.dataset.initialized === "true") return;
        
        const inner = card.querySelector(".card-inner");
        const glow = card.querySelector(".glow");
        
        if (!inner) return;
        
        card.dataset.initialized = "true";
        
        card.addEventListener("mousemove", e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const midWidth = rect.width / 2;
            const midHeight = rect.height / 2;
            
            const angleY = (x - midWidth) / 8;
            const angleX = (y - midHeight) / 8;
            
            const glowX = (x / rect.width) * 100;
            const glowY = (y / rect.height) * 100;
            
            inner.style.transform = `rotateX(${angleX}deg) rotateY(${angleY}deg) scale(1.05)`;
            
            if (glow) {
                glow.style.background = `radial-gradient(circle at ${glowX}% ${glowY}%, rgb(180, 195, 210), rgba(0,0,0,0.6))`;
            }
        });
        
        card.addEventListener("mouseleave", () => {
            inner.style.transform = "rotateX(0) rotateY(0) scale(1)";
            if (glow) {
                glow.style.background = "radial-gradient(circle at 50% 0%, rgb(129, 141, 154), transparent)";
            }
        });
    });
}

// Initialisation au chargement initial
document.addEventListener("DOMContentLoaded", function() {
    init3DCards();
    
    // Création des particules (ton code existant)
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        for (let i = 0; i < 100; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + 'vw';
            particle.style.top = Math.random() * 100 + 'vh';
            const size = Math.random() * 10 + 5;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            const hue = Math.random() * 40 + 200;
            particle.style.backgroundColor = `hsla(${hue}, 80%, 65%, 0.3)`;
            particle.style.animationDuration = Math.random() * 20 + 10 + 's';
            particle.style.animationDelay = Math.random() * 5 + 's';
            particlesContainer.appendChild(particle);
        }
    }
});

// Réinitialisation après chaque échange HTMX
document.body.addEventListener("htmx:afterSwap", function(event) {
    // Vérifier si le nouveau contenu contient des cartes
    if (event.target.querySelector && event.target.querySelector(".card")) {
        init3DCards();
    }
});
