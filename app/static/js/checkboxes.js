function logToServer(message) {
    fetch('/log', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    }).catch(error => console.error('Error logging to server:', error));
}

logToServer('checkboxes.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    logToServer('DOM fully loaded and parsed');
    const lineItemsTable = document.getElementById('line-items-table');
    const accessoryModal = document.getElementById('accessoryModal');
    let currentPumpId = null;
    let currentPumpData = null;

    if (!accessoryModal) {
        logToServer('Accessory modal not found in the DOM');
    }

    // Listen for modal opening
    $('#accessoryModal').on('show.bs.modal', function (event) {
        logToServer('Accessory modal is opening');
        const button = event.relatedTarget;
        currentPumpId = button.getAttribute('data-pump-id');
        logToServer('Current pump ID: ' + currentPumpId);
        fetchPumpData(currentPumpId);
    });

   // Handle save accessories button click
   const saveAccessoriesButton = document.getElementById('saveAccessories');
   if (saveAccessoriesButton) {
       logToServer('Save Accessories button found');
       saveAccessoriesButton.addEventListener('click', function(event) {
           logToServer('Save Accessories button clicked');
           event.preventDefault(); // Prevent default form submission
           const selectedAccessories = [];
           document.querySelectorAll('#accessoryModal .form-check-input:checked').forEach(checkbox => {
               selectedAccessories.push(checkbox.value);
           });
           
           logToServer('Selected accessories: ' + selectedAccessories.join(', '));
           logToServer('Current pump ID: ' + currentPumpId);
           logToServer('Current pump data: ' + JSON.stringify(currentPumpData));
           
           if (currentPumpId && currentPumpData) {
               logToServer('Processing accessories for pump: ' + currentPumpId);
               processSelectedAccessories(currentPumpId, selectedAccessories, currentPumpData);
           } else {
               logToServer('Current pump data is missing. Pump ID: ' + currentPumpId);
           }
           
           logToServer('Hiding accessory modal');
           $('#accessoryModal').modal('hide');
       });
   } else {
       logToServer('Save Accessories button not found');
   }


    function fetchPumpData(pumpId) {
        alert('Fetching pump data for pump ID: ' + pumpId);
        fetch(`/get-pump-data/${pumpId}`)
            .then(response => response.json())
            .then(data => {
                currentPumpData = data;
                alert('Fetched pump data: ' + JSON.stringify(currentPumpData));
            })
            .catch(error => alert('Error fetching pump data: ' + error));
    }

    function processSelectedAccessories(pumpId, accessories, pumpData) {
        alert('Processing selected accessories for pump: ' + pumpId);
        accessories.forEach(accessory => {
            alert('Processing accessory: ' + accessory);
            switch(accessory) {
                case 'inertia_base':
                    addInertiaBase(pumpId, pumpData);
                    break;
                case 'seismic_springs':
                    addSeismicSprings(pumpId, pumpData);
                    break;
                default:
                    alert('Unknown accessory type: ' + accessory);
            }
        });
        updateAccessoriesDisplay(pumpId, accessories);
    }

    function addInertiaBase(pumpId, pumpData) {
        alert('Adding inertia base for pump: ' + pumpId);
        const requiredWeight = pumpData.weight * 1.5;
        const requiredLength = pumpData.length + 100;
        const requiredWidth = pumpData.width + 100;

        fetch(`/get-suitable-inertia-base`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                weight: requiredWeight,
                length: requiredLength,
                width: requiredWidth
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Received inertia base data: ' + JSON.stringify(data));
            if (data.suitable_base) {
                addLineItem(pumpId, 'Inertia Base', data.suitable_base.PartNumber, data.suitable_base.Cost);
            } else {
                alert('No suitable inertia base found, adding generic');
                addLineItem(pumpId, 'Inertia Base', 'GENERIC-IB', 1000);
            }
        })
        .catch(error => alert('Error adding inertia base: ' + error));
    }

    function addSeismicSprings(pumpId, pumpData) {
        alert('Adding seismic springs for pump: ' + pumpId);
        fetch(`/get-suitable-seismic-springs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pump_weight: pumpData.weight,
                inertia_base_weight: pumpData.inertia_base_weight || 0,
                spring_amount: pumpData.spring_amount || 4
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Received seismic springs data: ' + JSON.stringify(data));
            if (data.suitable_springs) {
                addLineItem(pumpId, 'Seismic Springs', data.suitable_springs.PartNumber, data.suitable_springs.Cost);
            } else {
                alert('No suitable seismic springs found, adding generic');
                addLineItem(pumpId, 'Seismic Springs', 'GENERIC-SS', 500);
            }
        })
        .catch(error => alert('Error adding seismic springs: ' + error));
    }

    function addLineItem(pumpId, accessoryType, partNumber, cost) {
        alert('Adding line item: ' + accessoryType + ', ' + partNumber + ', ' + cost);
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${accessoryType}</td>
            <td></td>
            <td></td>
            <td>${partNumber}</td>
            <td>1</td>
            <td></td>
            <td>${cost}</td>
        `;
        const pumpRow = document.querySelector(`tr[data-pump-id="${pumpId}"]`);
        if (pumpRow) {
            pumpRow.parentNode.insertBefore(newRow, pumpRow.nextSibling);
            alert('Line item added successfully');
        } else {
            alert('Pump row not found for pump ID: ' + pumpId);
        }
    }

    function updateAccessoriesDisplay(pumpId, accessories) {
        alert('Updating accessories display for pump: ' + pumpId);
        const pumpRow = lineItemsTable.querySelector(`.pump-row[data-pump-id="${pumpId}"]`);
        if (pumpRow) {
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
                
                const button = pumpRow.querySelector('.accessory-toggle');
                if (button) {
                    button.textContent = 'Edit Accessories';
                }
                alert('Accessories display updated');
            } else {
                const button = pumpRow.querySelector('.accessory-toggle');
                if (button) {
                    button.textContent = 'Add Accessories';
                }
                alert('No accessories to display');
            }
        } else {
            alert('Pump row not found for pump ID: ' + pumpId);
        }
    }

    // Reset checkboxes and data when modal is hidden
    $('#accessoryModal').on('hidden.bs.modal', function () {
        alert('Accessory modal is closing');
        document.querySelectorAll('#accessoryModal .form-check-input:checked').forEach(checkbox => {
            checkbox.checked = false;
        });
        currentPumpId = null;
        currentPumpData = null;
    });
});