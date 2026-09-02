
gsap.registerPlugin(ScrollTrigger);


// ============================================
// NAVBAR PREMIUM
// ============================================
document.addEventListener('DOMContentLoaded', function() {
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
 })




// ============================================
// ANIMATION HERO SEXTION
// ============================================
        
 document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".hero_fade", {
                opacity: 0,
                y: 200,
                duration: 1.5,
            
            });

});
      
// Animation autonome des deux box
document.addEventListener('DOMContentLoaded', function() {
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        
        // 1. Box Droite (apparaît d'abord)
        gsap.from("#hero-box-right", {
            x: 200,
            opacity: 0,
            duration: 1,
            ease: "power3.out",
            scrollTrigger: {
                trigger: "#hero-box-right",
                start: "top 85%", // Se déclenche quand la box arrive vers le bas de l'écran
                toggleActions: "play none none reverse"
            }
        });

        // 2. Box Gauche (apparaît un peu plus tard au scroll)
        gsap.from("#hero-box-left", {
            x: -200,
            opacity: 0,
            duration: 1,
            ease: "power3.out",
            scrollTrigger: {
                trigger: "#hero-box-left",
                start: "top 75%", // Se déclenche quand on descend un peu plus
                toggleActions: "play none none reverse"
            }
        });

    }
});
        
// ============================================================
// ACTUALITES ANIMATIONS GSAP
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    
    // Vérification de la présence des plugins
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
    
    gsap.registerPlugin(ScrollTrigger);

    // Animation du titre principal de section
    gsap.from(".informes", {
        scrollTrigger: {
            trigger: ".actualite_sec",
            start: "top 80%",
            toggleActions: "play none none reverse"
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: "power2.out"
    });

    // Timeline Colonne Gauche (Hero Média)
    const heroTl = gsap.timeline({
        scrollTrigger: {
            trigger: ".act-hero",
            start: "top 75%",
            toggleActions: "play none none reverse"
        }
    });

    heroTl.from(".act-hero", {
        opacity: 0,
        x: -40,
        duration: 0.9,
        ease: "power3.out"
    })
    .from([".actu_type", ".actu_vedette"], {
        opacity: 0,
        y: -15,
        stagger: 0.1,
        duration: 0.4,
        ease: "power2.out"
    }, "-=0.4")
    .from([".actu_titre", ".actu_mini_descript"], {
        opacity: 0,
        y: 20,
        stagger: 0.12,
        duration: 0.5,
        ease: "power2.out"
    }, "-=0.2");

    // Timeline Colonne Droite (Description + Galerie)
    const rightTl = gsap.timeline({
        scrollTrigger: {
            trigger: ".actu_descript",
            start: "top 75%",
            toggleActions: "play none none reverse"
        }
    });

    rightTl.from(".actu_descript", {
        opacity: 0,
        x: 40,
        duration: 0.8,
        ease: "power3.out"
    })
    gsap.from(".actu-img-galerie > div" , {
    scrollTrigger: {
        trigger: ".actu-img-galerie", // Ou le conteneur parent de ta galerie
        start: "top 85%",
        toggleActions: "play none none reverse"
    },
    autoAlpha: 0,       // Remplace opacity: 0 pour éviter les glitches
    y: 20,
    scale: 0.9,
    stagger: 0.1,
    duration: 0.5,
    ease: "back.out(1.4)",
    clearProps: "all"   // Supprime le style inline à la fin
});
});

  
// ============================================================
// SERVICES – PINNED SCROLL ANIMATION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {

    gsap.from(".service-fade", {
                scrollTrigger: {
                    trigger: ".services-section",
                    start: "top 60%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                    
                },
                opacity: 0,
                y: 200,
                duration: 1,
                ease: "power3.out",
                
                
            });

   
    
  
});



