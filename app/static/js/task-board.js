/**
 * Task Board JavaScript
 * Handles task management, time tracking, drag & drop, and automation
 */

class TaskBoard {
    constructor() {
        this.timeTracking = {};
        this.notifications = [];
        this.init();
    }

    init() {
        this.initializeViewToggle();
        this.initializeDragAndDrop();
        this.initializeEventListeners();
        this.loadSavedTimeTracking();
    }

    // View Toggle Functionality
    initializeViewToggle() {
        const boardViewBtn = document.getElementById('boardView');
        const listViewBtn = document.getElementById('listView');
        
        if (boardViewBtn && listViewBtn) {
            boardViewBtn.addEventListener('click', () => this.switchToBoardView());
            listViewBtn.addEventListener('click', () => this.switchToListView());
        }
    }

    switchToBoardView() {
        document.getElementById('boardViewContent').style.display = 'block';
        document.getElementById('listViewContent').style.display = 'none';
        document.getElementById('boardView').classList.add('active');
        document.getElementById('listView').classList.remove('active');
        this.saveViewPreference('board');
    }

    switchToListView() {
        document.getElementById('boardViewContent').style.display = 'none';
        document.getElementById('listViewContent').style.display = 'block';
        document.getElementById('listView').classList.add('active');
        document.getElementById('boardView').classList.remove('active');
        this.saveViewPreference('list');
    }

    saveViewPreference(view) {
        localStorage.setItem('taskBoardView', view);
    }

    loadViewPreference() {
        const savedView = localStorage.getItem('taskBoardView');
        if (savedView === 'list') {
            this.switchToListView();
        }
    }

    // Time Tracking Functionality
    toggleTimeTracking(activityId) {
        const timeIcon = document.getElementById(`timeIcon-${activityId}`);
        const timeText = document.getElementById(`timeText-${activityId}`);
        const timeDisplay = document.getElementById(`timeDisplay-${activityId}`);
        
        if (!this.timeTracking[activityId]) {
            this.startTimeTracking(activityId, timeIcon, timeText, timeDisplay);
        } else {
            this.stopTimeTracking(activityId, timeIcon, timeText, timeDisplay);
        }
    }

    startTimeTracking(activityId, timeIcon, timeText, timeDisplay) {
        this.timeTracking[activityId] = {
            startTime: new Date(),
            isRunning: true,
            totalTime: this.getSavedTime(activityId) || 0
        };
        
        timeIcon.className = 'fas fa-pause';
        timeText.textContent = 'Pause';
        
        // Update display every second
        this.timeTracking[activityId].interval = setInterval(() => {
            this.updateTimeDisplay(activityId);
        }, 1000);
        
        this.showNotification('Time tracking started', 'success');
        this.saveTimeTracking();
    }

    stopTimeTracking(activityId, timeIcon, timeText, timeDisplay) {
        this.timeTracking[activityId].isRunning = false;
        clearInterval(this.timeTracking[activityId].interval);
        
        // Calculate total time
        const now = new Date();
        const sessionTime = now - this.timeTracking[activityId].startTime;
        this.timeTracking[activityId].totalTime += sessionTime;
        
        timeIcon.className = 'fas fa-play';
        timeText.textContent = 'Start';
        
        this.showNotification('Time tracking paused', 'info');
        this.saveTimeTracking();
    }

    updateTimeDisplay(activityId) {
        if (!this.timeTracking[activityId] || !this.timeTracking[activityId].isRunning) return;
        
        const now = new Date();
        const sessionTime = now - this.timeTracking[activityId].startTime;
        const totalTime = this.timeTracking[activityId].totalTime + sessionTime;
        
        const timeDisplay = document.getElementById(`timeDisplay-${activityId}`);
        if (timeDisplay) {
            timeDisplay.textContent = this.formatTime(totalTime);
        }
    }

