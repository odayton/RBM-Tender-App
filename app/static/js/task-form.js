/**
 * Task Form JavaScript
 * Handles subtask management, form interactions, and dynamic behavior
 */

class TaskForm {
    constructor() {
        this.subtasksContainer = document.getElementById('subtasksContainer');
        this.newSubtaskInput = document.getElementById('newSubtaskInput');
        this.addSubtaskBtn = document.getElementById('addSubtaskBtn');
        this.subtaskTemplate = document.getElementById('subtaskTemplate');
        this.recurringCheckbox = document.getElementById('is_recurring');
        this.recurringOptions = document.getElementById('recurringOptions');
        this.subtaskCounter = 0;
        
        this.init();
    }
    
    init() {
        this.initializeSubtaskFunctionality();
        this.initializeRecurringToggle();
        this.loadExistingSubtasks();
        this.initializeFormValidation();
    }
    
    // Subtask Management
    initializeSubtaskFunctionality() {
        if (!this.addSubtaskBtn || !this.newSubtaskInput) return;
        
        // Add subtask button
        this.addSubtaskBtn.addEventListener('click', () => {
            this.addSubtask();
        });
        
        // Enter key to add subtask
        this.newSubtaskInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.addSubtask();
            }
        });
    }
    
    addSubtask(title = '') {
        if (!this.subtaskTemplate || !this.subtasksContainer) return;
        
        const subtaskElement = this.subtaskTemplate.content.cloneNode(true);
        const subtaskItem = subtaskElement.querySelector('.subtask-item');
        const titleInput = subtaskItem.querySelector('.subtask-title');
        const checkbox = subtaskItem.querySelector('.subtask-checkbox');
        const removeBtn = subtaskItem.querySelector('.remove-subtask');
        
        this.subtaskCounter++;
        subtaskItem.dataset.subtaskId = this.subtaskCounter;
        titleInput.value = title;
        
        // Add hidden inputs for form submission
        const hiddenTitleInput = document.createElement('input');
        hiddenTitleInput.type = 'hidden';
        hiddenTitleInput.name = `subtasks[${this.subtaskCounter}][title]`;
        hiddenTitleInput.value = title;
        subtaskItem.appendChild(hiddenTitleInput);
        
        const completedInput = document.createElement('input');
        completedInput.type = 'hidden';
        completedInput.name = `subtasks[${this.subtaskCounter}][completed]`;
        completedInput.value = 'false';
        subtaskItem.appendChild(completedInput);
        
        // Event listeners
        checkbox.addEventListener('change', () => {
            const isCompleted = checkbox.checked;
            subtaskItem.classList.toggle('completed', isCompleted);
            titleInput.classList.toggle('text-decoration-line-through', isCompleted);
            completedInput.value = isCompleted.toString();
        });
        
        removeBtn.addEventListener('click', () => {
            subtaskItem.remove();
        });
        
        // Update hidden input when title changes
        titleInput.addEventListener('input', () => {
            hiddenTitleInput.value = titleInput.value;
        });
        
        this.subtasksContainer.appendChild(subtaskItem);
        
        // Clear input if it was a new subtask
        if (this.newSubtaskInput && title === '') {
            this.newSubtaskInput.value = '';
        }
    }
    
    // Recurring Task Toggle
    initializeRecurringToggle() {
        if (!this.recurringCheckbox || !this.recurringOptions) return;
        
        this.recurringCheckbox.addEventListener('change', () => {
            this.recurringOptions.style.display = this.recurringCheckbox.checked ? 'block' : 'none';
        });
        
        // Initialize visibility
        if (this.recurringCheckbox.checked) {
            this.recurringOptions.style.display = 'block';
        }
    }
    
    // Load existing subtasks (for editing)
    loadExistingSubtasks() {
        // This will be populated by the template with existing subtask data
        // The template will call addSubtask() for each existing subtask
    }
    
    // Form Validation
    initializeFormValidation() {
        const form = document.getElementById('taskForm');
        if (!form) return;
        
        // Custom validation for required fields
        form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showValidationErrors();
            }
        });
    }
    
    validateForm() {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    
    showValidationErrors() {
        // Show a notification or scroll to first error
        const firstError = document.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
    
    // Utility Methods
    getSubtasksData() {
        const subtasks = [];
        const subtaskItems = this.subtasksContainer.querySelectorAll('.subtask-item');
        
        subtaskItems.forEach(item => {
            const titleInput = item.querySelector('.subtask-title');
            const checkbox = item.querySelector('.subtask-checkbox');
            
            subtasks.push({
                title: titleInput.value,
                completed: checkbox.checked
            });
        });
        
        return subtasks;
    }
    
    clearSubtasks() {
        if (this.subtasksContainer) {
            this.subtasksContainer.innerHTML = '';
        }
        this.subtaskCounter = 0;
    }
}

// Global functions for template access
function addSubtask(title = '') {
    if (window.taskForm) {
        window.taskForm.addSubtask(title);
    }
}

function clearSubtasks() {
    if (window.taskForm) {
        window.taskForm.clearSubtasks();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.taskForm = new TaskForm();
}); 