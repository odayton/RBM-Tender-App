// /static/js/checkboxes.js

document.addEventListener('DOMContentLoaded', () => {
    const accessoryModal = document.getElementById('accessoryModal');
    if (!accessoryModal) {
        return; // Exit if the modal isn't on this page
    }

    let currentPumpId = null;

    // Use event delegation on the modal for the 'show.bs.modal' event
    // This is the vanilla JS equivalent of jQuery's $('...').on('show.bs.modal', ...)
    // Note: Bootstrap 4's jQuery events can be tricky. This relies on the event bubbling up.
    // If this proves unreliable, a MutationObserver on the modal's style/class is a more robust alternative.
    accessoryModal.addEventListener('show.bs.modal', (event) => {
        // The button that triggered the modal
        const button = event.relatedTarget;
        
        // Extract info from data-* attributes
        currentPumpId = button.getAttribute('data-pump-id');
        console.log('Modal opened for pump ID:', currentPumpId);
        
        if (currentPumpId) {
            fetchAccessoriesForPump(currentPumpId);
        }
    });

    // Add event listener to the "Save changes" button
    const saveButton = document.getElementById('saveAccessories');
    if(saveButton) {
        saveButton.addEventListener('click', () => {
            if (currentPumpId) {
                saveAccessoriesForPump(currentPumpId);
            }
        });
    }

    // --- Functions ---

    function fetchAccessoriesForPump(pumpId) {
        // Start by unchecking all boxes
        const checkboxes = accessoryModal.querySelectorAll('.form-check-input');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        fetch(`/deals/get_accessories/${pumpId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetched accessories:', data.accessories);
                // Check the boxes based on the response
                data.accessories.forEach(accessory => {
                    const checkbox = document.querySelector(`input[type="checkbox"][value="${accessory}"]`);
                    if (checkbox) {
                        checkbox.checked = true;
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching accessories:', error);
                // In a real app, you'd show an error message to the user here.
            });
    }

    function saveAccessoriesForPump(pumpId) {
        const selectedAccessories = [];
        const checkboxes = accessoryModal.querySelectorAll('.form-check-input:checked');
        checkboxes.forEach(checkbox => {
            selectedAccessories.push(checkbox.value);
        });

        console.log('Saving accessories for pump ID:', pumpId, selectedAccessories);

        fetch(`/deals/save_accessories/${pumpId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ accessories: selectedAccessories }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('Accessories saved successfully!');
                // Close the modal - requires access to the Bootstrap modal instance
                // This is a known difficulty when removing jQuery from Bootstrap 4.
                // A simple approach is to find the close button and click it.
                const closeButton = accessoryModal.querySelector('[data-dismiss="modal"]');
                if(closeButton) {
                    closeButton.click();
                }
            } else {
                console.error('Failed to save accessories:', data.error);
            }
        })
        .catch(error => {
            console.error('Error saving accessories:', error);
        });
    }
});