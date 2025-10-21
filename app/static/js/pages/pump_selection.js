// app/static/js/pages/pump_selection.js

document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    
    // Current state
    let currentPump = null;
    let currentOptionId = null;
    let pumpSeries = [];
    
    // Load pump series on page load
    loadPumpSeries();
    
    // Handle view pump button clicks
    $(document).on('click', '.view-pump-btn', function(e) {
        e.preventDefault();
        const assemblyId = $(this).data('assembly-id');
        
        // Find the pump sub-item (the one with "  • Pump:" in the name)
        // Look at the next sibling rows until we find the pump item
        const assemblyRow = $(this).closest('tr');
        let pumpLineItemId = null;
        
        // Get all rows after this assembly header
        let nextRow = assemblyRow.next();
        while (nextRow.length && nextRow.hasClass('pump-assembly-item')) {
            const itemId = nextRow.data('item-id');
            // Check if this row contains the pump detail
            const nameCell = nextRow.find('[data-field="custom_name"]');
            if (nameCell.length && nameCell.text().includes('• Pump:')) {
                pumpLineItemId = itemId;
                break;
            }
            nextRow = nextRow.next();
        }
        
        if (!pumpLineItemId) {
            alert('Could not find pump details for this assembly.');
            return;
        }
        
        // Fetch the pump configuration for this line item
        fetch(`/deals/api/pump-assembly/${pumpLineItemId}/view`)
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Error loading pump configuration:', data);
                    alert(data.error || 'Error loading pump configuration');
                    if (data.details) {
                        console.error('Error details:', data.details);
                    }
                    return;
                }
                
                // Update modal title to show "Update Pump Assembly"
                $('#pumpConfigModalLabel').text('Update Pump Assembly');
                
                // Store update mode info
                $('#pumpConfigModal').data('update-mode', true);
                $('#pumpConfigModal').data('line-item-id', data.line_item_id);
                
                // Populate pump details
                currentPump = data.pump;
                currentOptionId = data.option_id;
                
                $('#selectedPumpId').val(data.pump_id);
                $('#selectedOptionId').val(data.option_id);
                
                // Extract plant reference from assembly header
                // Look for the assembly header row (previous sibling without bullet)
                const pumpRow = assemblyRow.next();
                if (pumpRow.length) {
                    // Assembly header custom_name format: "Item No + Pump Name: Plant Ref"
                    const headerName = assemblyRow.find('[data-field="custom_name"]').text().trim();
                    if (headerName && headerName.includes(':')) {
                        const parts = headerName.split(':');
                        const plantRef = parts[parts.length - 1].trim();
                        $('#plantReference').val(plantRef);
                        $('#previewPlantRef').text(plantRef);
                    }
                }
                
                // Populate form fields with saved configuration
                if (data.config) {
                    console.log('Populating form with saved config:', data.config);
                    
                    // Margin
                    if (data.config.margin_percentage) {
                        $('#marginPercentage').val(data.config.margin_percentage);
                    }
                    
                    // Mounting type
                    if (data.config.mounting_type) {
                        $('#mountingType').val(data.config.mounting_type);
                    }
                    
                    // Crossbar quantity
                    if (data.config.crossbar_quantity) {
                        $('#crossbarQuantity').val(data.config.crossbar_quantity);
                    }
                    
                    // Spring type
                    if (data.config.spring_type) {
                        $('#springType').val(data.config.spring_type);
                    }
                    
                    // Spring quantity
                    if (data.config.spring_quantity) {
                        $('#springQuantity').val(data.config.spring_quantity);
                    }
                    
                    // Rubber mounts
                    if (data.config.include_rubber_mounts !== undefined) {
                        $('#includeRubberMounts').prop('checked', data.config.include_rubber_mounts);
                    }
                    
                    // Rubber mount quantity
                    if (data.config.rubber_mount_quantity) {
                        $('#rubberMountQuantity').val(data.config.rubber_mount_quantity);
                    }
                    
                    // Motor protection
                    if (data.config.include_motor_protection !== undefined) {
                        $('#includeMotorProtection').prop('checked', data.config.include_motor_protection);
                    }
                    
                    // Drip tray
                    if (data.config.include_drip_tray !== undefined) {
                        $('#includeDripTray').prop('checked', data.config.include_drip_tray);
                    }
                    
                    // Assembly description
                    if (data.config.assembly_description) {
                        $('#assemblyDescription').val(data.config.assembly_description);
                        $('#previewDescription').text(data.config.assembly_description);
                    }
                }
                
                // Update pump info display
                $('#configPumpName').text(data.pump.name);
                $('#configPumpPartNumber').text(data.pump.part_number);
                $('#configPumpSpecs').text(`${data.pump.kw || '-'} kW | ${data.pump.poles || '-'} Poles`);
                
                const sellPrice = data.pump.sell_price || 0;
                const costPrice = data.pump.cost_price || 0;
                $('#configPumpPrice').text(`$${sellPrice.toFixed(2)}`);
                $('#configPumpCostPrice').text(`$${costPrice.toFixed(2)}`);
                
                // Show pump curve link if available
                if (data.pump.curve_link) {
                    $('#configPumpCurveLink').attr('href', data.pump.curve_link).show();
                } else {
                    $('#configPumpCurveLink').hide();
                }
                
                // Update button text to "Update Pump"
                $('#addPumpToQuote').html('<i class="fas fa-check mr-2"></i>Update Pump');
                
                // Store the pump data for later use
                if (data.components) {
                    // Components data is available but we'll load it when needed
                    console.log('Pump components loaded:', data.components);
                }
                
                // Show the modal
                $('#pumpConfigModal').modal('show');
            })
            .catch(error => {
                console.error('Error loading pump configuration:', error);
                alert('Error loading pump configuration. Please try again.');
            });
    });
    
    // Step 1: Search method selection
    $('#addPumpModal').on('show.bs.modal', function(e) {
        const button = e.relatedTarget;
        currentOptionId = $(button).data('option-id');
        $('#selectedOptionId').val(currentOptionId);
        
        // Reset to method selection
        showMethodSelection();
    });
    
    // Make entire search method card clickable and auto-proceed
    $(document).on('click', '.search-method-card', function() {
        const radio = $(this).find('input[type="radio"]');
        const method = radio.val();
        
        radio.prop('checked', true);
        $('.search-method-card').removeClass('selected');
        $(this).addClass('selected');
        
        // Auto-proceed to the selected method
        $('#searchMethodSelection').hide();
        
        if (method === 'duty-point') {
            $('#dutyPointSearch').show();
        } else if (method === 'manual') {
            $('#manualSearch').show();
        } else if (method === 'browse') {
            $('#browseAllPumps').show();
            loadBrowseResults();
        }
    });
    
    function showMethodSelection() {
        $('#searchMethodSelection').show();
        $('#dutyPointSearch').hide();
        $('#manualSearch').hide();
        $('#browseAllPumps').hide();
        $('#pumpResults').hide();
        $('#noHistoricalData').hide();
        
        // Highlight the selected card
        $('.search-method-card').removeClass('selected');
        const selectedRadio = $('input[name="search_method"]:checked');
        selectedRadio.closest('.search-method-card').addClass('selected');
    }
    
    // Proceed with selected method
    $('#proceedWithMethod').on('click', function() {
        const method = $('input[name="search_method"]:checked').val();
        
        $('#searchMethodSelection').hide();
        
        if (method === 'duty-point') {
            $('#dutyPointSearch').show();
        } else if (method === 'manual') {
            $('#manualSearch').show();
        } else if (method === 'browse') {
            $('#browseAllPumps').show();
            loadBrowseResults();
        }
    });
    
    // Back buttons
    $('#backToMethodSelection, #backToMethodSelection2, #backToMethodSelection3').on('click', showMethodSelection);
    
    // Duty Point Search
    $('#searchByDutyPoint').on('click', function() {
        const flowRate = parseFloat($('#flowRate').val());
        const headPressure = parseFloat($('#headPressure').val());
        const tolerance = parseFloat($('#tolerance').val());
        const seriesId = $('#dutyPointSeriesFilter').val() || null;
        const poles = $('#dutyPointPolesFilter').val() || null;
        
        if (!flowRate || !headPressure) {
            alert('Please enter both flow rate and head pressure');
            return;
        }
        
        searchByDutyPoint(flowRate, headPressure, tolerance, seriesId, poles);
    });
    
    function searchByDutyPoint(flowRate, headPressure, tolerance, seriesId, poles) {
        $.ajax({
            url: '/deals/api/pumps/search/duty-point',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                flow_rate: flowRate,
                head_pressure: headPressure,
                tolerance: tolerance,
                series_id: seriesId,
                poles: poles
            }),
            success: function(response) {
                if (response.has_historical_data) {
                    displayPumpResults(response.pumps, 'historical');
                } else {
                    showNoHistoricalData(flowRate, headPressure, tolerance);
                }
            },
            error: function(xhr) {
                alert('Error searching for pumps: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    }
    
    function showNoHistoricalData(flowRate, headPressure, tolerance) {
        $('#dutyPointSearch').hide();
        $('#noHistoricalData').show();
    }
    
    $('#browseManuallyFromNoData').on('click', function() {
        $('#noHistoricalData').hide();
        $('#browseAllPumps').show();
        loadBrowseResults();
    });
    
    $('#adjustTolerance').on('click', function() {
        $('#noHistoricalData').hide();
        $('#dutyPointSearch').show();
    });
    
    $('#backToDutyPoint').on('click', function() {
        $('#noHistoricalData').hide();
        $('#dutyPointSearch').show();
    });
    
    // Manual Search
    let manualSearchTimeout;
    $('#manualSearchInput').on('input', function() {
        const query = $(this).val().trim();
        
        clearTimeout(manualSearchTimeout);
        
        if (query.length < 2) {
            $('#manualSearchResults').html('');
            return;
        }
        
        manualSearchTimeout = setTimeout(() => {
            const seriesId = $('#manualSeriesFilter').val() || null;
            searchManual(query, seriesId);
        }, 300);
    });
    
    function searchManual(query, seriesId) {
        $.ajax({
            url: '/deals/api/pumps/search/manual',
            method: 'GET',
            data: {
                q: query,
                series_id: seriesId,
                limit: 20
            },
            success: function(pumps) {
                displayManualSearchResults(pumps);
            },
            error: function(xhr) {
                alert('Error searching pumps: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    }
    
    function displayManualSearchResults(pumps) {
        const container = $('#manualSearchResults');
        container.html('');
        
        if (pumps.length === 0) {
            container.html('<p class="text-muted">No pumps found</p>');
            return;
        }
        
        pumps.forEach(pump => {
            const pumpCard = createPumpCard(pump, 'manual');
            container.append(pumpCard);
        });
    }
    
    // Browse All Pumps
    let currentBrowsePage = 1;
    
    $('#applyBrowseFilters').on('click', function() {
        currentBrowsePage = 1;
        loadBrowseResults();
    });
    
    function loadBrowseResults() {
        const seriesId = $('#browseSeriesFilter').val() || null;
        const poles = $('#browsePolesFilter').val() || null;
        const minKw = $('#browseKwFilter').val() || null;
        
        $.ajax({
            url: '/deals/api/pumps/browse',
            method: 'GET',
            data: {
                series_id: seriesId,
                poles: poles,
                min_kw: minKw,
                page: currentBrowsePage,
                per_page: 10
            },
            success: function(response) {
                displayBrowseResults(response);
            },
            error: function(xhr) {
                alert('Error loading pumps: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    }
    
    function displayBrowseResults(response) {
        const container = $('#browseResults');
        container.html('');
        
        if (response.pumps.length === 0) {
            container.html('<p class="text-muted">No pumps found matching filters</p>');
            return;
        }
        
        response.pumps.forEach(pump => {
            const pumpCard = createPumpCard(pump, 'browse');
            container.append(pumpCard);
        });
        
        // Pagination
        displayBrowsePagination(response);
    }
    
    function displayBrowsePagination(response) {
        const container = $('#browsePagination');
        container.html('');
        
        if (response.pages <= 1) return;
        
        const pagination = $('<nav><ul class="pagination"></ul></nav>');
        const ul = pagination.find('ul');
        
        // Previous button
        const prevDisabled = !response.has_prev ? 'disabled' : '';
        ul.append(`<li class="page-item ${prevDisabled}"><a class="page-link" href="#" data-page="${currentBrowsePage - 1}">Previous</a></li>`);
        
        // Page numbers
        for (let i = 1; i <= Math.min(response.pages, 5); i++) {
            const active = i === currentBrowsePage ? 'active' : '';
            ul.append(`<li class="page-item ${active}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`);
        }
        
        // Next button
        const nextDisabled = !response.has_next ? 'disabled' : '';
        ul.append(`<li class="page-item ${nextDisabled}"><a class="page-link" href="#" data-page="${currentBrowsePage + 1}">Next</a></li>`);
        
        container.append(pagination);
        
        // Handle pagination clicks
        container.find('.page-link').on('click', function(e) {
            e.preventDefault();
            if ($(this).parent().hasClass('disabled')) return;
            currentBrowsePage = parseInt($(this).data('page'));
            loadBrowseResults();
        });
    }
    
    function displayPumpResults(pumps, source) {
        $('#dutyPointSearch').hide();
        $('#pumpResults').show();
        
        const container = $('#resultsContainer');
        container.html('');
        
        if (source === 'historical') {
            container.append(`<h6 class="mb-3">Matching Pumps (${pumps.length} found)</h6>`);
        }
        
        pumps.forEach(pump => {
            const pumpCard = createPumpCard(pump, source);
            container.append(pumpCard);
        });
    }
    
    function createPumpCard(pump, source) {
        const card = $(`
            <div class="bg-gradient-to-r from-slate-800/50 to-slate-900/50 rounded-xl border border-slate-700 hover:border-blue-500/50 transition-all duration-300 mb-4 shadow-lg hover:shadow-blue-500/10 pump-result-card">
                <div class="p-6"></div>
            </div>
        `);
        const cardBody = card.find('div');
        
        // Confidence stars (only for historical data)
        let confidenceHTML = '';
        if (source === 'historical' && pump.confidence_stars) {
            const stars = '★'.repeat(pump.confidence_stars) + '☆'.repeat(5 - pump.confidence_stars);
            confidenceHTML = `
                <div class="mb-4">
                    <div class="flex items-center gap-3">
                        <span class="text-yellow-400 text-lg">${stars}</span>
                        <span class="px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-sm font-medium border border-green-500/30">
                            ${pump.confidence_score}% Confidence
                        </span>
                    </div>
                </div>
            `;
        }
        
        // Pump info
        const specs = [];
        if (pump.kw_rating) specs.push(`${pump.kw_rating} kW`);
        if (pump.poles) specs.push(`${pump.poles} Poles`);
        
        let historyHTML = '';
        if (source === 'historical') {
            historyHTML = `
                <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mb-4">
                    <div class="text-sm text-blue-300">
                        <div class="font-medium mb-1">Historical Performance</div>
                        <div class="text-blue-400">
                            Selected ${pump.selection_count} times | ${pump.success_rate.toFixed(0)}% success rate
                        </div>
                        <div class="text-blue-400 text-xs mt-1">
                            Flow match: ${pump.flow_match}% | Head match: ${pump.head_match}%
                        </div>
                    </div>
                </div>
            `;
        }
        
        const curveButton = pump.pump_curve_url 
            ? `<a href="${pump.pump_curve_url}" target="_blank" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-all duration-200 shadow-lg hover:shadow-blue-500/30">
                <i class="fas fa-chart-line"></i>
                View Curve
            </a>`
            : '';
        
        cardBody.html(`
            ${confidenceHTML}
            
            <!-- Pump Header -->
            <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                    <h6 class="text-xl font-bold text-white mb-2">${pump.name}</h6>
                    <div class="flex items-center gap-4 text-slate-400 text-sm">
                        <div class="flex items-center gap-1">
                            <i class="fas fa-tag text-blue-400"></i>
                            <span class="font-medium">Part #: <span class="text-slate-300">${pump.part_number || pump.item_number}</span></span>
                        </div>
                        <div class="flex items-center gap-1">
                            <i class="fas fa-cogs text-green-400"></i>
                            <span>${specs.join(' | ')}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Price Display -->
                <div class="text-right">
                    <div class="text-2xl font-bold text-green-400 mb-1">
                        $${pump.nett_price ? pump.nett_price.toLocaleString('en-AU', {minimumFractionDigits: 2}) : '0.00'}
                    </div>
                    <div class="text-xs text-slate-500 font-medium">NETT PRICE</div>
                </div>
            </div>
            
            ${historyHTML}
            
            <!-- Action Buttons -->
            <div class="flex items-center justify-between pt-4 border-t border-slate-700">
                <div class="flex items-center gap-3">
                    ${curveButton}
                </div>
                <button type="button" class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-green-500/30 select-pump-btn" data-pump-id="${pump.id}">
                    <i class="fas fa-check"></i>
                    Select This Pump
                </button>
            </div>
        `);
        
        return card;
    }
    
    // Handle pump selection
    $(document).on('click', '.select-pump-btn', function() {
        const pumpId = $(this).data('pump-id');
        selectPump(pumpId);
    });
    
    function selectPump(pumpId) {
        // Load pump details and show configuration modal
        $.ajax({
            url: `/deals/api/pumps/${pumpId}/components`,
            method: 'GET',
            success: function(data) {
                currentPump = data.pump;
                showConfigurationModal(data);
            },
            error: function(xhr) {
                alert('Error loading pump details: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    }
    
    function showConfigurationModal(data) {
        const pump = data.pump;
        
        // Populate pump details
        $('#selectedPumpId').val(pump.id);
        $('#configPumpName').text(pump.name);
        $('#configPumpPartNumber').text(pump.part_number);
        $('#configPumpSpecs').text(`${pump.kw_rating || '?'} kW | ${pump.poles || '?'} Poles`);
        
        // Store cost price for calculations and pump name for NBG detection
        currentPump.cost_price = pump.nett_price || 0;
        currentPump.name = pump.name;
        
        // Initialize plant reference with auto-generated default
        const nextAssemblyNumber = getNextAssemblyNumber();
        const defaultRef = `PUMP-ASSY-${String(nextAssemblyNumber).padStart(3, '0')}`;
        $('#plantReference').val(defaultRef);
        $('#defaultPlantRef').text(defaultRef);
        $('#assemblyQuantity').val(1);
        $('#assemblyDescription').val('');
        
        // Update preview immediately
        updateQuotePreview();
        
        // Store component data from BOM if available
        currentPump.inertia_base = data.inertia_base || null;
        currentPump.spring_standard = data.spring_standard || null;
        currentPump.spring_50mm = data.spring_50mm || null;
        
        // Check if this is an NBG or NK pump
        const pumpName = pump.name ? pump.name.toUpperCase() : '';
        const isNBG = pumpName.includes('NBG');
        const isNK = pumpName.includes('NK');
        const isNBGorNK = isNBG || isNK;
        
        // Hide "None (Pump Only)" option for NBG pumps
        if (isNBG) {
            $('#mountingNone').closest('.form-check').hide();
            // If "None" was selected, switch to Inertia Base
            if ($('#mountingNone').is(':checked')) {
                $('#mountingInertia').prop('checked', true);
            }
        } else {
            $('#mountingNone').closest('.form-check').show();
        }
        
        // Hide rubber mounts for NBG and NK pumps
        if (isNBGorNK) {
            $('#includeRubberMounts').closest('label').parent().hide(); // Hide checkbox
            $('#rubberMountQuantityGroup').hide(); // Hide quantity selector
            $('#includeRubberMounts').prop('checked', false); // Uncheck it
        } else {
            $('#includeRubberMounts').closest('label').parent().show();
            $('#includeRubberMounts').prop('checked', true); // Default checked for other pumps
        }
        
        // Set default margin and calculate price
        $('#marginPercentage').val(18.5);
        updatePumpPriceWithMargin();
        
        if (pump.pump_curve_url) {
            $('#configPumpCurveLink').attr('href', pump.pump_curve_url).show();
        } else {
            $('#configPumpCurveLink').hide();
        }
        
        // Reset to defaults
        resetConfigurationToDefaults();
        
        // Update component details
        updateInertiaBaseDetails();
        updateCrossbarQuantityVisibility();
        updateSpringDetails();
        
        // Calculate initial total
        calculateAssemblyTotal();
        
        // Hide main modal, show config modal
        $('#addPumpModal').modal('hide');
        $('#pumpConfigModal').modal('show');
    }
    
    function resetConfigurationToDefaults() {
        // Check if this is an NBG or NK pump
        const pumpName = currentPump && currentPump.name ? currentPump.name.toUpperCase() : '';
        const isNBG = pumpName.includes('NBG');
        const isNK = pumpName.includes('NK');
        const isNBGorNK = isNBG || isNK;
        
        $('#mountingInertia').prop('checked', true);
        $('#springStandard').prop('checked', true);
        $('#springQuantity').val('4');
        $('#crossbarQuantity').val('2');
        
        // Uncheck rubber mounts for NBG/NK pumps, check for others
        $('#includeRubberMounts').prop('checked', !isNBGorNK);
        $('#rubberMountQuantity').val('4');
        
        $('#includeMotorProtection').prop('checked', false);
        $('#includeDripTray').prop('checked', false);
        $('#ipRating').val('standard');
        $('#marginPercentage').val('18.5');
        
        updatePumpPriceWithMargin();
        updateSpringQuantityVisibility();
        updateCrossbarQuantityVisibility();
        updateRubberMountVisibility();
        updateInertiaBaseDetails();
        updateSpringDetails();
        calculateAssemblyTotal();
    }
    
    $('#resetToDefaults').on('click', resetConfigurationToDefaults);
    
    // Handle edit buttons
    $('#editInertiaBaseBtn, #editInertiaBase').on('click', function() {
        // Open inertia base selection modal or inline editor
        alert('Inertia Base Edit: This would open a component selection interface to choose different inertia base sizes/part numbers.');
        // TODO: Implement inertia base selection modal
    });
    
    $('#editSpringsBtn, #editSprings').on('click', function() {
        // Open spring selection modal or inline editor
        alert('Spring Edit: This would open a component selection interface to choose different spring types/part numbers.');
        // TODO: Implement spring selection modal
    });
    
    // Update visibility based on selections
    $('input[name="spring_type"]').on('change', function() {
        updateSpringQuantityVisibility();
        updateSpringDetails();
    });
    $('#includeRubberMounts').on('change', updateRubberMountVisibility);
    
    function updateSpringQuantityVisibility() {
        const springType = $('input[name="spring_type"]:checked').val();
        if (springType === 'none') {
            $('#springQuantityGroup').hide();
        } else {
            $('#springQuantityGroup').show();
        }
        calculateAssemblyTotal();
    }
    
    function updateCrossbarQuantityVisibility() {
        const mountingType = $('input[name="mounting_type"]:checked').val();
        if (mountingType === 'crossbar') {
            $('#crossbarQuantityGroup').show();
        } else {
            $('#crossbarQuantityGroup').hide();
        }
    }
    
    function updateRubberMountVisibility() {
        if ($('#includeRubberMounts').is(':checked')) {
            $('#rubberMountQuantityGroup').show();
        } else {
            $('#rubberMountQuantityGroup').hide();
        }
        calculateAssemblyTotal();
    }
    
    // Recalculate total when anything changes
    $('input[name="mounting_type"]').on('change', function() {
        updateInertiaBaseDetails();
        updateCrossbarQuantityVisibility();
        calculateAssemblyTotal();
    });
    $('input[name="spring_type"], #springQuantity, #crossbarQuantity, #rubberMountQuantity, #includeRubberMounts, #includeMotorProtection, #includeDripTray, #ipRating').on('change', calculateAssemblyTotal);
    
    // Update prices when margin changes
    $('#marginPercentage').on('input', function() {
        updatePumpPriceWithMargin();
        updateInertiaBaseDetails();
        updateSpringDetails();
        calculateAssemblyTotal();
    });
    
    // Update spring details when quantity changes
    $('#springQuantity').on('change', function() {
        updateSpringDetails();
    });
    
    function applyMargin(costPrice) {
        const margin = parseFloat($('#marginPercentage').val()) || 0;
        const priceWithMargin = costPrice * (1 + margin / 100);
        // Round up to nearest dollar
        return Math.ceil(priceWithMargin);
    }
    
    function updateInertiaBaseDetails() {
        const mountingType = $('input[name="mounting_type"]:checked').val();
        
        if (mountingType === 'inertia_base') {
            // Show the details panel and edit button
            $('#inertiaBaseDetails').show();
            $('#editInertiaBase').show();
            
            // Check if we have BOM data for the inertia base
            if (currentPump && currentPump.inertia_base) {
                const inertiaBase = currentPump.inertia_base;
                
                // Use real BOM data
                $('#inertiaPartNumber').text(inertiaBase.part_number || '-');
                $('#inertiaDimensions').text(inertiaBase.dimensions || '-');
                
                // Use actual nett_cost from BOM
                const cost = inertiaBase.nett_cost || 741.99;
                const sell = applyMargin(cost);
                
                $('#inertiaCostPrice').text('$' + cost.toFixed(2));
                $('#inertiaSellPrice').text('$' + sell.toFixed(0));
            } else {
                // No BOM data available - show defaults
                $('#inertiaPartNumber').text('Not configured in BOM');
                $('#inertiaDimensions').text('-');
                
                const cost = 741.99;
                const sell = applyMargin(cost);
                
                $('#inertiaCostPrice').text('$' + cost.toFixed(2));
                $('#inertiaSellPrice').text('$' + sell.toFixed(0));
            }
        } else {
            // Hide the details panel
            $('#inertiaBaseDetails').hide();
        }
    }
    
    function updateSpringDetails() {
        const springType = $('input[name="spring_type"]:checked').val();
        const springQty = parseInt($('#springQuantity').val()) || 0;
        
        if (springType !== 'none') {
            // Show the details panel and edit button
            $('#springDetails').show();
            $('#editSprings').show();
            
            // Get the appropriate spring data based on type
            let springData = null;
            if (springType === '50mm' && currentPump && currentPump.spring_50mm) {
                springData = currentPump.spring_50mm;
            } else if (springType === 'standard' && currentPump && currentPump.spring_standard) {
                springData = currentPump.spring_standard;
            }
            
            if (springData) {
                // Use real BOM data
                $('#springPartNumber').text(springData.part_number || '-');
                $('#springDescription').text(springData.description || '-');
                
                // Format max load
                if (springData.max_load_kg) {
                    $('#springMaxLoad').text(springData.max_load_kg + ' kg');
                } else {
                    $('#springMaxLoad').text('-');
                }
                
                // Use actual nett_price from BOM
                const cost = springData.nett_price || (springType === '50mm' ? 668.94 : 153.30);
                const sell = applyMargin(cost);
                
                $('#springCostPrice').text('$' + cost.toFixed(2));
                $('#springSellPrice').text('$' + (sell * springQty).toFixed(0));
                $('#springCurrentQty').text(springQty);
            } else {
                // No BOM data available - show defaults
                $('#springPartNumber').text('Not configured in BOM');
                $('#springDescription').text('-');
                $('#springMaxLoad').text('-');
                
                const cost = springType === '50mm' ? 668.94 : 153.30;
                const sell = applyMargin(cost);
                
                $('#springCostPrice').text('$' + cost.toFixed(2));
                $('#springSellPrice').text('$' + sell.toFixed(0));
            }
        } else {
            // Hide the details panel when "None" is selected
            $('#springDetails').hide();
        }
    }
    
    function updatePumpPriceWithMargin() {
        if (!currentPump || !currentPump.cost_price) return;
        
        const costPrice = currentPump.cost_price;
        const sellPrice = applyMargin(costPrice);
        
        $('#configPumpCostPrice').text('$' + costPrice.toLocaleString('en-AU', {minimumFractionDigits: 2}));
        $('#configPumpPrice').text('$' + sellPrice.toLocaleString('en-AU', {minimumFractionDigits: 0}));
        
        // Store sell price for calculations
        currentPump.nett_price = sellPrice;
    }
    
    function calculateAssemblyTotal() {
        if (!currentPump) return;
        
        let totalSell = currentPump.nett_price || 0;
        let totalCost = currentPump.cost_price || 0;
        
        // Check if this is an NBG or NK pump
        const pumpName = currentPump && currentPump.name ? currentPump.name.toUpperCase() : '';
        const isNBG = pumpName.includes('NBG');
        const isNK = pumpName.includes('NK');
        const isNBGorNK = isNBG || isNK;
        
        // Cost prices for components
        const COST_PRICES = {
            inertia_base: (currentPump && currentPump.inertia_base) ? currentPump.inertia_base.nett_cost : 741.99,
            base_only: isNBG ? 0 : 450.00,  // $0 for NBG pumps
            crossbar: 284.76,
            spring_standard: (currentPump && currentPump.spring_standard) ? currentPump.spring_standard.nett_price : 153.30,
            spring_50mm: (currentPump && currentPump.spring_50mm) ? currentPump.spring_50mm.nett_price : 668.94,
            rubber_mount: 11.83,
            motor_protection: 125.00,
            drip_tray: 85.00,
            ip56: 200.00,
            ip66: 400.00
        };
        
        // Mounting component
        const mountingType = $('input[name="mounting_type"]:checked').val();
        if (mountingType === 'inertia_base') {
            const cost = COST_PRICES.inertia_base;
            const price = applyMargin(cost);
            totalSell += price;
            totalCost += cost;
            $('#inertiaBasePrice').text('$' + price.toFixed(0));
        } else if (mountingType === 'base_only') {
            const cost = COST_PRICES.base_only;
            const price = applyMargin(cost);
            totalSell += price;
            totalCost += cost;
            $('#baseOnlyPrice').text('$' + price.toFixed(0));
        } else if (mountingType === 'crossbar') {
            const cost = COST_PRICES.crossbar;
            const price = applyMargin(cost);
            const crossbarQty = parseInt($('#crossbarQuantity').val()) || 2;
            totalSell += price * crossbarQty;
            totalCost += cost * crossbarQty;
            $('#crossbarUnitPrice').text('$' + price.toFixed(0));
            $('#crossbarTotalPrice').text('$' + (price * crossbarQty).toFixed(0));
            $('#crossbarPrice').text('$' + (price * crossbarQty).toFixed(0));
        }
        
        // Springs
        const springType = $('input[name="spring_type"]:checked').val();
        const springQty = parseInt($('#springQuantity').val()) || 0;
        if (springType === 'standard') {
            const cost = COST_PRICES.spring_standard;
            const price = applyMargin(cost);
            totalSell += price * springQty;
            totalCost += cost * springQty;
            $('#springUnitPrice').text('$' + price.toFixed(0));
            $('#springTotalPrice').text('$' + (price * springQty).toFixed(0));
        } else if (springType === '50mm') {
            const cost = COST_PRICES.spring_50mm;
            const price = applyMargin(cost);
            totalSell += price * springQty;
            totalCost += cost * springQty;
            $('#springUnitPrice').text('$' + price.toFixed(0));
            $('#springTotalPrice').text('$' + (price * springQty).toFixed(0));
        }
        
        // Rubber mounts
        if ($('#includeRubberMounts').is(':checked')) {
            const mountQty = parseInt($('#rubberMountQuantity').val()) || 0;
            const cost = COST_PRICES.rubber_mount;
            const price = applyMargin(cost);
            totalSell += price * mountQty;
            totalCost += cost * mountQty;
            $('#mountUnitPrice').text('$' + price.toFixed(0));
            $('#mountTotalPrice').text('$' + (price * mountQty).toFixed(0));
        }
        
        // Motor protection
        if ($('#includeMotorProtection').is(':checked')) {
            const cost = COST_PRICES.motor_protection;
            const price = applyMargin(cost);
            totalSell += price;
            totalCost += cost;
            $('#motorProtectionPrice').text('$' + price.toFixed(0));
        }
        
        // Drip tray
        if ($('#includeDripTray').is(':checked')) {
            const cost = COST_PRICES.drip_tray;
            const price = applyMargin(cost);
            totalSell += price;
            totalCost += cost;
            $('#dripTrayPrice').text('$' + price.toFixed(0));
        }
        
        // IP rating (placeholder - will be dynamic based on pump)
        const ipRating = $('#ipRating').val();
        if (ipRating === 'ip56') {
            const cost = COST_PRICES.ip56;
            const price = applyMargin(cost);
            totalSell += price;
            totalCost += cost;
        } else if (ipRating === 'ip66') {
            const cost = COST_PRICES.ip66;
            const price = applyMargin(cost);
            totalSell += price;
            totalCost += cost;
        }
        
        // Display totals
        $('#totalAssemblySell').text('$' + Math.round(totalSell).toLocaleString('en-AU', {minimumFractionDigits: 0}));
        $('#totalAssemblyCost').text('$' + totalCost.toLocaleString('en-AU', {minimumFractionDigits: 2}));
    }
    
    // Add pump to quote
    $('#addPumpToQuote').on('click', function() {
        const pumpId = $('#selectedPumpId').val();
        const optionId = $('#selectedOptionId').val();
        
        // Check if we're in update mode
        const isUpdateMode = $('#pumpConfigModal').data('update-mode');
        const lineItemId = $('#pumpConfigModal').data('line-item-id');
        
        if (!pumpId || !optionId) {
            alert('Missing pump or option ID');
            return;
        }
        
        // For update mode, plant reference validation is optional since it already exists
        const plantReference = $('#plantReference').val().trim();
        if (!isUpdateMode && !plantReference) {
            alert('Please enter a plant reference (e.g., CHWP-01)');
            $('#plantReference').focus();
            return;
        }
        
        const configuration = {
            pump_id: pumpId,
            option_id: optionId,
            
            // Plant reference data
            plant_reference: plantReference,
            assembly_description: $('#assemblyDescription').val().trim(),
            quantity: parseInt($('#assemblyQuantity').val()) || 1,
            
            // Pricing
            margin_percentage: parseFloat($('#marginPercentage').val()) || 18.5,
            
            // Components
            mounting_type: $('input[name="mounting_type"]:checked').val(),
            crossbar_quantity: parseInt($('#crossbarQuantity').val()) || 2,
            spring_type: $('input[name="spring_type"]:checked').val(),
            spring_quantity: parseInt($('#springQuantity').val()) || 0,
            include_rubber_mounts: $('#includeRubberMounts').is(':checked'),
            rubber_mount_quantity: parseInt($('#rubberMountQuantity').val()) || 0,
            include_motor_protection: $('#includeMotorProtection').is(':checked'),
            include_drip_tray: $('#includeDripTray').is(':checked'),
            ip_rating: $('#ipRating').val()
        };
        
        // Show loading state
        const $btn = $(this);
        const originalText = $btn.text();
        const loadingText = isUpdateMode ? 'Updating...' : 'Adding...';
        $btn.prop('disabled', true).html(`<i class="fas fa-spinner fa-spin"></i> ${loadingText}`);
        
        // Determine API endpoint based on mode
        const url = isUpdateMode 
            ? `/deals/api/pump-assembly/${lineItemId}/update` 
            : '/deals/api/pump-assembly/add';
        const successMessage = isUpdateMode
            ? `Successfully updated pump assembly!`
            : `Successfully added pump assembly "${configuration.plant_reference}" (Qty: ${configuration.quantity}) to quote!`;
        
        // Call API endpoint
        $.ajax({
            url: url,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(configuration),
            success: function(response) {
                if (response.success) {
                    // Close modal
                    $('#pumpConfigModal').modal('hide');
                    
                    // Clear update mode flags
                    $('#pumpConfigModal').data('update-mode', false);
                    $('#pumpConfigModal').data('line-item-id', null);
                    
                    // Show success message
                    alert(successMessage);
                    
                    // Reload the page to show updated quote
                    window.location.reload();
                } else {
                    alert('Error: ' + (response.message || 'Unknown error'));
                    $btn.prop('disabled', false).text(originalText);
                }
            },
            error: function(xhr) {
                console.error('Error with pump assembly:', xhr);
                const errorMsg = xhr.responseJSON?.error || `Failed to ${isUpdateMode ? 'update' : 'add'} pump assembly`;
                alert('Error: ' + errorMsg);
                $btn.prop('disabled', false).text(originalText);
            }
        });
    });
    
    // Load pump series for filters
    function loadPumpSeries() {
        $.ajax({
            url: '/deals/api/pump-series',
            method: 'GET',
            success: function(series) {
                pumpSeries = series;
                populateSeriesFilters(series);
            },
            error: function(xhr) {
                console.error('Error loading pump series:', xhr);
            }
        });
    }
    
    function populateSeriesFilters(series) {
        const selects = [
            '#dutyPointSeriesFilter',
            '#manualSeriesFilter',
            '#browseSeriesFilter'
        ];
        
        selects.forEach(selector => {
            const select = $(selector);
            select.find('option:not(:first)').remove();
            
            series.forEach(s => {
                select.append(`<option value="${s.id}">${s.code}</option>`);
            });
        });
    }
    
    $('#backToSearch').on('click', function() {
        $('#pumpResults').hide();
        $('#dutyPointSearch').show();
    });
    
    // ========================================
    // Plant Reference Functionality
    // ========================================
    
    // Plant reference real-time preview
    $('#plantReference, #assemblyDescription').on('input', updateQuotePreview);
    
    // Use default button
    $('#useDefaultRef').on('click', function() {
        const defaultRef = $('#defaultPlantRef').text();
        $('#plantReference').val(defaultRef);
        updateQuotePreview();
    });
    
    // Quantity change handler - No longer needed for auto-increment
    // $('#assemblyQuantity').on('change', function() {
    //     const qty = parseInt($(this).val()) || 1;
    //     updateQuantityHint(qty);
    // });
    
    function updateQuotePreview() {
        const plantRef = $('#plantReference').val().trim() || $('#defaultPlantRef').text();
        const pumpName = $('#configPumpName').text() || 'Grundfos Pump';
        const description = $('#assemblyDescription').val().trim();
        
        $('#previewPlantRef').text(plantRef);
        $('#previewPumpName').text(pumpName);
        
        if (description) {
            $('#previewDescription').html(`<span style="color: #666;">${description}</span>`);
        } else {
            $('#previewDescription').html('<em style="color: #999;">(No description added)</em>');
        }
    }
    
    // Auto-increment hint function removed - user will manually set references
    // function updateQuantityHint(quantity) {
    //     if (quantity > 1) {
    //         const plantRef = $('#plantReference').val().trim() || 'PUMP-ASSY-001';
    //         const baseRef = plantRef.replace(/\d+$/, '');
    //         const match = plantRef.match(/(\d+)$/);
    //         const startNum = match ? parseInt(match[1]) : 1;
    //         
    //         const examples = [];
    //         for (let i = 0; i < Math.min(quantity, 3); i++) {
    //             const num = String(startNum + i).padStart(2, '0');
    //             examples.push(`${baseRef}${num}`);
    //         }
    //         
    //         if (quantity > 3) {
    //             examples.push('...');
    //         }
    //         
    //         $('#quantityHint').text(`Will create: ${examples.join(', ')}`);
    //     } else {
    //         $('#quantityHint').text('Auto-increment: CHWP-01, CHWP-02...');
    //     }
    // }
    
    function getNextAssemblyNumber() {
        // This will be replaced with actual logic to query existing line items
        // For now, return 1 as default
        // TODO: Query current quote option for existing PUMP-ASSY items
        return 1;
    }
    
    // Initialize tooltips
    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });
    
    // Initialize pump modal after dynamic content load
    function initializePumpModal() {
        // Re-bind any event handlers that might be needed
        // This function can be expanded as needed for modal re-initialization
        console.log('Pump modal initialized');
    }
});

