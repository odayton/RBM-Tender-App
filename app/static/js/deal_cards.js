// deal_cards.js

document.addEventListener('DOMContentLoaded', function () {
    const dealCards = document.querySelectorAll('.deal-card');
    const stageContainers = document.querySelectorAll('.stage-container');

    dealCards.forEach(card => {
        card.addEventListener('dragstart', function (e) {
            e.dataTransfer.setData('text/plain', card.getAttribute('data-deal-id'));
        });
    });

    stageContainers.forEach(container => {
        container.addEventListener('dragover', function (e) {
            e.preventDefault();
            container.style.backgroundColor = '#37779e'; // highlight drop area
        });

        container.addEventListener('dragleave', function (e) {
            container.style.backgroundColor = ''; // remove highlight
        });

        container.addEventListener('drop', function (e) {
            e.preventDefault();
            const dealId = e.dataTransfer.getData('text/plain');
            const draggedCard = document.querySelector(`[data-deal-id="${dealId}"]`);
            container.appendChild(draggedCard);
            container.style.backgroundColor = ''; // remove highlight

            // Make an AJAX call to update the backend with the new stage
            const newStage = container.id.replace('-stage', '');
            updateDealStage(dealId, newStage);
        });
    });
});

function updateDealStage(dealId, newStage) {
    fetch('/update_deal_stage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ dealId: dealId, newStage: newStage }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Deal stage updated successfully.');
        } else {
            console.error('Error updating deal stage.');
        }
    });
}

document.querySelectorAll('.deal-card').forEach(function(card) {
    card.addEventListener('dragstart', function(e) {
        e.dataTransfer.setData('text/plain', this.dataset.dealId);
    });

    card.addEventListener('click', function(e) {
        if (e.defaultPrevented) return; // If the click was part of a drag, don't follow the link
    });
});
