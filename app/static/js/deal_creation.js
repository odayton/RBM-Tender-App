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
            resultsContainer.classList.add('d-none');
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
            resultsContainer.classList.remove('d-none');
        }
    };

    // --- Render Search Results ---
    const renderResults = (results, type, resultsContainer) => {
        resultsContainer.innerHTML = ''; // Clear previous results
        if (results.length > 0) {
            results.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.text;
                li.dataset.id = item.id;
                li.dataset.text = item.text;
                resultsContainer.appendChild(li);
            });
        } else {
            // Show "Create New" option if no results are found
            const li = document.createElement('li');
            li.textContent = `No ${type.replace('_', ' ')} found.`;
            li.classList.add('no-results');
            resultsContainer.appendChild(li);
            
            if (type === 'contact') {
                const createLi = document.createElement('li');
                createLi.textContent = '＋ Create New Contact';
                createLi.classList.add('create-new-button');
                // We will add functionality to this button in a later step
                createLi.onclick = () => alert('Functionality to create a new contact will be added here.');
                resultsContainer.appendChild(createLi);
            }
        }
        resultsContainer.classList.remove('d-none');
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
                contactResults.classList.add('d-none');
            } else if (type === 'company') {
                companySearchInput.value = text;
                companyIdField.value = id;
                contactIdField.value = ''; // Clear contact if company is selected
                companyResults.classList.add('d-none');
            }
        }
    };

    contactResults.addEventListener('click', (e) => handleResultSelection(e, 'contact'));
    companyResults.addEventListener('click', (e) => handleResultSelection(e, 'company'));

    // --- Event Listeners for Toggling Search Mode ---
    toggleToCompany.addEventListener('click', (e) => {
        e.preventDefault();
        contactSection.classList.add('d-none');
        companySection.classList.remove('d-none');
    });

    toggleToContact.addEventListener('click', (e) => {
        e.preventDefault();
        companySection.classList.add('d-none');
        contactSection.classList.remove('d-none');
    });

    // Hide results when clicking outside
    document.addEventListener('click', function(event) {
        if (!contactSearchInput.contains(event.target)) contactResults.classList.add('d-none');
        if (!companySearchInput.contains(event.target)) companyResults.classList.add('d-none');
    });
});