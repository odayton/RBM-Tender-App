document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

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

    $('#addRevisionModal').on('show.bs.modal', function(e) {
        const button = e.relatedTarget;
        $(this).find('#modalRecipientName').text(button.dataset.recipientName);
        $(this).find('#modalRecipientId').val(button.dataset.recipientId);
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
});