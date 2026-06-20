// Pet Adoption Platform Client Side Scripts

document.addEventListener('DOMContentLoaded', function() {
    // 1. Auto-dismiss Bootstrap flash alerts after 5 seconds
    const flashAlerts = document.querySelectorAll('.alert-dismissible');
    flashAlerts.forEach(function(alert) {
        setTimeout(function() {
            // Using Bootstrap's alert class method to close
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Photo upload dynamic preview
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

    // 3. Confirm Delete Prompts
    const deleteForms = document.querySelectorAll('.confirm-delete-form');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const petName = this.dataset.petName || 'this pet';
            const confirmed = confirm(`Are you sure you want to delete ${petName}? This action cannot be undone.`);
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});
