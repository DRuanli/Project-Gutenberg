
// Scripts for the Word Frequency Analyzer application

// Function to handle form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const requiredInputs = form.querySelectorAll('[required]');
    
    requiredInputs.forEach(input => {
        if (!input.value) {
            isValid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add event listeners when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Form validation for Gutenberg form
    const gutenbergForm = document.querySelector('form');
    if (gutenbergForm) {
        gutenbergForm.addEventListener('submit', function(e) {
            if (!validateForm(gutenbergForm.id)) {
                e.preventDefault();
            }
        });
    }
    
    // File input change handler
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            if (fileName) {
                const label = this.nextElementSibling;
                if (label) {
                    label.textContent = fileName;
                }
            }
        });
    }
});