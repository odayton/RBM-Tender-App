document.addEventListener('DOMContentLoaded', function() {
    const lineItemsTable = document.getElementById('line-items-table');
    const accessoryModal = document.getElementById('accessoryModal');
    let currentPumpId = null;

    // Listen for modal opening
    $('#accessoryModal').on('show.bs.modal', function (event) {
        const button = event.relatedTarget; // Button that triggered the modal
        currentPumpId = button.getAttribute('data-pump-id');
        console.log('Modal opened for pump ID:', currentPumpId);
    });

    // Handle save accessories button click
    document.getElementById('saveAccessories').addEventListener('click', function() {
        const selectedAccessories = [];
        document.querySelectorAll('#accessoryModal .form-check-input:checked').forEach(checkbox => {
            selectedAccessories.push(checkbox.value);
        });
        
        if (currentPumpId) {
            updateAccessories(currentPumpId, selectedAccessories);
        }
        
        $('#accessoryModal').modal('hide');
    });

    function updateAccessories(pumpId, accessories) {
        const pumpRow = lineItemsTable.querySelector(`.pump-row[data-pump-id="${pumpId}"]`);
        
        // Clear existing accessories
        const existingAccessories = pumpRow.nextElementSibling;
        if (existingAccessories && existingAccessories.classList.contains('accessory-row')) {
            existingAccessories.remove();
        }
        
        if (accessories.length > 0) {
            const accessoryRow = document.createElement('tr');
            accessoryRow.classList.add('accessory-row');
            accessoryRow.dataset.pumpId = pumpId;
            
            const accessoryCell = document.createElement('td');
            accessoryCell.colSpan = 7;
            accessoryCell.innerHTML = `<div class="selected-accessories">${accessories.join(', ')}</div>`;
            
            accessoryRow.appendChild(accessoryCell);
            pumpRow.insertAdjacentElement('afterend', accessoryRow);
            
            // Update the button text
            const button = pumpRow.querySelector('.accessory-toggle');
            button.textContent = 'Edit Accessories';
        } else {
            // Reset the button text if no accessories are selected
            const button = pumpRow.querySelector('.accessory-toggle');
            button.textContent = 'Add Accessories';
        }
    }

    // Reset checkboxes when modal is hidden
    $('#accessoryModal').on('hidden.bs.modal', function () {
        document.querySelectorAll('#accessoryModal .form-check-input').forEach(checkbox => {
            checkbox.checked = false;
        });
        currentPumpId = null;
    });

    // For debugging: log when the script has loaded
    console.log('checkboxes.js loaded and running');
});