// ============================================================
// ANIMATION : TYPES DE VÉHICULES (ESCALIER PREMIUM)
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.registerPlugin(ScrollTrigger);

    let mm = gsap.matchMedia();

    // ==========================================
    // 💻 DESKTOP (≥ 768px) : EFFET ARC EN ÉVENTAIL
    // ==========================================
    mm.add("(min-width: 768px)", () => {
        
        // 1ère carte (ex: SUV - vient de la gauche)
        gsap.from(".type-card:nth-child(1)", {
            x: -180,
            opacity: 0,
            scale: 0.85,
            rotation: -12,
            duration: 1.2,
            ease: "power3.out",
            scrollTrigger: {
                trigger: ".type-contain",
                start: "top 80%",
                toggleActions: "play none none reverse"
            }
        });

        // 2ème carte (ex: Berline - monte du bas)
        gsap.from(".type-card:nth-child(2)", {
            y: 100,
            opacity: 0,
            scale: 0.85,
            duration: 1.2,
            delay: 0.15,
            ease: "power3.out",
            scrollTrigger: {
                trigger: ".type-contain",
                start: "top 80%",
                toggleActions: "play none none reverse"
            }
        });

        // 3ème carte (ex: Truck - vient de la droite)
        gsap.from(".type-card:nth-child(3)", {
            x: 180,
            opacity: 0,
            scale: 0.85,
            rotation: 12,
            duration: 1.2,
            delay: 0.3,
            ease: "power3.out",
            scrollTrigger: {
                trigger: ".type-contain",
                start: "top 80%",
                toggleActions: "play none none reverse"
            }
        });

        // Bouton CTA
        gsap.from(".text-anim", {
            y: 40,
            opacity: 0,
            duration: 1,
            ease: "power3.out",
            scrollTrigger: {
                trigger: ".type-contain",
                start: "bottom 85%",
                toggleActions: "play none none reverse"
            }
        });

        // Flèche
        gsap.from(".fleche_anim", {
            x: -100,
            opacity: 0,
            duration: 1.2,
            ease: "power3.out",
            scrollTrigger: {
                trigger: ".text-anim",
                start: "top 90%",
                toggleActions: "play none none reverse"
            }
        });
    });

    // ==========================================
    // 📱 MOBILE (< 768px) : ALIGNÉ EN COLONNE
    // ==========================================
    mm.add("(max-width: 767px)", () => {
        
        // Anime toutes les cartes en cascade (stagger) sans rotation ni overflow
        gsap.from(".type-card", {
            y: 50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "power2.out",
            scrollTrigger: {
                trigger: ".type-contain",
                start: "top 85%",
                toggleActions: "play none none reverse"
            }
        });

        gsap.from(".text-anim", {
            y: 30,
            opacity: 0,
            duration: 0.8,
            scrollTrigger: {
                trigger: ".text-anim",
                start: "top 90%",
                toggleActions: "play none none reverse"
            }
        });
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
                y: 200,
                duration: 1,
                ease: "power3.out",
            
            });
    
    // Cibler chaque carte individuellement dans la boucle Django
    gsap.registerPlugin(ScrollTrigger);

    const vehicleCards = gsap.utils.toArray('.vedette_gallery_display');

    vehicleCards.forEach((card) => {
        const ved_img = card.querySelector('.vehicul_ved_anim');
        const triggerZone = card.querySelector('.img-slide-trigger');

        // Timeline rattachée au ScrollTrigger
        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: '.img-slide-trigger',
                start: "top 80%",
                end: "top 40%",
                toggleActions: "play none none reverse",
                
            }
        });

        // Step 1 : Entrée en slide-in
        tl.fromTo(".vehicul_ved_anim", 
            { x: 200, opacity: 0, scale: 1 },
            { x: 0, opacity: 1, duration: 1.2, ease: "power3.out" }
        )
        // Step 2 : Scale infini (effet respiration)
        .to(ved_img, {
            scale: 1.75,        // Légère augmentation pour un rendu propre
            duration: 3.8,      // Vitesse d'un cycle
            repeat: -1,         // -1 = Boucle infinie
            yoyo: true,         // Fait l'aller-retour (zoom -> dézoom)
            ease: "sine.inOut"  // Transition organique et fluide
        });
    });

});

