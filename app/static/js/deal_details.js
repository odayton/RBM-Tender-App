// JS to set the revision ID when opening the modal
$('#addLineItemModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);  // Button that triggered the modal
    var revisionId = button.data('revision-id');  // Extract revision ID
    var modal = $(this);
    modal.find('#modalRevisionId').val(revisionId);  // Set revision ID in modal

    // Get entity type and entity ID from the Contact/Company modal dropdowns
    var entityType = $('#entityType').val();  // Entity type: contact or company
    var entityId = $('#entityId').val();      // Entity ID: selected contact or company
    var dealId = $('#dealId').val();  // Hidden input or set it dynamically

    // Construct the correct URL for form action
    if (dealId && entityType && entityId) {
        var actionUrl = `/add_line_item/${dealId}/${entityType}/${entityId}`;
        modal.find('form').attr('action', actionUrl);
    } else {
        console.error("Entity type, entity ID, or deal ID is missing.");
    }
});

// Change the entity dropdown based on selected entity type (contact/company)
$('#entityType').change(function() {
    var entityType = $(this).val();
    var optionsHtml = '';
    
    if (entityType === 'contact') {
        optionsHtml = '{% for contact in all_contacts %}<option value="{{ contact.id }}">{{ contact.representative_name }}</option>{% endfor %}';
    } else if (entityType === 'company') {
        optionsHtml = '{% for company in all_companies %}<option value="{{ company.id }}">{{ company.company_name }}</option>{% endfor %}';
    }

    $('#entityId').html(optionsHtml);  // Update the dropdown options dynamically
});

// Function to dynamically add a new revision
function addNewRevision() {
    // Simulate dynamically adding a new revision tab
    const revisionsContainer = document.querySelector('.mb-3');  // Where the revisions are listed
    const revisionCount = revisionsContainer.querySelectorAll('.btn-primary').length;  // Current count of revision buttons

    // Create a new revision button
    const newRevisionButton = document.createElement('button');
    newRevisionButton.classList.add('btn', 'btn-primary', 'ml-2');
    newRevisionButton.textContent = `Rev ${revisionCount}.0`;

    // Append it to the revisions list
    revisionsContainer.appendChild(newRevisionButton);
}
