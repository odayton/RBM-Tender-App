document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation to handle clicks on any 'Add to Option' button
    document.body.addEventListener('click', function(event) {
        // Check if the clicked element is our button
        if (!event.target.classList.contains('add-assembly-btn')) {
            return;
        }

        const button = event.target;
        const assemblyId = button.dataset.assemblyId;
        const optionId = button.dataset.optionId;
        
        // Find the CSRF token from the form on the page
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        // Disable the button to prevent multiple clicks
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';

        fetch('/hvac/api/add-assembly-to-option', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                assembly_id: assemblyId,
                option_id: optionId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.innerHTML = '<i class="fas fa-check"></i> Added';
                button.classList.remove('btn-success');
                button.classList.add('btn-secondary');
            } else {
                // On failure, re-enable the button and show an error
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
                alert('Error adding assembly: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Fetch Error:', error);
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
            alert('A network error occurred. Please try again.');
        });
    });
});