// ============================================================
// ANIMATION : MISSION & VALEURS
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.registerPlugin(ScrollTrigger);

    let mm = gsap.matchMedia();

    mm.add({
        // Desktop / Tablette
        isDesktop: "(min-width: 768px)",
        // Mobile
        isMobile: "(max-width: 767px)"
    }, (context) => {
        let { isDesktop } = context.conditions;

        // 1. Animation En-tête
        gsap.from(".mission_header", {
            scrollTrigger: {
                trigger: ".mission_header",
                start: "top 85%",
                toggleActions: "play none none reverse"
            },
            opacity: 0,
            y: 30,
            duration: 0.8,
            ease: "power2.out"
        });

        // 2. Animation Carte Mission (Arrivée depuis la gauche sur Desktop, le bas sur Mobile)
        gsap.from(".mission_card", {
            scrollTrigger: {
                trigger: ".mission_card",
                start: "top 80%",
                toggleActions: "play none none reverse"
            },
            opacity: 0,
            x: isDesktop ? -40 : 0,
            y: isDesktop ? 0 : 30,
            duration: 0.9,
            ease: "power3.out"
        });
        // 3. Animation Carte Valeurs + Apparition progressive des 4 items (Stagger)
let valeurTl = gsap.timeline({
    scrollTrigger: {
        trigger: ".valeur_card",
        start: "top 85%",
        toggleActions: "play none none reverse",
        invalidateOnRefresh: true
    }
});

valeurTl.from(".valeur_card", {
    autoAlpha: 0, // Remplace opacity: 0 (gère visibility + opacity)
    x: isDesktop ? 40 : 0,
    y: isDesktop ? 0 : 30,
    duration: 0.9,
    ease: "power3.out",
    clearProps: "all" // Nettoie le CSS inline à la fin de l'anim
})
.from(".valeur_item", {
    autoAlpha: 0,
    y: 20,
    duration: 0.4,
    stagger: 0.1,
    ease: "power2.out",
    clearProps: "all"
}, "-=0.4");

// 4. Animation Bandeau Citation
gsap.from(".citation", {
    scrollTrigger: {
        trigger: ".citation",
        start: "top 90%",
        toggleActions: "play none none reverse",
        invalidateOnRefresh: true
    },
    autoAlpha: 0,
    scale: 0.95,
    y: 20,
    duration: 0.8,
    ease: "power2.out",
    clearProps: "all"
});
    });
});
    
        
// ============================================================
// ANIMATION : PRODUITS VEDETTE (PREMIUM) 
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".product_fade", {
                scrollTrigger: {
                    trigger: ".section_product",
                    start: "5% 70%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                    
                },
                opacity: 0,
                y: 200,
                duration: 1,
            
            });
})

// ============================================================
// ANIMATION : POURQUOI CHOISIR KOZ SERVICES  + un melange de section
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".choisir_fade", {
                scrollTrigger: {
                    trigger: ".section_choisir_koz",
                    start: "5% 70%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                   
                },
                opacity: 0,
                y: 200,
                duration: 1,
            
            });

    gsap.from(".financement_fade", {
                scrollTrigger: {
                    trigger: ".financement_fade",
                    start: "top 75%",
                    end: "top 40%",
                    toggleActions: "play none none reverse",
                },
                opacity: 0,
                y: 180,
                duration: 1,
            });

    gsap.from(".temoignage_fade", {
                scrollTrigger: {
                    trigger: ".temoignage_fade",
                    start: "top 75%",
                    end: "top 40%",
                    toggleActions: "play none none reverse",
                },
                opacity: 0,
                y: 180,
                duration: 1,
            });

    gsap.from(".socials_fade", {
                scrollTrigger: {
                    trigger: ".socials_fade",
                    start: "top 80%",
                    end: "top 40%",
                    toggleActions: "play none none reverse",
                },
                opacity: 0,
                y: 120,
                duration: 1,
                stagger: 0.08,
            });

    gsap.from(".videos_fade", {
                scrollTrigger: {
                    trigger: ".videos_fade",
                    start: "top 80%",
                    end: "top 40%",
                    toggleActions: "play none none reverse",
                },
                opacity: 0,
                y: 120,
                duration: 1,
                stagger: 0.08,
            });

    gsap.from(".section_type_vehicul .fade-section", {
                scrollTrigger: {
                    trigger: ".section_type_vehicul",
                    start: "top 70%",
                    end: "top 35%",
                    toggleActions: "play none none reverse",
                },
                opacity: 0,
                y: 200,
                duration: 1,
            });

    gsap.from(".section_type_vehicul .type-contain > div", {
                scrollTrigger: {
                    trigger: ".section_type_vehicul",
                    start: "top 75%",
                    end: "top 35%",
                    toggleActions: "play none none reverse",
                },
                opacity: 0,
                y: 120,
                duration: 1,
                stagger: 0.14,
            });

    gsap.from(".section_propos .container > .grid > div:first-child", {
                scrollTrigger: {
                    trigger: ".section_propos",
                    start: "top 75%",
                    end: "top 35%",
                    toggleActions: "play none none reverse",
                },
                autoAlpha: 0,
                x: -200,
                duration: 1.2,
                ease: "power3.out",
            });

    gsap.from(".section_propos .container > .grid > div:last-child", {
                scrollTrigger: {
                    trigger: ".section_propos",
                    start: "top 75%",
                    end: "top 35%",
                    toggleActions: "play none none reverse",
                },
                autoAlpha: 0,
                x: 200,
                duration: 1.2,
                ease: "power3.out",
            });

    gsap.from(".section_choisir_koz .grid > div", {
                scrollTrigger: {
                    trigger: ".section_choisir_koz",
                    start: "top 40%",
                    end: "top 55%",
                    toggleActions: "play none none reverse",
                    
                    
                },
                autoAlpha: 0,
                y: 300,
                duration: 1,
                stagger: 0.50,
                immediateRender: false,
                ease: "power3.out",
            });

    gsap.from(".section_stati .stat-card, .stat-card", {
                scrollTrigger: {
                    trigger: ".section_stati",
                    start: "top 40%",
                    end: "top 60%",
                    toggleActions: "play none none reverse",
                    
                    
                },
                autoAlpha: 0,
                y: 300,
                duration: 1,
                stagger: 0.50,
                immediateRender: false,
                ease: "power3.out",
            });

    
})

