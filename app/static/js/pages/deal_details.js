document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    const dealId = document.querySelector('[data-deal-id]')?.dataset.dealId;

    // --- PRODUCT SEARCH LOGIC ---
    const searchInput = document.getElementById('productSearchInput');
    const searchResultsContainer = document.getElementById('productSearchResults');
    const addItemForm = document.getElementById('addItemForm');
    let searchTimeout;

    if (searchInput && searchResultsContainer && addItemForm) {
        searchInput.addEventListener('input', function () {
            const query = this.value.trim();
            clearTimeout(searchTimeout);

            if (query.length < 2) {
                searchResultsContainer.innerHTML = '';
                return;
            }

            searchTimeout = setTimeout(() => {
                fetch(`/deals/api/products/search?q=${query}`)
                    .then(response => response.json())
                    .then(data => displaySearchResults(data))
                    .catch(error => console.error('Error fetching products:', error));
            }, 300);
        });
    }

    function displaySearchResults(products) {
        searchResultsContainer.innerHTML = '';
        if (products.length === 0) {
            searchResultsContainer.innerHTML = '<div class="search-result-item p-2 text-muted">No products found</div>';
        } else {
            products.forEach(product => {
                const item = document.createElement('div');
                item.className = 'search-result-item p-2 border-bottom';
                item.style.cursor = 'pointer';
                item.textContent = `${product.sku} - ${product.name}`;
                
                item.dataset.productId = product.id;
                item.dataset.sku = product.sku;
                item.dataset.name = product.name;
                item.dataset.unitPrice = product.unit_price;
                item.dataset.discount = product.discount || '0';

                item.addEventListener('click', function () {
                    populateAddItemForm(this.dataset);
                    searchResultsContainer.innerHTML = '';
                    if (searchInput) searchInput.value = '';
                });
                searchResultsContainer.appendChild(item);
            });
        }
    }

    function populateAddItemForm(dataset) {
        addItemForm.querySelector('#item_sku_display').value = dataset.sku;
        addItemForm.querySelector('#item_name_display').value = dataset.name;
        
        addItemForm.querySelector('input[name="product_id"]').value = dataset.productId;
        addItemForm.querySelector('textarea[name="notes"]').value = dataset.name;
        addItemForm.querySelector('input[name="unit_price"]').value = dataset.unitPrice;
        addItemForm.querySelector('input[name="discount"]').value = dataset.discount;
        addItemForm.querySelector('input[name="quantity"]').value = 1;
    }

    document.addEventListener('click', function (e) {
        if (searchResultsContainer && !searchResultsContainer.contains(e.target) && e.target !== searchInput) {
            searchResultsContainer.innerHTML = '';
        }
    });

    // --- MODAL & FORM HANDLING LOGIC ---
    // This is the key fix: Set the form's action URL when the modal is opened.
    $('#addItemModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const optionId = button.data('option-id');
        const actionUrl = `/deals/line_item/add/${optionId}`;
        $('#addItemForm').attr('action', actionUrl);

        // Clear the form when opening the modal
        $('#addItemForm')[0].reset();
        $('#item_sku_display').val('');
        $('#item_name_display').val('');
        $('#productSearchResults').empty();
    });

    // --- YOUR EXISTING INLINE EDITING, DRAG-DROP, AND OTHER MODAL LOGIC ---
    // (This part of your code is correct and should remain)
    function makeEditable(element) {
        if (element.querySelector('input')) return;
        const originalText = element.textContent.trim();
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control form-control-sm';
        input.value = originalText;
        element.innerHTML = '';
        element.appendChild(input);
        input.focus();
        function saveChanges() {
            const newValue = input.value;
            element.textContent = originalText;
            if (newValue === originalText) return;
            const model = element.dataset.model;
            const id = element.dataset.id;
            const field = element.dataset.field;
            let apiUrl = '';
            if (model === 'line_item') {
                apiUrl = `/deals/api/line-item/${id}/update-field`;
            } else if (model === 'quote_option') {
                apiUrl = `/deals/api/quote-option/${id}/update-field`;
            }
            if (!apiUrl) return;
            fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ field: field, value: newValue })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    element.textContent = newValue;
                    if (field === 'custom_name' && data.newState) {
                        const row = element.closest('tr');
                        const skuCell = row.querySelector('[data-field="sku"]');
                        if (skuCell) skuCell.textContent = data.newState.sku;
                    }
                    const optionCard = element.closest('.option-card');
                    if(optionCard) calculateTotalsForOption(optionCard);
                } else {
                    alert('Error: ' + data.message);
                    element.textContent = originalText;
                }
            })
            .catch(() => {
                alert('An error occurred while saving.');
                element.textContent = originalText;
            });
        }
        input.addEventListener('blur', saveChanges);
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') input.blur();
            if (e.key === 'Escape') element.textContent = originalText;
        });
    }
    document.querySelectorAll('.editable').forEach(el => el.addEventListener('click', (e) => {
        e.stopPropagation();
        makeEditable(el);
    }));

    function calculateTotalsForOption(optionCard) {
        let subtotal = 0;
        optionCard.querySelectorAll('.line-items-table tbody tr').forEach(row => {
            const qty = parseFloat(row.querySelector('[data-field="quantity"]').textContent) || 0;
            const price = parseFloat(row.querySelector('[data-field="unit_price"]').textContent.replace(/,/g, '')) || 0;
            const discount = parseFloat(row.querySelector('[data-field="discount"]').textContent) || 0;
            const lineTotal = qty * (price * (1 - discount / 100));
            row.querySelector('.line-total').textContent = lineTotal.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' });
            subtotal += lineTotal;
        });
        const freight = parseFloat(optionCard.querySelector('.freight-value').textContent.replace(/,/g, '')) || 0;
        const grandTotal = subtotal + freight;
        optionCard.querySelector('.subtotal-value').textContent = subtotal.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' });
        optionCard.querySelector('.total-value').textContent = grandTotal.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' });
    }
    document.querySelectorAll('.option-card').forEach(calculateTotalsForOption);

    // --- Sortable Rows Logic ---
    // Check if Sortable is available before using it
    try {
        // Wait a bit for the script to load if it's not immediately available
        if (typeof Sortable !== 'undefined') {
            initializeSortable();
        } else {
            // Try to wait for the script to load
            setTimeout(() => {
                if (typeof Sortable !== 'undefined') {
                    initializeSortable();
                } else {
                    console.warn('Sortable library not loaded. Drag and drop functionality will be disabled.');
                }
            }, 100);
        }
    } catch (error) {
        console.warn('Error initializing Sortable:', error);
        console.warn('Drag and drop functionality will be disabled.');
    }

    function initializeSortable() {
        document.querySelectorAll('.sortable-items').forEach(tbody => {
            new Sortable(tbody, {
                animation: 150,
                handle: '.drag-handle',
                onEnd: function (evt) {
                    const optionId = evt.from.closest('.line-items-table').dataset.optionId;
                    const orderedIds = Array.from(evt.from.children).map(row => row.dataset.itemId);
                    fetch(`/deals/api/quote-option/${optionId}/reorder-items`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                        body: JSON.stringify({ ordered_ids: orderedIds })
                    });
                }
            });
        });
    }

    // --- Revision Creation Modal Logic ---
    // This section handles the revision creation functionality independently of Sortable
    $('#addRevisionModal').on('show.bs.modal', function(e) {
        const button = e.relatedTarget;
        console.log('=== ADD REVISION MODAL DEBUG START ===');
        console.log('Add revision modal opened');
        console.log('Button:', button);
        console.log('Button dataset:', button.dataset);
        
        // Try multiple ways to get the recipient ID
        let recipientId = button.dataset.recipientId;
        let recipientName = button.dataset.recipientName;
        
        // Fallback: try jQuery data method
        if (!recipientId) {
            recipientId = $(button).data('recipient-id');
            recipientName = $(button).data('recipient-name');
        }
        
        // Fallback: try getAttribute method
        if (!recipientId) {
            recipientId = button.getAttribute('data-recipient-id');
            recipientName = button.getAttribute('data-recipient-name');
        }
        
        console.log('Recipient ID (final):', recipientId);
        console.log('Recipient Name (final):', recipientName);
        
        if (!recipientId) {
            console.error('ERROR: No recipient ID found in button dataset');
            console.error('Available dataset keys:', Object.keys(button.dataset));
            console.error('Available attributes:', button.attributes);
            alert('Error: Could not determine recipient ID. Please refresh the page and try again.');
            return;
        }
        
        // Set the values in the modal
        $(this).find('#modalRecipientName').text(recipientName || 'Unknown');
        $(this).find('#modalRecipientId').val(recipientId);
        
        // Verify the value was set
        const setValue = $(this).find('#modalRecipientId').val();
        console.log('Modal recipient ID value after setting:', setValue);
        console.log('Modal recipient name after setting:', $(this).find('#modalRecipientName').text());
        console.log('=== ADD REVISION MODAL DEBUG END ===');
    });
    
    // Add form validation for the add revision form
    $('#addRevisionForm').on('submit', function(e) {
        console.log('=== FORM SUBMISSION DEBUG START ===');
        const recipientId = $('#modalRecipientId').val();
        const creationMethod = $('input[name="creation_method"]:checked').val();
        const csrfToken = $('input[name="csrf_token"]').val();
        
        console.log('Form submission - recipient_id:', recipientId);
        console.log('Form submission - creation_method:', creationMethod);
        console.log('Form submission - csrf_token:', csrfToken ? 'Present' : 'Missing');
        console.log('Form action:', $(this).attr('action'));
        console.log('Form method:', $(this).attr('method'));
        
        // Log all form data
        const formData = new FormData(this);
        for (let [key, value] of formData.entries()) {
            console.log(`Form data - ${key}:`, value);
        }
        
        if (!recipientId) {
            console.error('ERROR: Recipient ID is missing');
            e.preventDefault();
            alert('Error: Recipient ID is missing. Please try refreshing the page and try again.');
            return false;
        }
        
        if (!creationMethod) {
            console.error('ERROR: Creation method is missing');
            e.preventDefault();
            alert('Error: Please select a creation method.');
            return false;
        }
        
        if (!csrfToken) {
            console.error('ERROR: CSRF token is missing');
            e.preventDefault();
            alert('Error: Security token is missing. Please refresh the page and try again.');
            return false;
        }
        
        if (creationMethod === 'clone_other') {
            const sourceQuoteId = $('select[name="source_quote_id"]').val();
            if (!sourceQuoteId) {
                console.error('ERROR: Source quote ID is missing for clone_other');
                e.preventDefault();
                alert('Error: Please select a source quote to clone from.');
                return false;
            }
        }
        
        // Disable the submit button to prevent double submission
        $('#createRevisionBtn').prop('disabled', true).text('Creating...');
        
        console.log('Form validation passed - proceeding with submission');
        console.log('=== FORM SUBMISSION DEBUG END ===');
    });
    $('input[name="creation_method"]').on('change', function() {
        $('#cloneSourceWrapper').slideToggle(this.value === 'clone_other');
    });
    $('#addOptionModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const quoteId = button.data('quote-id');
        $('#addOptionForm').attr('action', `/deals/quote_option/add/${quoteId}`);
    });
    $('#deleteRevisionModal').on('show.bs.modal', function(e) {
        const recipientId = e.relatedTarget.dataset.recipientId;
        const select = $('#revision-to-delete-select');
        select.empty();
        $(`.nav-tabs a[data-recipient-id="${recipientId}"]`).each(function() {
            select.append(new Option($(this).text().trim(), $(this).data('quote-id')));
        });
        select.trigger('change');
    });
    $('#revision-to-delete-select').on('change', function() {
        $('#deleteRevisionForm').attr('action', `/deals/revision/delete/${this.value}`);
    });
    $('#deleteOptionModal').on('show.bs.modal', function(e) {
        const quoteId = e.relatedTarget.dataset.quoteId;
        const select = $('#option-to-delete-select');
        select.empty();
        $(`#option-accordion-${quoteId} .option-card`).each(function() {
            const optionId = $(this).find('.editable[data-model="quote_option"]').data('id');
            const optionName = $(this).find('.editable[data-model="quote_option"]').text().trim();
            select.append(new Option(optionName, optionId));
        });
        select.trigger('change');
    });
    $('#option-to-delete-select').on('change', function() {
        $('#deleteOptionForm').attr('action', `/deals/quote_option/delete/${this.value}`);
    });
    $('.delete-item-form, #deleteRevisionForm, #deleteOptionForm').on('submit', function(e) {
        if (!confirm('Are you sure you want to permanently delete this?')) {
            e.preventDefault();
        }
    });
    $('#expand-all-btn').on('click', () => $('#quote-streams-accordion .collapse').collapse('show'));
    $('#collapse-all-btn').on('click', () => $('#quote-streams-accordion .collapse').collapse('hide'));
    $('.quote-stream-panel').each(function() {
        $(this).find('.nav-tabs .nav-link').first().tab('show');
    });

    // --- MANAGE PARTIES MODAL FUNCTIONALITY ---
    $('#managePartiesModal').on('show.bs.modal', function() {
        // Initialize company select with search functionality
        $('#addCompanySelect').select2({
            placeholder: 'Search for a company...',
            allowClear: true,
            ajax: {
                url: '/deals/search/modal',
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        q: params.term,
                        type: 'company',
                        deal_id: dealId
                    };
                },
                processResults: function(data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.text
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2
        });

        // Initialize contact select with search functionality
        $('#addContactSelect').select2({
            placeholder: 'Search for a contact...',
            allowClear: true,
            ajax: {
                url: '/deals/search/modal',
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        q: params.term,
                        type: 'contact',
                        deal_id: dealId
                    };
                },
                processResults: function(data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.text
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2
        });
    });

    // Clear dropdowns when modal is hidden
    $('#managePartiesModal').on('hidden.bs.modal', function() {
        $('#addCompanySelect').val(null).trigger('change');
        $('#addContactSelect').val(null).trigger('change');
    });

    // --- LEAD-TIME FUNCTIONALITY ---
    // Handle Ex-Stock Brisbane checkbox
    $('.lead-time-ex-stock').on('change', function() {
        const optionId = $(this).data('option-id');
        const isChecked = $(this).is(':checked');
        const customDiv = $(this).closest('.d-flex').find('.lead-time-custom');
        
        if (isChecked) {
            customDiv.addClass('d-none');
            // Save the ex-stock setting
            updateLeadTime(optionId, null, null, true);
        } else {
            customDiv.removeClass('d-none');
            // Save the custom lead-time
            const value = customDiv.find('.lead-time-value').val();
            const unit = customDiv.find('.lead-time-unit').val();
            updateLeadTime(optionId, value, unit, false);
        }
    });

    // Handle lead-time value changes
    $('.lead-time-value').on('change', function() {
        const optionId = $(this).data('option-id');
        const value = $(this).val();
        const unit = $(this).closest('.lead-time-custom').find('.lead-time-unit').val();
        const isExStock = $(this).closest('.d-flex').find('.lead-time-ex-stock').is(':checked');
        
        if (!isExStock) {
            updateLeadTime(optionId, value, unit, false);
        }
    });

    // Handle lead-time unit changes
    $('.lead-time-unit').on('change', function() {
        const optionId = $(this).data('option-id');
        const unit = $(this).val();
        const value = $(this).closest('.lead-time-custom').find('.lead-time-value').val();
        const isExStock = $(this).closest('.d-flex').find('.lead-time-ex-stock').is(':checked');
        
        if (!isExStock) {
            updateLeadTime(optionId, value, unit, false);
        }
    });

    function updateLeadTime(optionId, value, unit, isExStock) {
        fetch(`/deals/api/quote-option/${optionId}/update_lead_time`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                lead_time_value: value,
                lead_time_unit: unit,
                is_ex_stock_brisbane: isExStock
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Lead-time updated successfully');
            } else {
                console.error('Failed to update lead-time:', data.error);
                alert('Failed to update lead-time. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error updating lead-time:', error);
            alert('Error updating lead-time. Please try again.');
        });
    }
});