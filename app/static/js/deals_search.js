document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('dealsSearchInput');
    const searchBtn = document.getElementById('searchBtn');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    let debounceTimer;
    let searchResultsDropdown = null;
    
    // Create search results dropdown
    function createSearchDropdown() {
        if (!searchResultsDropdown) {
            searchResultsDropdown = document.createElement('div');
            searchResultsDropdown.id = 'dealsSearchResults';
            searchResultsDropdown.className = 'absolute z-50 w-full mt-2 bg-gray-700 border border-gray-700 rounded-lg shadow-xl max-h-96 overflow-y-auto hidden';
            searchInput.parentElement.appendChild(searchResultsDropdown);
        }
        return searchResultsDropdown;
    }
    
    // Show/hide clear button based on input value
    function toggleClearButton() {
        if (searchInput.value.trim()) {
            clearSearchBtn.style.display = 'block';
        } else {
            clearSearchBtn.style.display = 'none';
        }
    }
    
    // Perform live search
    async function performLiveSearch(query) {
        const dropdown = createSearchDropdown();
        
        if (!query || query.length < 2) {
            dropdown.classList.add('hidden');
            return;
        }
        
        try {
            // Show loading state
            dropdown.innerHTML = '<div class="p-4 text-center text-gray-400"><i class="fas fa-spinner fa-spin mr-2"></i>Searching...</div>';
            dropdown.classList.remove('hidden');
            
            const response = await fetch(`/deals/?search=${encodeURIComponent(query)}`);
            const html = await response.text();
            
            // Parse the response to extract deals
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const dealCards = doc.querySelectorAll('.deal-card');
            
            if (dealCards.length === 0) {
                dropdown.innerHTML = `
                    <div class="p-6 text-center">
                        <i class="fas fa-search text-4xl text-gray-600 mb-3"></i>
                        <p class="text-gray-400">No deals found matching "${query}"</p>
                        <p class="text-xs text-gray-500 mt-2">Try a different search term</p>
                    </div>
                `;
            } else {
                dropdown.innerHTML = '<div class="p-2"><p class="text-xs text-gray-500 uppercase tracking-wider px-3 py-2">Results (' + dealCards.length + ')</p></div>';
                
                const resultsContainer = document.createElement('div');
                resultsContainer.className = 'divide-y divide-gray-600';
                
                dealCards.forEach((card, index) => {
                    if (index >= 10) return; // Limit to 10 results
                    
                    const dealId = card.dataset.dealId;
                    const dealName = card.querySelector('h4')?.textContent.trim() || 'Unknown';
                    const dealValue = card.querySelector('.text-green-400')?.textContent.trim() || '$0';
                    const dealType = card.querySelector('.inline-flex.items-center')?.textContent.trim() || '';
                    const dealStage = card.closest('.kanban-cards-container')?.dataset.stage || 'Unknown';
                    
                    const resultItem = document.createElement('a');
                    resultItem.href = `/deals/${dealId}`;
                    resultItem.className = 'flex items-center justify-between p-3 hover:bg-gray-600 transition-colors cursor-pointer group';
                    resultItem.innerHTML = `
                        <div class="flex-1 min-w-0">
                            <p class="text-white font-medium truncate group-hover:text-blue-400 transition-colors">${dealName}</p>
                            <div class="flex items-center gap-2 mt-1">
                                <span class="text-xs text-gray-400">#${dealId}</span>
                                <span class="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-300">${dealType}</span>
                                <span class="text-xs text-gray-500">${dealStage}</span>
                            </div>
                        </div>
                        <div class="text-right ml-4">
                            <p class="text-green-400 font-bold">${dealValue}</p>
                        </div>
                    `;
                    
                    resultsContainer.appendChild(resultItem);
                });
                
                dropdown.appendChild(resultsContainer);
                
                // Add "View all results" button
                if (dealCards.length > 10) {
                    const viewAllBtn = document.createElement('a');
                    viewAllBtn.href = `/deals/?search=${encodeURIComponent(query)}`;
                    viewAllBtn.className = 'block p-3 text-center text-blue-400 hover:bg-gray-600 border-t border-gray-600 transition-colors';
                    viewAllBtn.innerHTML = `<i class="fas fa-arrow-right mr-2"></i>View all ${dealCards.length} results`;
                    dropdown.appendChild(viewAllBtn);
                }
            }
        } catch (error) {
            console.error('Search error:', error);
            dropdown.innerHTML = '<div class="p-4 text-center text-red-400"><i class="fas fa-exclamation-circle mr-2"></i>Error performing search</div>';
        }
    }
    
    // Debounced search function
    function debouncedSearch(query) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => performLiveSearch(query), 300);
    }
    
    // Perform full page search
    function performSearch() {
        const searchValue = searchInput.value.trim();
        const currentUrl = new URL(window.location);
        
        if (searchValue) {
            currentUrl.searchParams.set('search', searchValue);
        } else {
            currentUrl.searchParams.delete('search');
        }
        
        window.location.href = currentUrl.toString();
    }
    
    // Clear search
    function clearSearch() {
        searchInput.value = '';
        toggleClearButton();
        const dropdown = document.getElementById('dealsSearchResults');
        if (dropdown) dropdown.classList.add('hidden');
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.delete('search');
        window.location.href = currentUrl.toString();
    }
    
    // Event listeners
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            toggleClearButton();
            debouncedSearch(this.value.trim());
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Hide dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResultsDropdown?.contains(e.target)) {
                const dropdown = document.getElementById('dealsSearchResults');
                if (dropdown) dropdown.classList.add('hidden');
            }
        });
    }
    
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', clearSearch);
    }
    
    // Initialize clear button state
    toggleClearButton();
}); 