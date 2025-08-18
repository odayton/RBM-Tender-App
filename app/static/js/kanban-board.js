/**
 * Kanban Board JavaScript
 * Handles drag-and-drop functionality, status updates, and view toggling
 */

class KanbanBoard {
    constructor() {
        this.draggedElement = null;
        this.dragPreview = null;
        this.init();
    }
    
    init() {
        this.initializeDragAndDrop();
        this.initializeViewToggle();
        this.initializeEventListeners();
    }
    
    // Drag and Drop Functionality
    initializeDragAndDrop() {
        const kanbanCards = document.querySelectorAll('.kanban-card');
        const kanbanColumns = document.querySelectorAll('.kanban-column');
        
        kanbanCards.forEach(card => {
            card.addEventListener('dragstart', (e) => this.handleDragStart(e));
            card.addEventListener('dragend', (e) => this.handleDragEnd(e));
        });
        
        kanbanColumns.forEach(column => {
            column.addEventListener('dragover', (e) => this.handleDragOver(e));
            column.addEventListener('dragenter', (e) => this.handleDragEnter(e));
            column.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            column.addEventListener('drop', (e) => this.handleDrop(e));
        });
    }
    
    handleDragStart(e) {
        this.draggedElement = e.target;
        e.target.classList.add('dragging');
        
        // Create drag preview
        this.dragPreview = e.target.cloneNode(true);
        this.dragPreview.classList.add('drag-preview');
        this.dragPreview.style.position = 'fixed';
        this.dragPreview.style.top = '-1000px';
        this.dragPreview.style.left = '-1000px';
        document.body.appendChild(this.dragPreview);
        
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', e.target.outerHTML);
    }
    
    handleDragEnd(e) {
        e.target.classList.remove('dragging');
        
        // Remove drag preview
        if (this.dragPreview) {
            document.body.removeChild(this.dragPreview);
            this.dragPreview = null;
        }
        
        // Remove drag-over styling from all columns
        document.querySelectorAll('.kanban-column').forEach(column => {
            column.classList.remove('drag-over', 'drop-target');
        });
        
        this.draggedElement = null;
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }
    
    handleDragEnter(e) {
        e.preventDefault();
        const column = e.target.closest('.kanban-column');
        if (column) {
            column.classList.add('drag-over');
        }
    }
    
    handleDragLeave(e) {
        const column = e.target.closest('.kanban-column');
        if (column && !column.contains(e.relatedTarget)) {
            column.classList.remove('drag-over');
        }
    }
    
    handleDrop(e) {
        e.preventDefault();
        const targetColumn = e.target.closest('.kanban-column');
        
        if (targetColumn && this.draggedElement) {
            const newStatus = targetColumn.dataset.status;
            const taskId = this.draggedElement.dataset.taskId;
            
            // Move the card to the new column
            const columnContent = targetColumn.querySelector('.kanban-column-content');
            columnContent.appendChild(this.draggedElement);
            
            // Update the task status via AJAX
            this.updateTaskStatus(taskId, newStatus);
            
            // Update column counts
            this.updateColumnCounts();
            
            // Show success notification
            this.showNotification(`Task moved to ${this.getStatusDisplayName(newStatus)}`, 'success');
        }
        
        // Remove drag-over styling
        targetColumn.classList.remove('drag-over', 'drop-target');
    }
    
