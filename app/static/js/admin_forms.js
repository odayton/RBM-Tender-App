/**
 * Admin Forms Enhancement JavaScript
 * Provides better UX for company and contact creation forms
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-format phone numbers
    const phoneInputs = document.querySelectorAll('input[name="phone_number"], input[name="mobile_number"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                // Format as Australian phone number
                if (value.startsWith('61')) {
                    value = '+' + value;
                } else if (value.startsWith('0')) {
                    value = '+61' + value.substring(1);
                } else if (!value.startsWith('+')) {
                    value = '+61' + value;
                }
            }
            e.target.value = value;
        });
    });

    // Auto-format ABN
    const abnInput = document.querySelector('input[name="abn"]');
    if (abnInput) {
        abnInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                // Format as ABN (XX XXX XXX XXX)
                value = value.replace(/(\d{2})(\d{3})(\d{3})(\d{3})/, '$1 $2 $3 $4');
            }
            e.target.value = value;
        });
    }

    // Auto-format domain field
    const domainInput = document.querySelector('input[name="domain"]');
    if (domainInput) {
        domainInput.addEventListener('input', function(e) {
            let value = e.target.value.toLowerCase();
            // Remove http/https and www if user enters full URL
            value = value.replace(/^https?:\/\//, '').replace(/^www\./, '');
            e.target.value = value;
        });
    }

    // Auto-format website field
    const websiteInput = document.querySelector('input[name="website"]');
    if (websiteInput) {
        websiteInput.addEventListener('input', function(e) {
            let value = e.target.value.toLowerCase();
            // Add https:// if not present
            if (value && !value.startsWith('http://') && !value.startsWith('https://')) {
                value = 'https://' + value;
            }
            e.target.value = value;
        });
    }

    // Real-time validation feedback
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-suggest company based on email domain
    const emailInput = document.querySelector('input[name="email"]');
    const companySelect = document.querySelector('select[name="company"]');
    
    if (emailInput && companySelect) {
        emailInput.addEventListener('blur', function() {
            const email = this.value;
            if (email && email.includes('@')) {
                const domain = email.split('@')[1];
                
                // Check if any company has this domain
                const options = companySelect.querySelectorAll('option');
                let matchingCompany = null;
                
                options.forEach(option => {
                    if (option.textContent.toLowerCase().includes(domain)) {
                        matchingCompany = option;
                    }
                });
                
                if (matchingCompany) {
                    companySelect.value = matchingCompany.value;
                    showNotification(`Auto-suggested company: ${matchingCompany.textContent}`, 'info');
                }
            }
        });
    }

    // Show notification function
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Enhanced form styling
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
});

// Add some CSS for enhanced styling
const style = document.createElement('style');
style.textContent = `
    .form-control.focused {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
    }
    
    .input-group.focused .input-group-text {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    .form-control:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    }
    
    .btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .card {
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
`;
document.head.appendChild(style); 