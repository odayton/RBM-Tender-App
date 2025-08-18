/**
 * Enhanced Admin Forms JavaScript
 * Provides interactive features and animations for admin forms
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize enhanced admin forms
    initAdminForms();
});

function initAdminForms() {
    // Add form validation enhancements
    enhanceFormValidation();
    
    // Add interactive animations
    addFormAnimations();
    
    // Add real-time feedback
    addRealTimeFeedback();
    
    // Add form submission enhancements
    enhanceFormSubmission();
}

function enhanceFormValidation() {
    const forms = document.querySelectorAll('.company-form, .contact-form, .admin-form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('.form-control');
        
        inputs.forEach(input => {
            // Add real-time validation feedback
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldValidation(this);
            });
            
            // Add focus effects
            input.addEventListener('focus', function() {
                this.closest('.input-group').classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.closest('.input-group').classList.remove('focused');
            });
        });
    });
}

function validateField(field) {
    const inputGroup = field.closest('.input-group');
    const value = field.value.trim();
    
    // Clear previous validation states
    clearFieldValidation(field);
    
    // Check if field is required
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Phone validation
    if (field.name === 'phone_number' && value) {
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        if (!phoneRegex.test(value)) {
            showFieldError(field, 'Please enter a valid phone number');
            return false;
        }
    }
    
    // Website validation
    if (field.name === 'website' && value) {
        if (!value.startsWith('http://') && !value.startsWith('https://')) {
            showFieldError(field, 'Website must start with http:// or https://');
            return false;
        }
    }
    
    // Show success state for valid fields
    if (value) {
        showFieldSuccess(field);
    }
    
    return true;
}

function showFieldError(field, message) {
    const inputGroup = field.closest('.input-group');
    inputGroup.classList.add('has-error');
    
    // Create or update error message
    let errorDiv = inputGroup.querySelector('.field-error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        inputGroup.appendChild(errorDiv);
    }
    
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    errorDiv.style.display = 'block';
}

function showFieldSuccess(field) {
    const inputGroup = field.closest('.input-group');
    inputGroup.classList.add('has-success');
    
    // Add success icon
    let successIcon = inputGroup.querySelector('.success-icon');
    if (!successIcon) {
        successIcon = document.createElement('i');
        successIcon.className = 'fas fa-check success-icon';
        successIcon.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #28a745;
            z-index: 10;
        `;
        inputGroup.style.position = 'relative';
        inputGroup.appendChild(successIcon);
    }
}

function clearFieldValidation(field) {
    const inputGroup = field.closest('.input-group');
    inputGroup.classList.remove('has-error', 'has-success');
    
    // Remove error message
    const errorDiv = inputGroup.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
    
    // Remove success icon
    const successIcon = inputGroup.querySelector('.success-icon');
    if (successIcon) {
        successIcon.remove();
    }
}

function addFormAnimations() {
    // Add staggered animation to form sections
    const formSections = document.querySelectorAll('.form-section');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    formSections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(section);
    });
    
    // Add hover effects to input groups
    const inputGroups = document.querySelectorAll('.input-group');
    inputGroups.forEach(group => {
        group.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        group.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function addRealTimeFeedback() {
    // Add character count for text areas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'char-counter';
            counter.style.cssText = `
                font-size: 0.75rem;
                color: #6c757d;
                text-align: right;
                margin-top: 0.25rem;
            `;
            textarea.parentNode.appendChild(counter);
            
            const updateCounter = () => {
                const current = textarea.value.length;
                counter.textContent = `${current}/${maxLength}`;
                counter.style.color = current > maxLength * 0.9 ? '#dc3545' : '#6c757d';
            };
            
            textarea.addEventListener('input', updateCounter);
            updateCounter();
        }
    });
    
    // Add progress indicator for form completion
    const forms = document.querySelectorAll('.company-form, .contact-form, .admin-form');
    forms.forEach(form => {
        const progressBar = document.createElement('div');
        progressBar.className = 'form-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(135deg, #37779e 0%, #2c5a7a 100%);
            z-index: 9999;
            transition: width 0.3s ease;
        `;
        document.body.appendChild(progressBar);
        
        const updateProgress = () => {
            const requiredFields = form.querySelectorAll('[required]');
            const filledFields = Array.from(requiredFields).filter(field => field.value.trim() !== '');
            const progress = (filledFields.length / requiredFields.length) * 100;
            progressBar.style.width = `${progress}%`;
        };
        
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', updateProgress);
        });
        
        updateProgress();
    });
}

function enhanceFormSubmission() {
    const forms = document.querySelectorAll('.company-form, .contact-form, .admin-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Validate all fields before submission
            const inputs = this.querySelectorAll('.form-control');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showFormError('Please fix the errors before submitting');
                return false;
            }
            
            // Add loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            submitBtn.disabled = true;
            this.classList.add('form-loading');
            
            // Simulate form processing (remove in production)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                this.classList.remove('form-loading');
            }, 2000);
        });
    });
}

function showFormError(message) {
    // Create or update form error message
    let errorAlert = document.querySelector('.form-error-alert');
    if (!errorAlert) {
        errorAlert = document.createElement('div');
        errorAlert.className = 'form-error-alert alert alert-danger';
        errorAlert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        `;
        document.body.appendChild(errorAlert);
    }
    
    errorAlert.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        ${message}
        <button type="button" class="close" onclick="this.parentElement.remove()">
            <span>&times;</span>
        </button>
    `;
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorAlert.parentElement) {
            errorAlert.remove();
        }
    }, 5000);
}

// Add CSS for new validation states
const additionalStyles = `
    .input-group.has-error {
        border-color: #dc3545;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
    }
    
    .input-group.has-success {
        border-color: #28a745;
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
    }
    
    .field-error {
        color: #dc3545;
        font-size: 0.875rem;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: rgba(220, 53, 69, 0.05);
        border-radius: 6px;
        border-left: 3px solid #dc3545;
    }
    
    .input-group.focused {
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .char-counter {
        font-size: 0.75rem;
        color: #6c757d;
        text-align: right;
        margin-top: 0.25rem;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet); 