    // Status Update Functionality
    async updateTaskStatus(taskId, newStatus) {
        try {
            const response = await fetch(`/crm/tasks/${taskId}/update-status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    status: newStatus,
                    csrf_token: this.getCSRFToken()
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to update task status');
            }
            
            const result = await response.json();
            if (result.success) {
                console.log('Task status updated successfully');
            } else {
                throw new Error(result.message || 'Failed to update task status');
            }
        } catch (error) {
            console.error('Error updating task status:', error);
            this.showNotification('Failed to update task status', 'error');
            
            // Revert the card position if update failed
            this.revertCardPosition();
        }
    }
    
    revertCardPosition() {
        // This would need to be implemented to revert the card to its original position
        // For now, we'll just show an error message
        this.showNotification('Failed to update task status. Please try again.', 'error');
    }
    
    // View Toggle Functionality
    initializeViewToggle() {
        const kanbanViewBtn = document.getElementById('kanbanView');
        const listViewBtn = document.getElementById('listView');
        const kanbanContent = document.getElementById('kanbanViewContent');
        const listContent = document.getElementById('listViewContent');
        
        if (kanbanViewBtn && listViewBtn) {
            kanbanViewBtn.addEventListener('click', () => {
                this.switchToKanbanView(kanbanViewBtn, listViewBtn, kanbanContent, listContent);
            });
            
            listViewBtn.addEventListener('click', () => {
                this.switchToListView(kanbanViewBtn, listViewBtn, kanbanContent, listContent);
            });
        }
    }
    
    switchToKanbanView(kanbanBtn, listBtn, kanbanContent, listContent) {
        kanbanBtn.classList.add('active');
        listBtn.classList.remove('active');
        kanbanContent.style.display = 'block';
        listContent.style.display = 'none';
        
        // Save preference
        localStorage.setItem('taskViewPreference', 'kanban');
    }
    
    switchToListView(kanbanBtn, listBtn, kanbanContent, listContent) {
        listBtn.classList.add('active');
        kanbanBtn.classList.remove('active');
        listContent.style.display = 'block';
        kanbanContent.style.display = 'none';
        
        // Save preference
        localStorage.setItem('taskViewPreference', 'list');
    }
    
    // Column Count Updates
    updateColumnCounts() {
        const columns = document.querySelectorAll('.kanban-column');
        
        columns.forEach(column => {
            const status = column.dataset.status;
            const content = column.querySelector('.kanban-column-content');
            const count = content.children.length;
            const badge = column.querySelector('.badge');
            
            if (badge) {
                badge.textContent = count;
            }
        });
    }
    
    // Event Listeners
    initializeEventListeners() {
        // Quick status change buttons (if any)
        document.querySelectorAll('.quick-status-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const taskId = e.target.dataset.taskId;
                const newStatus = e.target.dataset.status;
                this.quickStatusChange(taskId, newStatus);
            });
        });
        
        // Filter form submission
        const filterForm = document.querySelector('#filterModal form');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => {
                this.handleFilterSubmit(e);
            });
        }
        
        // Sort form submission
        const sortForm = document.querySelector('#sortModal form');
        if (sortForm) {
            sortForm.addEventListener('submit', (e) => {
                this.handleSortSubmit(e);
            });
        }
    }
    
    // Quick Status Change
    async quickStatusChange(taskId, newStatus) {
        try {
            await this.updateTaskStatus(taskId, newStatus);
            
            // Move the card to the appropriate column
            const card = document.querySelector(`[data-task-id="${taskId}"]`);
            const targetColumn = document.querySelector(`[data-status="${newStatus}"] .kanban-column-content`);
            
            if (card && targetColumn) {
                targetColumn.appendChild(card);
                this.updateColumnCounts();
                this.showNotification(`Task status changed to ${this.getStatusDisplayName(newStatus)}`, 'success');
            }
        } catch (error) {
            console.error('Error in quick status change:', error);
        }
    }
    
    // Filter and Sort Handlers
    handleFilterSubmit(e) {
        // The form will submit normally, but we can add custom logic here if needed
        this.showNotification('Filters applied', 'info');
    }
    
    handleSortSubmit(e) {
        // The form will submit normally, but we can add custom logic here if needed
        this.showNotification('Sorting applied', 'info');
    }
    
    // Utility Methods
    getStatusDisplayName(status) {
        const statusMap = {
            'pending': 'Not Started',
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'deferred': 'Deferred',
            'cancelled': 'Cancelled'
        };
        return statusMap[status] || status;
    }
    
    getCSRFToken() {
        const tokenElement = document.querySelector('meta[name="csrf-token"]');
        return tokenElement ? tokenElement.getAttribute('content') : '';
    }
    
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
    
    // Card Management
    addCard(taskData) {
        const column = document.querySelector(`[data-status="${taskData.status}"]`);
        if (column) {
            const card = this.createCardElement(taskData);
            const content = column.querySelector('.kanban-column-content');
            content.appendChild(card);
            this.updateColumnCounts();
        }
    }
    
    createCardElement(taskData) {
        const card = document.createElement('div');
        card.className = 'kanban-card';
        card.dataset.taskId = taskData.id;
        card.draggable = true;
        
        card.innerHTML = `
            <div class="card border-0 shadow-sm">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">${taskData.title}</h6>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="/crm/tasks/${taskData.id}/view">
                                    <i class="fas fa-eye"></i> View
                                </a></li>
                                <li><a class="dropdown-item" href="/crm/tasks/${taskData.id}/edit">
                                    <i class="fas fa-edit"></i> Edit
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="deleteTask(${taskData.id})">
                                    <i class="fas fa-trash"></i> Delete
                                </a></li>
                            </ul>
                        </div>
                    </div>
                    <p class="text-muted small mb-2">${taskData.description || ''}</p>
                    <div class="mb-2">
                        <span class="badge bg-${taskData.priority.toLowerCase()}">${taskData.priority}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <div class="avatar-sm me-2">
                                <img src="https://ui-avatars.com/api/?name=${taskData.assigned_to}&background=random" 
                                     class="rounded-circle" width="24" height="24" alt="${taskData.assigned_to}">
                            </div>
                            <small class="text-muted">${taskData.assigned_to}</small>
                        </div>
                        <small class="text-muted">
                            ${taskData.due_date ? `<i class="fas fa-calendar"></i> ${taskData.due_date}` : ''}
                        </small>
                    </div>
                </div>
            </div>
        `;
        
        // Add drag event listeners
        card.addEventListener('dragstart', (e) => this.handleDragStart(e));
        card.addEventListener('dragend', (e) => this.handleDragEnd(e));
        
        return card;
    }
    
    removeCard(taskId) {
        const card = document.querySelector(`[data-task-id="${taskId}"]`);
        if (card) {
            card.remove();
            this.updateColumnCounts();
        }
    }
    
    // Load saved view preference
    loadViewPreference() {
        const preference = localStorage.getItem('taskViewPreference');
        if (preference === 'list') {
            const listBtn = document.getElementById('listView');
            if (listBtn) {
                listBtn.click();
            }
        }
    }
}

// Global functions for HTML onclick handlers
function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/crm/tasks/${taskId}/delete`;
        
        // Add CSRF token if available
        const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
        if (csrfTokenElement) {
            const csrfToken = csrfTokenElement.getAttribute('content');
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
            }
        }
        
        document.body.appendChild(form);
        form.submit();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.kanbanBoard = new KanbanBoard();
    window.kanbanBoard.loadViewPreference();
}); 