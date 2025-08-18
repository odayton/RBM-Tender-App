/**
 * Activity Form JavaScript
 * Handles activity form interactions, validation, and dynamic behavior
 */

class ActivityForm {
    constructor() {
        this.form = document.getElementById('activityForm');
        this.privateCheckbox = document.getElementById('is_private');
        this.durationInput = document.getElementById('duration_minutes');
        this.scheduledDateInput = document.getElementById('scheduled_date');
        this.tagsInput = document.getElementById('tags');
        
        this.init();
    }
    
    init() {
        this.initializeFormValidation();
        this.initializePrivateToggle();
        this.initializeDurationInput();
        this.initializeDatePicker();
        this.initializeTagsInput();
        this.initializeFormEnhancements();
    }
    
    // Form Validation
    initializeFormValidation() {
        if (!this.form) return;
        
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showValidationErrors();
            }
        });
        
        // Real-time validation
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', () => {
                this.validateField(field);
            });
        });
    }
    
    validateForm() {
        let isValid = true;
        const requiredFields = this.form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        // Custom validation for duration
        if (this.durationInput && this.durationInput.value) {
            const duration = parseInt(this.durationInput.value);
            if (duration <= 0 || duration > 1440) { // Max 24 hours
                this.showFieldError(this.durationInput, 'Duration must be between 1 and 1440 minutes');
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        
        if (isRequired && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }
        
        // Clear any existing errors
        this.clearFieldError(field);
        
        // Specific field validations
        if (field.name === 'title' && value.length < 3) {
            this.showFieldError(field, 'Title must be at least 3 characters long');
            return false;
        }
        
        if (field.name === 'scheduled_date' && value) {
            const selectedDate = new Date(value);
            const now = new Date();
            if (selectedDate < now) {
                this.showFieldError(field, 'Scheduled date cannot be in the past');
                return false;
            }
        }
        
        return true;
    }
    
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    showValidationErrors() {
        const firstError = this.form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
    
    // Private Activity Toggle
    initializePrivateToggle() {
        if (!this.privateCheckbox) return;
        
        this.privateCheckbox.addEventListener('change', () => {
            this.updatePrivateIndicator();
        });
        
        // Initialize on load
        this.updatePrivateIndicator();
    }
    
    updatePrivateIndicator() {
        const privateIndicator = document.querySelector('.private-indicator');
        if (privateIndicator) {
            if (this.privateCheckbox.checked) {
                privateIndicator.style.display = 'block';
            } else {
                privateIndicator.style.display = 'none';
            }
        }
    }
    
    // Duration Input Enhancement
    initializeDurationInput() {
        if (!this.durationInput) return;
        
        // Add input validation
        this.durationInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/[^0-9]/g, '');
            
            // Limit to reasonable range
            if (value > 1440) {
                value = 1440;
            }
            
            e.target.value = value;
        });
        
        // Add quick duration buttons
        this.addQuickDurationButtons();
    }
    
    addQuickDurationButtons() {
        const durationContainer = this.durationInput.parentNode;
        const quickButtons = document.createElement('div');
        quickButtons.className = 'mt-2';
        quickButtons.innerHTML = `
            <small class="text-muted">Quick select: </small>
            <button type="button" class="btn btn-sm btn-outline-secondary me-1" data-duration="15">15m</button>
            <button type="button" class="btn btn-sm btn-outline-secondary me-1" data-duration="30">30m</button>
            <button type="button" class="btn btn-sm btn-outline-secondary me-1" data-duration="60">1h</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-duration="120">2h</button>
        `;
        
        durationContainer.appendChild(quickButtons);
        
        // Add event listeners
        quickButtons.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const duration = btn.dataset.duration;
                this.durationInput.value = duration;
                this.durationInput.focus();
            });
        });
    }
    
    // Date Picker Enhancement
    initializeDatePicker() {
        if (!this.scheduledDateInput) return;
        
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        this.scheduledDateInput.setAttribute('min', today);
        
        // Add quick date buttons
        this.addQuickDateButtons();
    }
    
    addQuickDateButtons() {
        const dateContainer = this.scheduledDateInput.parentNode;
        const quickButtons = document.createElement('div');
        quickButtons.className = 'mt-2';
        quickButtons.innerHTML = `
            <small class="text-muted">Quick select: </small>
            <button type="button" class="btn btn-sm btn-outline-secondary me-1" data-days="1">Tomorrow</button>
            <button type="button" class="btn btn-sm btn-outline-secondary me-1" data-days="7">Next Week</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-days="30">Next Month</button>
        `;
        
        dateContainer.appendChild(quickButtons);
        
        // Add event listeners
        quickButtons.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const days = parseInt(btn.dataset.days);
                const futureDate = new Date();
                futureDate.setDate(futureDate.getDate() + days);
                const dateString = futureDate.toISOString().split('T')[0];
                this.scheduledDateInput.value = dateString;
                this.scheduledDateInput.focus();
            });
        });
    }
    
    // Tags Input Enhancement
    initializeTagsInput() {
        if (!this.tagsInput) return;
        
        this.tagsInput.addEventListener('input', (e) => {
            // Auto-format tags
            let value = e.target.value;
            value = value.replace(/,\s*,/g, ','); // Remove double commas
            value = value.replace(/,\s*$/g, ','); // Ensure trailing comma
            e.target.value = value;
        });
        
        // Add suggested tags
        this.addSuggestedTags();
    }
    
    addSuggestedTags() {
        const tagsContainer = this.tagsInput.parentNode;
        const suggestedTags = document.createElement('div');
        suggestedTags.className = 'mt-2';
        suggestedTags.innerHTML = `
            <small class="text-muted">Suggested tags: </small>
            <button type="button" class="btn btn-sm btn-outline-primary me-1" data-tag="follow-up">follow-up</button>
            <button type="button" class="btn btn-sm btn-outline-primary me-1" data-tag="important">important</button>
            <button type="button" class="btn btn-sm btn-outline-primary me-1" data-tag="urgent">urgent</button>
            <button type="button" class="btn btn-sm btn-outline-primary" data-tag="meeting">meeting</button>
        `;
        
        tagsContainer.appendChild(suggestedTags);
        
        // Add event listeners
        suggestedTags.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const tag = btn.dataset.tag;
                const currentTags = this.tagsInput.value;
                const newTags = currentTags ? `${currentTags}${tag},` : `${tag},`;
                this.tagsInput.value = newTags;
                this.tagsInput.focus();
            });
        });
    }
    
    // Form Enhancements
    initializeFormEnhancements() {
        // Auto-save draft functionality
        this.initializeAutoSave();
        
        // Form state management
        this.initializeFormState();
    }
    
    initializeAutoSave() {
        let autoSaveTimer;
        
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('input', () => {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    this.saveDraft();
                }, 2000); // Save after 2 seconds of inactivity
            });
        });
    }
    
    saveDraft() {
        const formData = new FormData(this.form);
        const draft = {};
        
        for (let [key, value] of formData.entries()) {
            draft[key] = value;
        }
        
        localStorage.setItem('activityFormDraft', JSON.stringify(draft));
        this.showNotification('Draft saved automatically', 'info');
    }
    
    loadDraft() {
        const draft = localStorage.getItem('activityFormDraft');
        if (draft) {
            const data = JSON.parse(draft);
            
            Object.keys(data).forEach(key => {
                const field = this.form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
            
            this.showNotification('Draft loaded', 'success');
        }
    }
    
    clearDraft() {
        localStorage.removeItem('activityFormDraft');
    }
    
    initializeFormState() {
        // Load draft on page load
        this.loadDraft();
        
        // Clear draft on successful submission
        this.form.addEventListener('submit', () => {
            this.clearDraft();
        });
    }
    
    // Notification System
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    // Utility Methods
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    resetForm() {
        this.form.reset();
        this.clearDraft();
        this.showNotification('Form reset', 'info');
    }
}

// Global functions for template access
function resetActivityForm() {
    if (window.activityForm) {
        window.activityForm.resetForm();
    }
}

function loadActivityDraft() {
    if (window.activityForm) {
        window.activityForm.loadDraft();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.activityForm = new ActivityForm();
}); 