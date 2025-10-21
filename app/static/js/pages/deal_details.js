document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;
    const dealId = document.querySelector('[data-deal-id]')?.dataset.dealId;

    // Utility function to format currency with thousand separators
    function formatCurrency(value) {
        return parseFloat(value).toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // Function to handle revision tab switching (Tailwind version)
    function showRevisionTab(clickedTab) {
        const targetPaneId = clickedTab.data('target');
        const recipientId = clickedTab.data('recipient-id');
        
        // Hide all tab panes for this recipient
        $(`#stream-content-${recipientId} .tab-pane`).removeClass('show active');
        
        // Show the target pane
        $(targetPaneId).addClass('show active');
        
        // Update tab styles - remove active from all tabs in this recipient's panel
        $(`#stream-content-${recipientId} .revision-tab`).removeClass('text-white bg-gradient-to-b from-blue-600 to-blue-700')
                                                      .addClass('text-gray-400 hover:text-white hover:bg-blue-600/20');
        
        // Add active styles to clicked tab
        clickedTab.removeClass('text-gray-400 hover:text-white hover:bg-blue-600/20')
                  .addClass('text-white bg-gradient-to-b from-blue-600 to-blue-700');
        
        // Update aria-selected attributes
        $(`#stream-content-${recipientId} .revision-tab`).attr('aria-selected', 'false');
        clickedTab.attr('aria-selected', 'true');
    }

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
            searchResultsContainer.innerHTML = `
                <div class="p-6 text-center">
                    <i class="fas fa-search text-2xl text-gray-500 mb-2"></i>
                    <p class="text-gray-400 text-sm">No products found</p>
                </div>
            `;
        } else {
            // Clear any existing classes and set proper scrolling
            searchResultsContainer.className = 'absolute z-50 left-0 right-0 mt-1 border border-gray-700 rounded-lg bg-gray-800 shadow-2xl';
            searchResultsContainer.style.maxHeight = '400px';
            searchResultsContainer.style.overflowY = 'auto';
            searchResultsContainer.style.overflowX = 'auto';
            
            // Create table
            const table = document.createElement('table');
            table.className = 'w-full text-sm';
            table.style.minWidth = '800px'; // Ensure table is wide enough for all columns
            
            // Table header
            const thead = document.createElement('thead');
            thead.className = 'bg-gray-900/50 sticky top-0 z-10';
            thead.innerHTML = `
                <tr class="border-b border-gray-700">
                    <th class="px-3 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Series</th>
                    <th class="px-3 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Item No</th>
                    <th class="px-3 py-2 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Description</th>
                    <th class="px-3 py-2 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">List Price</th>
                    <th class="px-3 py-2 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">Disc Code</th>
                    <th class="px-3 py-2 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">Unit Price</th>
                </tr>
            `;
            table.appendChild(thead);
            
            // Table body
            const tbody = document.createElement('tbody');
            tbody.className = 'divide-y divide-gray-700/30';
            
            products.forEach((product, index) => {
                const row = document.createElement('tr');
                // Add zebra striping with alternating background colors
                const zebraClass = index % 2 === 0 ? 'bg-gray-700/20' : 'bg-gray-700/40';
                row.className = `search-result-item ${zebraClass} hover:bg-gray-600/60 transition-colors cursor-pointer`;
                
                row.innerHTML = `
                    <td class="px-3 py-2 text-gray-300 text-xs whitespace-nowrap">${product.series || '-'}</td>
                    <td class="px-3 py-2 text-white font-medium text-xs whitespace-nowrap">${product.sku}</td>
                    <td class="px-3 py-2 text-gray-300 text-xs max-w-xs truncate">${product.name}</td>
                    <td class="px-3 py-2 text-right text-gray-300 text-xs whitespace-nowrap">$${formatCurrency(product.list_price)}</td>
                    <td class="px-3 py-2 text-center whitespace-nowrap">
                        ${product.disc_code ? `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-orange-500/20 text-orange-400">${product.disc_code}</span>` : '<span class="text-gray-600 text-xs">-</span>'}
                    </td>
                    <td class="px-3 py-2 text-right whitespace-nowrap">
                        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400">$${formatCurrency(product.unit_price)}</span>
                    </td>
                `;
                
                row.dataset.productId = product.id;
                row.dataset.sku = product.sku;
                row.dataset.name = product.name;
                row.dataset.series = product.series || '';
                row.dataset.listPrice = product.list_price;
                row.dataset.unitPrice = product.unit_price;
                row.dataset.discCode = product.disc_code || '';
                row.dataset.discount = product.discount || '0.0';

                row.addEventListener('click', function () {
                    populateAddItemForm(this.dataset);
                    searchResultsContainer.innerHTML = '';
                    if (searchInput) searchInput.value = '';
                });
                
                tbody.appendChild(row);
            });
            
            table.appendChild(tbody);
            searchResultsContainer.appendChild(table);
        }
    }

    function populateAddItemForm(dataset) {
        // Show selected product info section
        const selectedProductInfo = document.getElementById('selectedProductInfo');
        if (selectedProductInfo) {
            selectedProductInfo.style.display = 'block';
        }
        
        // Populate product display fields
        addItemForm.querySelector('#item_sku_display').value = dataset.sku;
        addItemForm.querySelector('#item_name_display').value = dataset.name;
        
        // Populate form fields
        addItemForm.querySelector('input[name="product_id"]').value = dataset.productId;
        
        // Populate list price and discount
        const listPriceInput = addItemForm.querySelector('#list_price');
        const discountInput = addItemForm.querySelector('input[name="discount"]');
        
        if (listPriceInput) {
            listPriceInput.value = dataset.listPrice || '0.00';
        }
        if (discountInput) {
            discountInput.value = dataset.discount || '0.0';
        }
        
        // Calculate and set unit price
        calculateUnitPrice();
        
        console.log('Populated form with:', {
            sku: dataset.sku,
            listPrice: dataset.listPrice,
            discount: dataset.discount
        });
    }
    
    function calculateUnitPrice() {
        const listPriceInput = addItemForm.querySelector('#list_price');
        const discountInput = addItemForm.querySelector('input[name="discount"]');
        const unitPriceInput = addItemForm.querySelector('input[name="unit_price"]');
        
        if (!listPriceInput || !discountInput || !unitPriceInput) return;
        
        const listPrice = parseFloat(listPriceInput.value) || 0;
        const discount = parseFloat(discountInput.value) || 0;
        
        // Calculate unit price: list price - (list price * discount / 100)
        const unitPrice = listPrice - (listPrice * discount / 100);
        unitPriceInput.value = formatCurrency(unitPrice);
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
        $('#selectedProductInfo').hide();
    });
    
    // Add event listeners for price calculation
    $(document).on('input change', '#addItemForm input[name="discount"]', function() {
        calculateUnitPrice();
    });

    // --- YOUR EXISTING INLINE EDITING, DRAG-DROP, AND OTHER MODAL LOGIC ---
    // (This part of your code is correct and should remain)
    function makeEditable(element) {
        if (element.querySelector('input')) return;
        const originalText = element.textContent.trim();
        const field = element.dataset.field;
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control form-control-sm';
        
        // For price fields, show numeric value without $ for editing
        if (field === 'unit_price' || field === 'list_price') {
            input.value = originalText.replace(/[$,]/g, '');
        } else {
            input.value = originalText;
        }
        
        element.innerHTML = '';
        element.appendChild(input);
        input.focus();
        function saveChanges() {
            let newValue = input.value;
            element.textContent = originalText;
            if (newValue === originalText) return;
            
            const model = element.dataset.model;
            const id = element.dataset.id;
            const field = element.dataset.field;
            
            // Format unit price fields with dollar sign
            if (field === 'unit_price' || field === 'list_price') {
                // Remove any existing dollar signs and format as currency
                const numericValue = parseFloat(newValue.replace(/[$,]/g, ''));
                if (!isNaN(numericValue)) {
                    newValue = '$' + formatCurrency(numericValue);
                } else {
                    // If not a valid number, keep original value
                    newValue = originalText;
                }
            }
            let apiUrl = '';
            if (model === 'line_item') {
                apiUrl = `/deals/api/line-item/${id}/update-field`;
            } else if (model === 'quote_option') {
                apiUrl = `/deals/api/quote-option/${id}/update-field`;
            }
            if (!apiUrl) return;
            
            // Send the numeric value (without $) to the server
            const serverValue = field === 'unit_price' || field === 'list_price' ? 
                newValue.replace('$', '') : newValue;
                
            fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ field: field, value: serverValue })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    element.textContent = newValue;
                    const row = element.closest('tr');
                    
                    if (field === 'custom_name' && data.newState) {
                        const skuCell = row.querySelector('[data-field="sku"]');
                        if (skuCell) skuCell.textContent = data.newState.sku;
                    }
                    
                    // Check if this is a pump assembly header unit price change (collapsed or expanded)
                    if (field === 'unit_price' && row.classList.contains('pump-assembly-header')) {
                        const assemblyId = element.dataset.id;
                        const newTotalPrice = parseFloat(newValue.replace(/[$,]/g, ''));
                        
                        if (!isNaN(newTotalPrice) && newTotalPrice > 0) {
                            distributeAssemblyPrice(assemblyId, newTotalPrice);
                        }
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

    // Function to distribute assembly price among components
    function distributeAssemblyPrice(assemblyId, newTotalPrice) {
        fetch(`/deals/api/pump-assembly/${assemblyId}/distribute-price`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                total_price: newTotalPrice
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the component prices in the UI
                data.updated_components.forEach(component => {
                    const componentRow = document.querySelector(`tr[data-item-id="${component.id}"]`);
                    if (componentRow) {
                        const unitPriceCell = componentRow.querySelector('[data-field="unit_price"]');
                        const lineTotalCell = componentRow.querySelector('.line-total');
                        
                        if (unitPriceCell) {
                            unitPriceCell.textContent = '$' + formatCurrency(component.new_unit_price);
                        }
                        if (lineTotalCell) {
                            lineTotalCell.textContent = '$' + formatCurrency(component.total_price);
                        }
                    }
                });
                
                // Recalculate totals for the option
                const optionCard = document.querySelector(`tr[data-item-id="${assemblyId}"]`).closest('.option-card');
                if (optionCard) {
                    calculateTotalsForOption(optionCard);
                }
                
                console.log('Assembly price distributed successfully:', data.updated_components);
            } else {
                console.error('Failed to distribute assembly price:', data.message);
                alert('Failed to distribute assembly price: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error distributing assembly price:', error);
            alert('Error distributing assembly price. Please try again.');
        });
    }

    function calculateTotalsForOption(optionCard) {
        let subtotal = 0;
        optionCard.querySelectorAll('.line-items-table tbody tr').forEach(row => {
            // Handle pump assembly headers
            if (row.classList.contains('pump-assembly-header')) {
                const assemblyId = row.dataset.assemblyId;
                const subItems = optionCard.querySelectorAll(`tr.pump-assembly-item[data-assembly-id="${assemblyId}"]`);
                
                // If assembly is expanded (sub-items are visible), use component total
                if (subItems.length > 0 && subItems[0].style.display !== 'none') {
                    // Calculate total from visible sub-items
                    let componentTotal = 0;
                    subItems.forEach(subRow => {
                        const qty = parseFloat(subRow.querySelector('[data-field="quantity"]').textContent) || 0;
                        const unitPrice = parseFloat(subRow.querySelector('[data-field="unit_price"]').textContent.replace(/[$,]/g, '')) || 0;
                        componentTotal += qty * unitPrice;
                        
                        // Calculate line total for sub-item display
                        const lineTotal = qty * unitPrice;
                        subRow.querySelector('.line-total').textContent = lineTotal.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' });
                    });
                    
                    // Set assembly header total to component sum
                    row.querySelector('.assembly-unit-price').textContent = '$' + formatCurrency(componentTotal);
                    row.querySelector('.line-total').textContent = componentTotal.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' });
                    subtotal += componentTotal;
                    return; // Skip normal processing
                } else {
                    // Assembly is collapsed, use stored total price
                    const qty = parseFloat(row.querySelector('[data-field="quantity"]').textContent) || 0;
                    const unitPrice = parseFloat(row.querySelector('[data-field="unit_price"]').textContent.replace(/[$,]/g, '')) || 0;
                    const lineTotal = qty * unitPrice;
                    row.querySelector('.line-total').textContent = lineTotal.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' });
                    subtotal += lineTotal;
                    return;
                }
            }
            
            // Skip pump assembly sub-items entirely (never include in subtotal to avoid double counting)
            if (row.classList.contains('pump-assembly-item')) {
                // Calculate line total for display but don't add to subtotal (already counted in header)
                const qty = parseFloat(row.querySelector('[data-field="quantity"]').textContent) || 0;
                const unitPrice = parseFloat(row.querySelector('[data-field="unit_price"]').textContent.replace(/[$,]/g, '')) || 0;
                const lineTotal = qty * unitPrice;
                row.querySelector('.line-total').textContent = lineTotal.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' });
                return; // Skip adding to subtotal
            }
            
            // Regular items
            const qty = parseFloat(row.querySelector('[data-field="quantity"]').textContent) || 0;
            const unitPrice = parseFloat(row.querySelector('[data-field="unit_price"]').textContent.replace(/[$,]/g, '')) || 0;
            const lineTotal = qty * unitPrice;
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
        
        // Reset the form state - ensure dropdown is hidden and default option is selected
        $('#cloneSourceWrapper').hide();
        $('#methodCopyLast').prop('checked', true);
        $('input[name="creation_method"]').not('#methodCopyLast').prop('checked', false);
        $('#source_quote_id').val('');
        
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
        console.log('Creation method changed to:', this.value);
        if (this.value === 'clone_other') {
            $('#cloneSourceWrapper').slideDown();
            console.log('Showing clone source dropdown');
        } else {
            $('#cloneSourceWrapper').slideUp();
            $('#source_quote_id').val(''); // Clear selection when hiding
            console.log('Hiding clone source dropdown');
        }
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
    // Custom quote stream toggle functionality
    function toggleStream(streamId, show = null) {
        const content = document.getElementById(`stream-content-${streamId}`);
        const chevron = document.querySelector(`[data-stream-id="${streamId}"] .stream-chevron`);
        const isVisible = content.style.display !== 'none';
        
        const shouldShow = show !== null ? show : !isVisible;
        
        if (shouldShow) {
            content.style.display = 'block';
            chevron.style.transform = 'rotate(90deg)';
        } else {
            content.style.display = 'none';
            chevron.style.transform = 'rotate(0deg)';
        }
    }
    
    // Handle individual stream toggles
    $(document).on('click', '.stream-toggle-btn', function() {
        const streamId = $(this).data('stream-id');
        toggleStream(streamId);
    });
    
    // Handle expand/collapse all buttons
    $('#expand-all-btn').on('click', () => {
        $('.stream-content').show();
        $('.stream-chevron').css('transform', 'rotate(90deg)');
    });
    
    $('#collapse-all-btn').on('click', () => {
        $('.stream-content').hide();
        $('.stream-chevron').css('transform', 'rotate(0deg)');
    });
    
    // Custom option toggle functionality
    function toggleOption(optionId, show = null) {
        const content = document.getElementById(`option-content-${optionId}`);
        const isVisible = content.style.display !== 'none';
        
        const shouldShow = show !== null ? show : !isVisible;
        
        if (shouldShow) {
            content.style.display = 'block';
        } else {
            content.style.display = 'none';
        }
    }
    
    // Handle individual option toggles
    $(document).on('click', '.option-toggle-btn', function() {
        const optionId = $(this).data('option-id');
        toggleOption(optionId);
    });
    
    // Initialize revision tabs (Tailwind version)
    $('.quote-stream-panel').each(function() {
        const firstTab = $(this).find('.revision-tab').first();
        if (firstTab.length) {
            showRevisionTab(firstTab);
        }
    });

    // Handle revision tab clicks
    $(document).on('click', '.revision-tab', function(e) {
        e.preventDefault();
        showRevisionTab($(this));
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

    // --- PUMP ASSEMBLY COLLAPSE/EXPAND FUNCTIONALITY ---
    $(document).on('click', '.assembly-toggle', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const $toggle = $(this);
        const $headerRow = $toggle.closest('tr.pump-assembly-header');
        const assemblyId = $headerRow.data('assembly-id');
        
        console.log('Toggle clicked for assembly:', assemblyId);
        
        // Find all sub-items for this assembly
        const $subItems = $(`.pump-assembly-item[data-assembly-id="${assemblyId}"]`);
        
        console.log('Found sub-items:', $subItems.length);
        
        // Toggle visibility
        if ($subItems.is(':visible')) {
            // Collapse
            console.log('Collapsing');
            $subItems.slideUp(200);
            $toggle.removeClass('fa-chevron-down').addClass('fa-chevron-right');
            
            // Keep the current calculated total when collapsed (it's already correct from expansion or editing)
            // No need to change unit price - it already shows the sum of components
            
            // Restore list price when collapsed (but leave empty for pump assemblies)
            const $listPriceCell = $headerRow.find('[data-field="list_price"]');
            const originalListPrice = $listPriceCell.data('original-list-price');
            if (originalListPrice !== undefined) {
                $listPriceCell.text(originalListPrice);
            }
            
            // Restore discount when collapsed
            const $discountCell = $headerRow.find('[data-field="discount"]');
            const originalDiscount = $discountCell.data('original-discount');
            if (originalDiscount !== undefined) {
                $discountCell.text(originalDiscount);
            }
            
            // Restore price columns when collapsed (already visible, just restore content)
            // No need to show() since we're not hiding them anymore
        } else {
            // Expand
            console.log('Expanding');
            $subItems.slideDown(200);
            $toggle.removeClass('fa-chevron-right').addClass('fa-chevron-down');
            
            // Calculate total from sub-items when expanded
            const $unitPriceCell = $headerRow.find('.assembly-unit-price');
            let componentTotal = 0;
            $subItems.each(function() {
                const qty = parseFloat($(this).find('[data-field="quantity"]').text()) || 0;
                const unitPrice = parseFloat($(this).find('[data-field="unit_price"]').text().replace(/[$,]/g, '')) || 0;
                componentTotal += qty * unitPrice;
            });
            $unitPriceCell.text('$' + formatCurrency(componentTotal));
            
            // Store original list price and set to 0.00 when expanded
            const $listPriceCell = $headerRow.find('[data-field="list_price"]');
            const currentListPrice = $listPriceCell.text();
            if (!$listPriceCell.data('original-list-price')) {
                $listPriceCell.data('original-list-price', currentListPrice);
            }
            $listPriceCell.text('$0.00');
            
            // Store original discount and set to 0.0% when expanded
            const $discountCell = $headerRow.find('[data-field="discount"]');
            const currentDiscount = $discountCell.text();
            if (!$discountCell.data('original-discount')) {
                $discountCell.data('original-discount', currentDiscount);
            }
            $discountCell.text('0.0%');
            
            // Clear price columns when expanded (keep columns but make content blank)
            $headerRow.find('[data-field="list_price"]').text('');
            $headerRow.find('[data-field="discount"]').text('');
            // Don't clear unit price - let it show the calculated total from components
        }
        
        // Recalculate totals after animation completes
        setTimeout(() => {
            const $optionCard = $headerRow.closest('.option-card');
            calculateTotalsForOption($optionCard[0]);
            
            // If expanded, also recalculate the assembly header total from components
            if ($subItems.is(':visible')) {
                let componentTotal = 0;
                $subItems.each(function() {
                    const qty = parseFloat($(this).find('[data-field="quantity"]').text()) || 0;
                    const unitPrice = parseFloat($(this).find('[data-field="unit_price"]').text().replace(/[$,]/g, '')) || 0;
                    componentTotal += qty * unitPrice;
                });
                $headerRow.find('.assembly-unit-price').text('$' + formatCurrency(componentTotal));
            }
        }, 250); // Wait for slide animation to complete
    });
    
    // Make pump assembly header row clickable for expand/collapse (except on editable fields and delete button)
    $(document).on('click', 'tr.pump-assembly-header', function(e) {
        // Don't trigger if clicking on editable field, delete button, drag handle, or toggle icon itself
        if ($(e.target).hasClass('editable') || 
            $(e.target).closest('.editable').length > 0 ||
            $(e.target).closest('form').length > 0 ||
            $(e.target).hasClass('assembly-toggle') ||
            $(e.target).closest('.assembly-toggle').length > 0 ||
            $(e.target).hasClass('drag-handle') ||
            $(e.target).closest('.drag-handle').length > 0 ||
            $(e.target).hasClass('fa-grip-vertical')) {
            return;
        }
        
        // Click the toggle icon
        $(this).find('.assembly-toggle').trigger('click');
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