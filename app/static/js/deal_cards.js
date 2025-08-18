// /static/js/deal_cards.js

document.addEventListener('DOMContentLoaded', function () {
    const dealCards = document.querySelectorAll('.deal-card');
    // --- THIS IS THE FIX: Use the new class name ---
    const stageContainers = document.querySelectorAll('.kanban-cards-container');
    let draggedItem = null;

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
        card.addEventListener('dragstart', (e) => {
            draggedItem = card;
            setTimeout(() => card.classList.add('dragging'), 0);
            e.dataTransfer.effectAllowed = 'move';
        });

        card.addEventListener('dragend', () => {
            draggedItem.classList.remove('dragging');
        });
    });

    // --- Drop Handlers for Containers ---
    stageContainers.forEach(container => {
        container.addEventListener('dragover', (e) => {
            e.preventDefault(); // Necessary to allow dropping
            container.classList.add('drag-over');
        });

        container.addEventListener('dragleave', () => {
            container.classList.remove('drag-over');
        });

        container.addEventListener('drop', (e) => {
            e.preventDefault();
            container.classList.remove('drag-over');
            if (draggedItem) {
                const dealId = draggedItem.dataset.dealId;
                const newStage = container.dataset.stage;

                // Move the card in the UI first for responsiveness
                container.appendChild(draggedItem);

                // Then, save the change to the server
                updateDealStage(dealId, newStage);
            }
        });
    });

    // --- Function to update the deal stage via fetch ---
    function updateDealStage(dealId, newStage) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch(`/deals/update_stage/${dealId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                stage: newStage
            })
        })
        .then(response => {
            if (!response.ok) {
                alert('Error: Could not save the new deal stage. Please refresh the page.');
                throw new Error('Server responded with an error.');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log(`Deal ${dealId} successfully moved to ${newStage}.`);
                // Here you could trigger a small success notification if desired
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
    }
});