    formatTime(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${seconds}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds}s`;
        } else {
            return `${seconds}s`;
        }
    }

    getSavedTime(activityId) {
        const saved = localStorage.getItem(`timeTracking_${activityId}`);
        return saved ? parseInt(saved) : 0;
    }

    saveTimeTracking() {
        Object.keys(this.timeTracking).forEach(activityId => {
            const data = this.timeTracking[activityId];
            if (data.totalTime) {
                localStorage.setItem(`timeTracking_${activityId}`, data.totalTime.toString());
            }
        });
    }

    loadSavedTimeTracking() {
        // Load saved times and update displays
        document.querySelectorAll('[id^="timeDisplay-"]').forEach(element => {
            const activityId = element.id.replace('timeDisplay-', '');
            const savedTime = this.getSavedTime(activityId);
            if (savedTime > 0) {
                element.textContent = this.formatTime(savedTime);
            }
        });
    }

    // Drag and Drop Functionality
    initializeDragAndDrop() {
        const activityCards = document.querySelectorAll('.activity-card');
        activityCards.forEach(card => {
            card.draggable = true;
            card.addEventListener('dragstart', (e) => this.handleDragStart(e));
            card.addEventListener('dragend', (e) => this.handleDragEnd(e));
        });
        
        const columns = document.querySelectorAll('#thisWeekActivities, #nextWeekActivities');
        columns.forEach(column => {
            column.addEventListener('dragover', (e) => this.handleDragOver(e));
            column.addEventListener('drop', (e) => this.handleDrop(e));
        });
    }

    handleDragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.activityId);
        e.target.classList.add('dragging');
    }

    handleDragEnd(e) {
        e.target.classList.remove('dragging');
    }

    handleDragOver(e) {
        e.preventDefault();
    }

    handleDrop(e) {
        e.preventDefault();
        const activityId = e.dataTransfer.getData('text/plain');
        const card = document.querySelector(`[data-activity-id="${activityId}"]`);
        const targetColumn = e.currentTarget;
        
        if (card && targetColumn) {
            targetColumn.appendChild(card);
            this.showNotification('Activity moved successfully!', 'success');
            this.saveActivityPosition(activityId, targetColumn.id);
        }
    }

    saveActivityPosition(activityId, columnId) {
        const positions = JSON.parse(localStorage.getItem('activityPositions') || '{}');
        positions[activityId] = columnId;
        localStorage.setItem('activityPositions', JSON.stringify(positions));
    }

    // Status Change and Automation
    updateActivityStatus(activityId, newStatus) {
        const statusBadge = document.querySelector(`[data-activity-id="${activityId}"] .badge`);
        if (statusBadge) {
            statusBadge.className = `badge bg-${newStatus.toLowerCase()}`;
            statusBadge.textContent = newStatus.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
        
        // Trigger automation rules
        this.triggerAutomationRules(activityId, newStatus);
    }

    triggerAutomationRules(activityId, newStatus) {
        if (newStatus === 'in_progress') {
            this.showNotification('Status changed to "Working on it" - Team notified and time tracking started!', 'success');
            // Auto-start time tracking
            if (!this.timeTracking[activityId]) {
                this.toggleTimeTracking(activityId);
            }
        } else if (newStatus === 'completed') {
            this.showNotification('Activity completed! Deal stage updated and stakeholders notified.', 'success');
        }
    }

    // Notification System
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
        
        // Store notification for tracking
        this.notifications.push({
            message,
            type,
            timestamp: new Date()
        });
    }

    // Activity Management
    deleteActivity(activityId) {
        if (confirm('Are you sure you want to delete this activity?')) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/crm/activities/${activityId}/delete`;
            
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

    // Event Listeners
    initializeEventListeners() {
        // Load saved view preference
        this.loadViewPreference();
        
        // Handle window beforeunload to save time tracking
        window.addEventListener('beforeunload', () => {
            this.saveTimeTracking();
        });
        
        // Handle visibility change to pause tracking when tab is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAllTimeTracking();
            }
        });
    }

    pauseAllTimeTracking() {
        Object.keys(this.timeTracking).forEach(activityId => {
            if (this.timeTracking[activityId].isRunning) {
                const timeIcon = document.getElementById(`timeIcon-${activityId}`);
                const timeText = document.getElementById(`timeText-${activityId}`);
                if (timeIcon && timeText) {
                    this.stopTimeTracking(activityId, timeIcon, timeText);
                }
            }
        });
    }

    // Utility Methods
    getActivityById(activityId) {
        return document.querySelector(`[data-activity-id="${activityId}"]`);
    }

    refreshActivityCard(activityId) {
        const card = this.getActivityById(activityId);
        if (card) {
            card.classList.add('loading');
            setTimeout(() => {
                card.classList.remove('loading');
            }, 500);
        }
    }

    // Export for global access
    static getInstance() {
        if (!TaskBoard.instance) {
            TaskBoard.instance = new TaskBoard();
        }
        return TaskBoard.instance;
    }
}

// Global functions for HTML onclick handlers
function toggleTimeTracking(activityId) {
    TaskBoard.getInstance().toggleTimeTracking(activityId);
}

function deleteActivity(activityId) {
    TaskBoard.getInstance().deleteActivity(activityId);
}

function updateActivityStatus(activityId, newStatus) {
    TaskBoard.getInstance().updateActivityStatus(activityId, newStatus);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    TaskBoard.getInstance();
}); 