// ============================================================
// ANIME STAT SECTION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {

    
    gsap.from(".stats_fade", {
                scrollTrigger: {
                    trigger: ".section-stats",
                    start: "top 70%",
                    end: "top 30%",
                    toggleActions: "play none none reverse",
                     
                     
                },
                opacity: 0,
                y: 200,
                duration: 1,
                ease: "power3.out",
            
            });
    
});

document.addEventListener('DOMContentLoaded', () => {
    const statNumbers = document.querySelectorAll('.stat-number');
    const statTexts = document.querySelectorAll('.stat-text');

    // 1. Animation des compteurs numériques (avec prefix/suffix)
    function animateCounter(el) {
        const target = parseInt(el.getAttribute('data-target'), 10);
        const prefix = el.getAttribute('data-prefix') || '';
        const suffix = el.getAttribute('data-suffix') || '';
        const duration = 1800;
        const startTime = performance.now();

        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // Easing cubic-out

            const currentValue = Math.floor(eased * target);
            el.textContent = `${prefix}${currentValue.toLocaleString()}${suffix}`;

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                el.textContent = `${prefix}${target.toLocaleString()}${suffix}`;
            }
        }

        requestAnimationFrame(updateCounter);
    }

    // 2. Observer global pour l'ensemble des cartes
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const card = entry.target;
                
                // Si la carte contient un chiffre à animer
                const numEl = card.querySelector('.stat-number');
                if (numEl) animateCounter(numEl);

                // Si la carte contient du texte, on applique une petite transition d'apparition
                const textEl = card.querySelector('.stat-text');
                if (textEl) {
                    textEl.classList.add('animate-fade-in-up');
                }

                observer.unobserve(card);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.stat-card').forEach(card => observer.observe(card));
});

// ============================================================
// ANIME NOUS CONTACTER + PRISE DE RENDEZ-VOUS  
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".contact_fade", {
                scrollTrigger: {
                    trigger: ".section-contact",
                    start: "top 70%",
                    end: "top 30%",
                    toggleActions: "play none none reverse",
                    
                     
                },
                opacity: 0,
                y: 200,
                duration: 1,
                ease: "power3.out",
            
            });

})


//============================================================
// CTA ANIME – 
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    gsap.from(".cta_fade", {
                scrollTrigger: {
                    trigger: ".section-cta",
                    start: "top 70%",
                    end: "top 30%",
                    toggleActions: "play none none reverse", 
                   
                   
                },
                opacity: 0,
                y: 200,
                duration: 1,
                ease: "power3.out",
            });

        gsap.fromTo(
        ".avantages .group",
        {
            y: 0,
            backgroundColor: "rgba(255,255,255,0.12)",
            borderColor: "rgba(147,197,253,0.2)",
            boxShadow: "0 0 0 rgba(59,130,246,0)",
        },
        {
            scrollTrigger: {
                trigger: ".avantages",
                start: "top 85%",
                end: "top 60%",
                toggleActions: "play none none reverse",
                
            },
            y: 50,
            backgroundColor: "rgba(255,255,255,0.24)",
            borderColor: "rgba(96,165,250,0.35)",
            boxShadow: "0 24px 62px rgba(59,130,246,0.14)",
            duration: 1,
            ease: "sine.inOut",
            repeat: -1,
            yoyo: true,
            stagger: 0.5,
        }
    );

})

// Initialize a new Lenis instance for smooth scrolling
document.addEventListener('DOMContentLoaded', function() {
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
            gsap.ticker.lagSmoothing();


})

  