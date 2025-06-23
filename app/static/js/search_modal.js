// /static/js/search_modal.js

document.addEventListener('DOMContentLoaded', () => {
    const searchModal = document.getElementById('searchModal');
    if (!searchModal) {
        return; // Exit if the modal is not on the page
    }

    let currentSearchType = 'company'; // Default search type

    const companySearchBtn = document.getElementById('searchCompanyBtn');
    const contactSearchBtn = document.getElementById('searchContactBtn');
    const searchInput = document.getElementById('searchInput');
    const searchResultsContainer = document.getElementById('searchResults');
    const entityIdInput = document.getElementById('entityId'); // Hidden input in the create deal form

    function setupEventListeners() {
        if(companySearchBtn) {
            companySearchBtn.addEventListener('click', () => {
                currentSearchType = 'company';
                performSearch(searchInput.value);
            });
        }

        if(contactSearchBtn) {
            contactSearchBtn.addEventListener('click', () => {
                currentSearchType = 'contact';
                performSearch(searchInput.value);
            });
        }
        
        // Use event delegation for dynamically added result items
        searchResultsContainer.addEventListener('click', (event) => {
            const target = event.target;
            // Check if a result item or its child was clicked
            const resultItem = target.closest('.search-result-item');
            if (resultItem) {
                const entityName = resultItem.textContent;
                const entityId = resultItem.dataset.id;
                
                // Update the hidden form input with the selected ID
                if(entityIdInput) {
                    entityIdInput.value = entityId;
                }
                
                // Update the visible input field to show the selection
                const searchEntityInput = document.getElementById('searchEntityInput');
                if(searchEntityInput) {
                    searchEntityInput.value = entityName.trim();
                }

                // Programmatically close the Bootstrap modal
                const closeButton = searchModal.querySelector('[data-dismiss="modal"]');
                if(closeButton) {
                    closeButton.click();
                }
            }
        });
    }

    function performSearch(query) {
        if (!query || query.length < 2) {
            searchResultsContainer.innerHTML = '<p>Please enter at least 2 characters.</p>';
            return;
        }

        const url = `/search/${currentSearchType}?query=${encodeURIComponent(query)}`;
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok.');
                }
                return response.json();
            })
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                searchResultsContainer.innerHTML = '<p>Error fetching results. Please try again.</p>';
            });
    }

    function displayResults(data) {
        searchResultsContainer.innerHTML = ''; // Clear previous results

        if (data.length === 0) {
            searchResultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }

        const list = document.createElement('ul');
        list.className = 'list-group';

        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item list-group-item-action search-result-item';
            listItem.textContent = item.name;
            listItem.dataset.id = item.id;
            listItem.style.cursor = 'pointer';
            list.appendChild(listItem);
        });
        
        searchResultsContainer.appendChild(list);
    }
    
    setupEventListeners();
});