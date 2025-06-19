// This script controls the behavior of the searchable modal window.

// A global variable to keep track of what we are currently searching for.
// This will be set to 'company', 'contact', or 'deal_owner'.
let currentSearchType = null;

// A mapping of search types to their corresponding API endpoints.
const searchEndpoints = {
    company: '/quotes/api/search/companies',
    contact: '/quotes/api/search/contacts',
    deal_owner: '/quotes/api/search/deal_owners'
};

// This function is called by the "Search" buttons in the form.
function openSearchModal(searchType) {
    // Store the type of search we're performing.
    currentSearchType = searchType;

    // Set a descriptive title for the modal.
    const modalTitle = document.getElementById('searchModalLabel');
    modalTitle.textContent = `Search for a ${searchType.replace('_', ' ')}`;

    // Clear any previous search results and input text.
    document.getElementById('modalSearchInput').value = '';
    document.getElementById('modalResultsList').innerHTML = '';

    // Use jQuery (which is included in base.html) to show the Bootstrap modal.
    $('#searchModal').modal('show');
}

// This function is called when an item is clicked in the search results.
function selectItem(id, text) {
    // Based on the current search type, update the correct fields on the main form.
    if (currentSearchType) {
        // Update the visible text input (which is read-only).
        document.getElementById(`${currentSearchType}_name`).value = text;
        // Update the hidden input that stores the ID for form submission.
        document.getElementById(`${currentSearchType}_id`).value = id;
    }

    // Hide the modal window.
    $('#searchModal').modal('hide');
}

// This function fetches results from the server as the user types.
async function fetchResults(query) {
    // Don't search if the query is too short.
    if (query.length < 2) {
        document.getElementById('modalResultsList').innerHTML = '';
        return;
    }

    // Get the correct API endpoint for the current search type.
    const endpoint = searchEndpoints[currentSearchType];
    if (!endpoint) return;

    try {
        // Use the Fetch API to make a request to our backend.
        const response = await fetch(`${endpoint}?q=${query}`);
        const results = await response.json();

        // Pass the results to another function to display them.
        displayResults(results);
    } catch (error) {
        console.error('Error fetching search results:', error);
    }
}

// This function takes the JSON data from the server and builds the HTML list.
function displayResults(results) {
    const resultsList = document.getElementById('modalResultsList');
    // Clear any old results.
    resultsList.innerHTML = '';

    if (results.length === 0) {
        resultsList.innerHTML = '<li class="list-group-item">No results found.</li>';
        return;
    }

    // Loop through each result and create a clickable list item.
    results.forEach(result => {
        const li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action';
        li.textContent = result.text;
        // When clicked, it calls the selectItem function with its ID and text.
        li.onclick = () => selectItem(result.id, result.text);
        resultsList.appendChild(li);
    });
}

// Wait for the whole document to be loaded before we attach event listeners.
document.addEventListener('DOMContentLoaded', function() {
    const modalSearchInput = document.getElementById('modalSearchInput');
    
    // Add an event listener to the search input field inside the modal.
    // It will call fetchResults every time the user types a key.
    if (modalSearchInput) {
        modalSearchInput.addEventListener('keyup', (event) => {
            fetchResults(event.target.value);
        });
    }
});