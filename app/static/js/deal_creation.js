document.addEventListener('DOMContentLoaded', function () {
    // This script should only run when the #createDealModal is present
    const createDealModal = document.getElementById('createDealModal');
    if (!createDealModal) {
        return;
    }

    // --- Element Selectors ---
    const contactSection = document.getElementById('contact-search-section');
    const companySection = document.getElementById('company-search-section');
    const contactSearchInput = document.getElementById('contact-search-input');
    const companySearchInput = document.getElementById('company-search-input');
    const contactResults = document.getElementById('contact-search-results');
    const companyResults = document.getElementById('company-search-results');
    const contactIdField = document.getElementById('contact_id');
    const companyIdField = document.getElementById('company_id');
    const toggleToCompany = document.getElementById('toggle-search-mode');
    const toggleToContact = document.getElementById('toggle-search-mode-2');

    // --- Debounce function to limit API calls while typing ---
    let debounceTimer;
    const debounce = (callback, time) => {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(callback, time);
    };

    // --- Main Search Function ---
    const performSearch = async (query, type, resultsContainer) => {
        if (query.length < 2) {
            resultsContainer.classList.add('hidden');
            return;
        }

        try {
            const response = await fetch(`/deals/search/modal?type=${type}&q=${query}`);
            if (!response.ok) throw new Error('Network response was not ok');
            const results = await response.json();
            renderResults(results, type, resultsContainer);
        } catch (error) {
            console.error(`Error fetching ${type} data:`, error);
            resultsContainer.innerHTML = `<li class="no-results">Error loading results.</li>`;
            resultsContainer.classList.remove('hidden');
        }
    };

    // --- Render Search Results ---
    const renderResults = (results, type, resultsContainer) => {
        resultsContainer.innerHTML = ''; // Clear previous results
        
        if (results.length > 0) {
            // Add header
            const header = document.createElement('div');
            header.className = 'px-3 py-2 bg-gray-800 border-b border-gray-600';
            header.innerHTML = `<p class="text-xs text-gray-400 uppercase tracking-wider">Found ${results.length} ${type === 'contact' ? 'contact(s)' : 'company(ies)'}</p>`;
            resultsContainer.appendChild(header);
            
            results.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'group';
                li.dataset.id = item.id;
                li.dataset.text = item.text;
                
                // Enhanced display with icon
                const icon = type === 'contact' ? 'fa-user' : 'fa-building';
                const iconColor = type === 'contact' ? 'text-blue-400' : 'text-green-400';
                
                li.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="flex items-center justify-center w-8 h-8 bg-gray-800 rounded-full">
                            <i class="fas ${icon} ${iconColor} text-xs"></i>
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-white group-hover:text-blue-400 font-medium truncate transition-colors">${item.text}</p>
                            ${item.email ? `<p class="text-xs text-gray-500 truncate">${item.email}</p>` : ''}
                        </div>
                        <i class="fas fa-chevron-right text-gray-600 group-hover:text-blue-400 transition-colors text-xs"></i>
                    </div>
                `;
                
                resultsContainer.appendChild(li);
            });
        } else {
            // Show "No results" message
            const noResults = document.createElement('div');
            noResults.className = 'p-6 text-center';
            noResults.innerHTML = `
                <i class="fas fa-search text-4xl text-gray-600 mb-3"></i>
                <p class="text-gray-400 font-medium">No ${type.replace('_', ' ')} found</p>
                <p class="text-xs text-gray-500 mt-1">Try a different search term</p>
            `;
            resultsContainer.appendChild(noResults);
            
            if (type === 'contact') {
                const createBtn = document.createElement('button');
                createBtn.type = 'button';
                createBtn.className = 'mt-3 inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm';
                createBtn.innerHTML = '<i class="fas fa-plus"></i><span>Create New Contact</span>';
                createBtn.onclick = () => alert('Functionality to create a new contact will be added here.');
                noResults.appendChild(createBtn);
            }
        }
        resultsContainer.classList.remove('hidden');
    };

    // --- Event Listeners for Inputs ---
    contactSearchInput.addEventListener('keyup', () => {
        debounce(() => performSearch(contactSearchInput.value, 'contact', contactResults), 300);
    });

    companySearchInput.addEventListener('keyup', () => {
        debounce(() => performSearch(companySearchInput.value, 'company', companyResults), 300);
    });

    // --- Event Listener for Selecting a Result ---
    const handleResultSelection = (e, type) => {
        const target = e.target;
        if (target.tagName === 'LI' && target.dataset.id) {
            const id = target.dataset.id;
            const text = target.dataset.text;
            
            if (type === 'contact') {
                contactSearchInput.value = text;
                contactIdField.value = id;
                companyIdField.value = ''; // Clear company if contact is selected
                contactResults.classList.add('hidden');
            } else if (type === 'company') {
                companySearchInput.value = text;
                companyIdField.value = id;
                contactIdField.value = ''; // Clear contact if company is selected
                companyResults.classList.add('hidden');
            }
        }
    };

    contactResults.addEventListener('click', (e) => handleResultSelection(e, 'contact'));
    companyResults.addEventListener('click', (e) => handleResultSelection(e, 'company'));

    // --- Event Listeners for Toggling Search Mode ---
    toggleToCompany.addEventListener('click', (e) => {
        e.preventDefault();
        contactSection.classList.add('hidden');
        companySection.classList.remove('hidden');
    });

    toggleToContact.addEventListener('click', (e) => {
        e.preventDefault();
        companySection.classList.add('hidden');
        contactSection.classList.remove('hidden');
    });

    // Hide results when clicking outside
    document.addEventListener('click', function(event) {
        if (!contactSearchInput.contains(event.target)) contactResults.classList.add('hidden');
        if (!companySearchInput.contains(event.target)) companyResults.classList.add('hidden');
    });
});