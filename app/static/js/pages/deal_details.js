document.addEventListener('DOMContentLoaded', function() {

    // --- Modal Activation Logic (No Changes Needed Here) ---
    $('#addRevisionModal').on('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const recipientId = button.getAttribute('data-recipient-id');
        const recipientName = button.getAttribute('data-recipient-name');
        const modal = $(this);
        modal.find('#modalRecipientName').text(recipientName);
        modal.find('#modalRecipientId').val(recipientId);
    });

    $('input[name="creation_method"]').on('change', function() {
        if (this.value === 'clone_other') {
            $('#cloneSourceWrapper').slideDown();
        } else {
            $('#cloneSourceWrapper').slideUp();
        }
    });

    $('#addOptionModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const quoteId = button.data('quote-id');
        const form = $('#addOptionForm');
        const actionUrl = `/deals/quote_option/add/${quoteId}`;
        form.attr('action', actionUrl);
    });

    $('#editOptionModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const optionId = button.data('option-id');
        const optionName = button.data('option-name');
        const form = $('#editOptionForm');
        const actionUrl = `/deals/quote_option/update/${optionId}`;
        form.attr('action', actionUrl);
        form.find('#edit_option_name').val(optionName);
    });

    $('#addItemModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const optionId = button.data('option-id');
        const form = $('#addItemForm');
        const actionUrl = `/deals/line_item/add/${optionId}`;
        form.attr('action', actionUrl);
    });

    $('#editItemModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const itemId = button.data('item-id');
        const description = button.data('item-description');
        const quantity = button.data('item-quantity');
        const unitPrice = button.data('item-unit-price');
        const form = $('#editItemForm');
        const actionUrl = `/deals/line_item/update/${itemId}`;
        form.attr('action', actionUrl);
        form.find('#edit_description').val(description);
        form.find('#edit_quantity').val(quantity);
        form.find('#edit_unit_price').val(unitPrice);
    });

    // --- Delete Confirmation Dialogs (No Changes Needed Here) ---
    $('.delete-item-form, .delete-option-form, .delete-revision-form').on('submit', function(event) {
        let message = 'Are you sure you want to delete this?';
        if ($(this).hasClass('delete-revision-form')) {
            message = 'Are you sure you want to delete this entire revision and all of its contents? This action cannot be undone.';
        } else if ($(this).hasClass('delete-option-form')) {
            message = 'Are you sure you want to delete this option? This can only be done if it has no line items.';
        }
        if (!confirm(message)) {
            event.preventDefault();
        }
    });

    // --- NEW: Logic for Tabs and Nested Accordions ---
    // For each quote stream panel on the page...
    $('.quote-stream-panel').each(function() {
        // Find the first revision tab and its corresponding content pane, and make them active.
        const firstTab = $(this).find('.nav-link').first();
        const firstPane = $(this).find('.tab-pane').first();
        
        if (firstTab.length) {
            firstTab.addClass('active');
            firstTab.attr('aria-selected', 'true');
        }
        if (firstPane.length) {
            firstPane.addClass('show active');
        }
        
        // Inside that *now active* pane, find its nested accordion for options...
        const activeOptionsAccordion = firstPane.find('.accordion');
        // ...and expand the first option within it.
        if (activeOptionsAccordion.length) {
            activeOptionsAccordion.find('.collapse').first().addClass('show');
        }
    });

});