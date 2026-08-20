

// ===== LIGHTBOX =====
        function openLightbox(src) {
            const lightbox = document.getElementById('lightbox');
            const img = document.getElementById('lightbox-img');
            if (lightbox && img) {
                img.src = src;
                lightbox.classList.remove('hidden');
                lightbox.classList.add('flex');
                document.body.style.overflow = 'hidden';
            }
        }

        function closeLightbox() {
            const lightbox = document.getElementById('lightbox');
            if (lightbox) {
                lightbox.classList.add('hidden');
                lightbox.classList.remove('flex');
                document.body.style.overflow = 'auto';
            }
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeLightbox();
        });

        // ===== SCROLL REVEAL (GSAP) =====
        document.addEventListener('DOMContentLoaded', function() {
            // Animation des cartes glass au scroll
            const cards = document.querySelectorAll('.glass-card');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, { threshold: 0.1 });

            cards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                card.style.transition = 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
                observer.observe(card);
            });
        });

// ============================================================
// GESTION DU SLIDE DIRECTIONNEL (avec sortie)
// ============================================================
document.addEventListener('htmx:beforeSwap', function(evt) {
    const container = document.getElementById('hero-image-container');
    const direction = evt.detail.requestConfig.parameters.direction;
    
    if (container && direction) {
        // Ajoute une classe de sortie sur l'image actuelle
        const currentImg = container.querySelector('img');
        if (currentImg) {
            currentImg.parentElement.classList.add(
                direction === 'right' ? 'animate-slide-out-left' : 'animate-slide-out-right'
            );
        }
    }
});

document.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.target.id === 'hero-image-container') {
        // Nettoie les classes de sortie après l'animation
        const container = evt.target;
        const wrapper = container.querySelector('div');
        if (wrapper) {
            wrapper.classList.remove('animate-slide-out-left', 'animate-slide-out-right');
        }
    }
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