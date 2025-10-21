// /static/js/deal_cards.js

document.addEventListener('DOMContentLoaded', function () {
    console.log('Deal cards script loaded');
    
    // Function to initialize drag and drop
    function initializeDragAndDrop() {
        const dealCards = document.querySelectorAll('.deal-card');
        const stageContainers = document.querySelectorAll('.kanban-cards-container');
        let draggedItem = null;

        console.log(`Found ${dealCards.length} deal cards`);
        console.log(`Found ${stageContainers.length} stage containers`);

        // --- Add a style for visual feedback during drag ---
        const style = document.createElement('style');
        style.innerHTML = `
            .deal-card.dragging {
                opacity: 0.5;
                border: 2px dashed #fff;
            }
            .kanban-cards-container.drag-over {
                border: 2px dashed #007bff;
                background-color: #333;
            }
        `;
        document.head.appendChild(style);

        // --- Drag Handlers for Cards ---
        dealCards.forEach(card => {
            let isDragging = false;
            
            card.addEventListener('dragstart', (e) => {
                console.log('Drag started on card:', card.dataset.dealId);
                isDragging = true;
                draggedItem = card;
                setTimeout(() => card.classList.add('dragging'), 0);
                e.dataTransfer.effectAllowed = 'move';
                
                // Disable the link during drag
                const link = card.querySelector('a');
                if (link) {
                    link.style.pointerEvents = 'none';
                }
            });

            card.addEventListener('dragend', () => {
                console.log('Drag ended');
                isDragging = false;
                if (draggedItem) {
                    draggedItem.classList.remove('dragging');
                    
                    // Re-enable the link after drag
                    const link = draggedItem.querySelector('a');
                    if (link) {
                        link.style.pointerEvents = 'auto';
                    }
                }
            });
            
            // Handle click to prevent navigation during drag
            card.addEventListener('click', (e) => {
                if (isDragging) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            });
        });

        // --- Drop Handlers for Containers ---
        stageContainers.forEach(container => {
            console.log('Setting up drop handlers for container:', container.dataset.stage);
            
            container.addEventListener('dragover', (e) => {
                e.preventDefault(); // Necessary to allow dropping
                container.classList.add('drag-over');
            });

            container.addEventListener('dragleave', (e) => {
                // Only remove drag-over if we're actually leaving the container
                if (!container.contains(e.relatedTarget)) {
                    container.classList.remove('drag-over');
                }
            });

            container.addEventListener('drop', (e) => {
                e.preventDefault();
                container.classList.remove('drag-over');
                
                console.log('Drop event triggered');
                console.log('Dragged item:', draggedItem);
                console.log('Target stage:', container.dataset.stage);
                
                if (draggedItem) {
                    const dealId = draggedItem.dataset.dealId;
                    const newStage = container.dataset.stage;
                    
                    // Get the old container before moving the card
                    const oldContainer = draggedItem.closest('.kanban-cards-container');

                    console.log(`Moving deal ${dealId} to stage ${newStage}`);

                    // Move the card in the UI first for responsiveness
                    container.appendChild(draggedItem);
                    
                    // Update the counts immediately for better UX
                    updateStageCounts(oldContainer, container);

                    // Then, save the change to the server
                    updateDealStage(dealId, newStage);
                }
            });
        });
    }

    // Initialize immediately
    initializeDragAndDrop();

    // Also re-initialize if new cards are added dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check if any new deal cards were added
                const hasNewCards = Array.from(mutation.addedNodes).some(node => 
                    node.nodeType === 1 && node.classList && node.classList.contains('deal-card')
                );
                if (hasNewCards) {
                    console.log('New deal cards detected, re-initializing drag and drop');
                    initializeDragAndDrop();
                }
            }
        });
    });

    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // --- Function to update stage counts in the column headers ---
    function updateStageCounts(oldContainer, newContainer) {
        // Update old container count
        if (oldContainer) {
            const oldHeader = oldContainer.previousElementSibling;
            if (oldHeader) {
                const oldCountBadge = oldHeader.querySelector('span[class*="bg-blue-600"]');
                if (oldCountBadge) {
                    const oldCount = oldContainer.querySelectorAll('.deal-card').length;
                    oldCountBadge.textContent = oldCount;
                    console.log(`Updated old container count to ${oldCount}`);
                    
                    // Show/hide empty state
                    updateEmptyState(oldContainer, oldCount);
                }
            }
        }
        
        // Update new container count
        if (newContainer) {
            const newHeader = newContainer.previousElementSibling;
            if (newHeader) {
                const newCountBadge = newHeader.querySelector('span[class*="bg-blue-600"]');
                if (newCountBadge) {
                    const newCount = newContainer.querySelectorAll('.deal-card').length;
                    newCountBadge.textContent = newCount;
                    console.log(`Updated new container count to ${newCount}`);
                    
                    // Show/hide empty state
                    updateEmptyState(newContainer, newCount);
                }
            }
        }
    }
    
    // --- Function to show/hide empty state message ---
    function updateEmptyState(container, count) {
        // Remove existing empty state if present
        const existingEmpty = container.querySelector('.flex.flex-col.items-center.justify-center');
        if (existingEmpty) {
            existingEmpty.remove();
        }
        
        // Add empty state if no cards
        if (count === 0) {
            const emptyState = document.createElement('div');
            emptyState.className = 'flex flex-col items-center justify-center py-8 text-gray-500';
            emptyState.innerHTML = `
                <i class="fas fa-inbox text-2xl mb-2 opacity-30"></i>
                <p class="text-xs">No deals in this stage</p>
            `;
            container.appendChild(emptyState);
        }
    }

    // --- Function to update the deal stage via fetch ---
    function updateDealStage(dealId, newStage) {
        console.log(`Updating deal ${dealId} to stage ${newStage}`);
        
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        
        if (!csrfToken) {
            console.error('CSRF token not found');
            alert('Error: Security token not found. Please refresh the page.');
            return;
        }

        fetch(`/deals/update_stage/${dealId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken.getAttribute('content')
            },
            body: JSON.stringify({
                stage: newStage
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                console.log(`Deal ${dealId} successfully moved to ${newStage}.`);
                // Show success notification
                showNotification(`Deal moved to ${newStage}`, 'success');
            } else {
                console.error('Server error:', data.error);
                alert(`Error: ${data.error}`);
                // Optionally revert the UI change here
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert(`Error: Could not save the new deal stage. ${error.message}`);
            // Optionally revert the UI change here
        });
    }

    // Simple notification function
    function showNotification(message, type = 'info') {
        // Create a simple notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} notification-toast`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
});