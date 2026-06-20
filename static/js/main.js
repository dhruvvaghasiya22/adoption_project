// Pet Adoption Platform Interactive Client Scripts

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Auto-dismiss alerts after 5 seconds
    const flashAlerts = document.querySelectorAll('.alert-dismissible');
    flashAlerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Photo Upload Preview (Add / Edit Forms)
    const photoInput = document.querySelector('input[type="file"][name="photo"]');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImage = document.getElementById('image-preview');

    if (photoInput && previewContainer && previewImage) {
        photoInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.addEventListener('load', function() {
                    previewImage.setAttribute('src', this.result);
                    previewContainer.style.display = 'block';
                });
                reader.readAsDataURL(file);
            } else {
                previewImage.setAttribute('src', '#');
                previewContainer.style.display = 'none';
            }
        });
    }

    // 3. Mobile Filters Drawer Toggle (Browse Page)
    const openFiltersBtn = document.getElementById('open-filters-btn');
    const closeFiltersBtn = document.getElementById('close-filters-btn');
    const drawer = document.getElementById('mobile-filter-drawer');
    const overlay = document.getElementById('overlay-backdrop');

    if (openFiltersBtn && drawer && overlay) {
        openFiltersBtn.addEventListener('click', function() {
            drawer.classList.add('drawer-active');
            overlay.classList.add('overlay-active');
        });
    }

    if (closeFiltersBtn && drawer && overlay) {
        closeFiltersBtn.addEventListener('click', closeFilters);
    }
    if (overlay && drawer) {
        overlay.addEventListener('click', closeFilters);
    }

    function closeFilters() {
        if (drawer) drawer.classList.remove('drawer-active');
        if (overlay) overlay.classList.remove('overlay-active');
    }

    // 4. Favorites Toggle System
    let favorites = [];
    try {
        const saved = localStorage.getItem('pet_favorites');
        favorites = saved ? JSON.parse(saved) : [];
    } catch (e) {
        console.error('Error parsing favorites', e);
    }

    // Initialize Favorite Heart Buttons
    const favButtons = document.querySelectorAll('.fav-btn');
    favButtons.forEach(btn => {
        const petId = btn.dataset.petId;
        if (favorites.includes(petId)) {
            const icon = btn.querySelector('svg');
            if (icon) {
                icon.classList.add('text-red-500', 'fill-red-500');
            }
        }

        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const icon = this.querySelector('svg');
            
            if (favorites.includes(petId)) {
                favorites = favorites.filter(id => id !== petId);
                if (icon) {
                    icon.classList.remove('text-red-500', 'fill-red-500');
                }
            } else {
                favorites.push(petId);
                if (icon) {
                    icon.classList.add('text-red-500', 'fill-red-500');
                }
            }
            localStorage.setItem('pet_favorites', JSON.stringify(favorites));
        });
    });

    // 5. Scroll Reveal Intersection Observer
    const revealElements = document.querySelectorAll('.animate-scroll-reveal');
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('reveal-active');
                    revealObserver.unobserve(entry.target); // Reveal only once
                }
            });
        }, { threshold: 0.1 });

        revealElements.forEach(el => revealObserver.observe(el));
    }

    // 6. Inline Adoption Application Modal (Pet Details Page)
    const openAdoptBtn = document.getElementById('open-adopt-modal-btn');
    const closeAdoptBtn = document.getElementById('close-adopt-modal-btn');
    const cancelAdoptBtn = document.getElementById('cancel-adopt-modal-btn');
    const adoptModal = document.getElementById('adopt-modal-container');
    const adoptOverlay = document.getElementById('adopt-modal-overlay');

    if (openAdoptBtn && adoptModal && adoptOverlay) {
        openAdoptBtn.addEventListener('click', function() {
            adoptModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Stop page scrolling
        });
    }

    if (adoptModal && adoptOverlay) {
        const closeActions = [closeAdoptBtn, cancelAdoptBtn, adoptOverlay];
        closeActions.forEach(btn => {
            if (btn) {
                btn.addEventListener('click', function() {
                    adoptModal.classList.add('hidden');
                    document.body.style.overflow = ''; // Resume page scrolling
                });
            }
        });
    }
});
