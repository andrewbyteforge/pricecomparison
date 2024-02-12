/**
 * This JavaScript code manages the functionality of a shopping basket in a web application, 
 * specifically handling the addition and removal of items from the basket and updating the total price.
 * 
 * The process starts when a user interacts with the webpage, typically by clicking buttons 
 * to add or remove items from their shopping basket.
 * 
 * - Adding an Item to the Basket:
 *   1. The 'addToBasket' function is triggered when a user clicks an 'Add' button associated with a product.
 *      This function retrieves the store name, product name, and price from the button's data attributes.
 *   2. A POST request is sent to the server with the product details. 
 *      The server responds with confirmation and the product details.
 *   3. Upon successful response, 'updateBasketUI' function is called, which inserts a new row 
 *      into the basket table with the product details and a 'Remove' button.
 *   4. 'updateTotalPrice' function is also called to update the total price for the respective store.
 * 
 * - Removing an Item from the Basket:
 *   1. The 'removeItemFromBasket' function is invoked when a user clicks a 'Remove' button in the basket.
 *      This function sends the item ID to the server via a POST request for removal.
 *   2. If the server confirms the removal, the corresponding row in the basket table is removed.
 *   3. 'recalculateTotalPrice' function is then called to update the total prices for all stores.
 * 
 * - Recalculating Total Price:
 *   1. 'recalculateTotalPrice' iterates over all items in the basket, sums up the prices for each store,
 *      and updates the total price display for Tesco, Asda, and Sainsburys.
 * 
 * - Utility Functions:
 *   - 'getCookie' is used to retrieve the CSRF token required for secure POST requests.
 *   - 'updateBasketUI' handles the dynamic update of the basket's UI.
 *   - 'updateTotalPrice' updates the total price for a specific store after adding an item.
 * 
 * This set of functions provides an interactive and responsive user experience, allowing 
 * real-time update of the basket contents and total price calculation.
 */

// *************************************************************************
// Function to add an item to the basket when the user clicks the add button
// *************************************************************************
function addToBasket(element) { 
    console.log('addToBasket function called', element);  
    // Get the store, name, and price from the data attributes of the clicked element
    var store = element.getAttribute('data-store');
    var name = element.getAttribute('data-name');
    var price = element.getAttribute('data-price');  

    const payload = { store: store, name: name, price: price };
    console.log("Sending payload:", payload);
    fetch('/asda/add_to_basket/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
    });

    // Send a POST request to the server to add the item to the basket
    fetch('/asda/add_to_basket/', {
        method: 'POST', // The HTTP method for the request
        headers: {
            // Set the Content-Type header to application/json to send the body as JSON
            'Content-Type': 'application/json',
            // Include CSRF token for protection against Cross-Site Request Forgeries
            'X-CSRFToken': getCookie('csrftoken')
        },
        // Stringify the item data into JSON to send as the body of the request
        body: JSON.stringify({store: store, name: name, price: price})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Wait to parse the response
    })
    .then(data => {
        if (data && data.store && data.name && data.price && data.itemId) {
            updateBasketUI(data.store, data.name, data.price, data.itemId); // Update UI
            // Add to local storage
            let basket = JSON.parse(localStorage.getItem('basket') || '[]');
            basket.push({ store: data.store, name: data.name, price: data.price, itemId: data.itemId });
            localStorage.setItem('basket', JSON.stringify(basket));
        } else {
            console.error("Invalid or missing data from server:", data);
        }
    })
    .catch((error) => {
        // Log any errors to the console
        console.error('Error:', error);
    });
}

// **********************************************************************
// Function to remove an item from the basket 
// **********************************************************************
// function removeItemFromBasket(element) {
//     const itemId = element.getAttribute('data-item-id'); // Correctly obtaining the item ID
    
//     // Correctly specify the endpoint and include CSRF token
//     fetch('/asda/remove_from_basket/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCookie('csrftoken'), // Ensure CSRF token is correctly included
//         },
//         body: JSON.stringify({ item_id: itemId })
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error(`Network response was not ok: ${response.statusText}`);
//         }
//         return response.json();
//     })
//     .then(data => {
//         if (data.success) {
//             // Correctly use `element` to refer to the button that was clicked
//             element.closest('tr').remove(); // Remove the item from the UI
//             recalculateTotalPrice(); // Update total price accordingly
//         } else {
//             console.error("Failed to remove item: ", data.error || 'Unknown error');
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// }

function updateNoItemsRowVisibility() {
    // Check if there are any rows for Asda items
    const asdaItemsExist = document.querySelectorAll('#asda-basket tbody tr').length > 0;
    const noItemsRow = document.getElementById('no-items-row');
    
    if (asdaItemsExist) {
        // If there are Asda items, ensure the "No items" row is hidden
        if (noItemsRow) noItemsRow.style.display = 'none';
    } else {
        // If there are no Asda items, show the "No items" row
        if (noItemsRow) noItemsRow.style.display = '';
    }
}

// Call this function after any operation that adds or removes items
updateNoItemsRowVisibility();



function removeItemFromBasket(itemId) {
    // Remove the item from local storage
    var basket = JSON.parse(localStorage.getItem('basket') || '[]');
    var newBasket = basket.filter(function(item) {
        return item.itemId !== itemId;
    });
    localStorage.setItem('basket', JSON.stringify(newBasket));

    // Optionally, make a server request here to sync the state

    // Reload the basket from local storage to reflect changes in the UI
    loadBasketFromLocalStorage();
}





// **********************************************************************
// Function to update the basket UI with a new item
// **********************************************************************
function updateBasketUI(store, name, price, itemId) {
    if (!store || !name || !price || !itemId) {
        console.error('Invalid input parameters provided to updateBasketUI');
        return;
    }

    var basketTableBody = document.getElementById('asda-basket')?.getElementsByTagName('tbody')[0];
    if (!basketTableBody) {
        console.error('Basket table body not found');
        return;
    }

    try {
        // Add a new row at the end of the basket table
        var newRow = basketTableBody.insertRow(-1);

        // Insert cell for the item name
        var nameCell = newRow.insertCell(0);
        nameCell.textContent = name;

        // Insert cell for the price
        var priceCell = newRow.insertCell(1);
        priceCell.textContent = `£${price}`;

        // Insert cell for the remove button
        var removeButtonCell = newRow.insertCell(2);
        var removeButton = createRemoveButton(itemId, store); 
        removeButtonCell.appendChild(removeButton);
    document.getElementById('no-items-row').style.display = 'none';

    } catch (error) {
        console.error('Error updating basket UI:', error);
    }
}


// *************************************************************************
// Functions remove button setup
// *************************************************************************
function setupRemoveButton(buttonElement, itemId) {
    buttonElement.addEventListener('click', () => {
        removeItemFromLocalStorage(itemId);        
    });
}

// *************************************************************************
// Create an HTML button that removes an item with the given id from the user's basket
// *************************************************************************
function createPriceSpan(className, price) {
    var span = document.createElement('span');
    span.className = className;
    span.textContent = price;
    return span;
}

// *************************************************************************
// Returns a button element which, when clicked, will remove the specified item from the user's
// *************************************************************************
function createRemoveButton(itemId, store) {
    var button = document.createElement('button');
    button.className = 'btn btn-danger btn-sm';
    button.textContent = 'REMOVE';
    button.setAttribute('data-item-id', itemId);
    button.setAttribute('data-store', store);
    button.onclick = function() { removeItemFromBasket(this); };
    return button;
}


// **********************************************************************
// Update total Price
// **********************************************************************
function fetchUpdatedTotalPrice() {
    $.ajax({
        url: '/asda/get_updated_total/',
        success: function(response) {
            console.log("Updated total from server:", response.newTotal);
            $('#total-price').text(response.newTotal);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching updated total:', error);
        }
    });
}

// *************************************************************************
// Function to recalculate the total price of items in the shopping basket
// *************************************************************************
function recalculateTotalPrice() {
    let tescoTotalPrice = 0, asdaTotalPrice = 0, sainsburysTotalPrice = 0;

    // Sum prices for Tesco items
    document.querySelectorAll('.tesco-price').forEach(function(priceElement) {
        tescoTotalPrice += parseFloat(priceElement.textContent.replace('£', '') || 0);
    });

    // Sum prices for Asda items
    document.querySelectorAll('.asda-price').forEach(function(priceElement) {
        asdaTotalPrice += parseFloat(priceElement.textContent.replace('£', '') || 0);
    });

    // Sum prices for Sainsburys items
    document.querySelectorAll('.sainsburys-price').forEach(function(priceElement) {
        sainsburysTotalPrice += parseFloat(priceElement.textContent.replace('£', '') || 0);
    });

    // Update total price displays
    document.getElementById('tesco-total').textContent = `£${tescoTotalPrice.toFixed(2)}`;
    document.getElementById('asda-total').textContent = `£${asdaTotalPrice.toFixed(2)}`;
    document.getElementById('sainsburys-total').textContent = `£${sainsburysTotalPrice.toFixed(2)}`;
}


// *************************************************************************
// Function to update the total price for a specific store
// *************************************************************************
function updateTotalPrice(store, priceChange) {
    // Retrieve the total price element for the specified store from the DOM
    // The 'store' variable is expected to be the name of the store (e.g., 'Tesco', 'Asda', 'Sainsburys')
    // The 'toLowerCase()' method is used to ensure the store name matches the ID format in the HTML
    var totalPriceElement = document.getElementById(store.toLowerCase() + '-total');

    // Parse the current total price from the total price element
    // 'parseFloat' is used to convert the string to a floating-point number
    // The 'replace' method removes the pound sign '£' for proper conversion to a number
    // The '|| 0' ensures that if the current total is not a number, it defaults to 0
    var currentTotal = parseFloat(totalPriceElement.innerHTML.replace('£', '')) || 0;

    // Calculate the new total price by adding the price change to the current total
    // The 'priceChange' variable can be positive (for adding an item) or negative (for removing an item)
    var newTotal = currentTotal + priceChange;
    // If the new total is zero, hide the "Your total" message and show the
    // "You haven't added anything yet" message instead
    if (newTotal === 0) {
        totalPriceElement.nextElementSibling.style.display = 'block';
        totalPriceElement.style.display = 'none';
        } else {
            totalPriceElement.nextElementSibling.style.display = 'none';
            totalPriceElement.style.display = 'inline';
            }
            // Set the new total price in the total price element using innerHTML
            // We use 'innerHTML' rather than 'innerText' because we want any HTML within the
            // price display to be rendered properly (e.g., allowing £ signs to appear).
            totalPriceElement.innerHTML = `£${newTotal.toFixed(2)}`;
            // Update the overall total prices            
            }
    // Update the total price element's content with the new total price
    // 'Math.max' is used to ensure the total price doesn't go below 0
    // 'toFixed(2)' formats the number to two decimal places, representing pounds and pence


// *************************************************************************
// Helper function to get the value of a specified cookie by name
// *************************************************************************
function getCookie(name) {
    // Initialize cookieValue as null, it will store the value of the cookie if found
    let cookieValue = null;

    // Check if the document has any cookies and they are not an empty string
    if (document.cookie && document.cookie !== '') {
        // Split the document.cookie string into an array of individual cookies
        const cookies = document.cookie.split(';');

        // Iterate through each cookie in the array
        for (let i = 0; i < cookies.length; i++) {
            // Trim leading and trailing whitespace from the cookie string
            const cookie = cookies[i].trim();

            // Check if the current cookie string starts with the name we are looking for
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                // If found, decode the cookie value and assign it to cookieValue
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;  // Break out of the loop as we found the cookie we were looking for
            }
        }
    }
    // Return the value of the cookie, or null if the cookie was not found
    return cookieValue;
}



// *************************************************************************
function loadBasketFromLocalStorage() {
    // Retrieve the basket from local storage
    var basket = JSON.parse(localStorage.getItem('basket') || '[]');
    var basketTableBody = document.getElementById('asda-basket').getElementsByTagName('tbody')[0];

    // Clear the current basket UI
    basketTableBody.innerHTML = '';

    // Iterate over the basket items and add them to the UI
    basket.forEach(function(item) {
        var row = basketTableBody.insertRow();
        var nameCell = row.insertCell(0);
        var priceCell = row.insertCell(1);
        var removeButtonCell = row.insertCell(2);
        nameCell.textContent = item.name;
        priceCell.textContent = `£${item.price}`;
        
        // Create a remove button for each item
        var removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.className = 'btn btn-danger';
        removeButton.onclick = function() {
            // Functionality to remove item from basket
            removeItemFromBasket(item.itemId);
        };
        removeButtonCell.appendChild(removeButton);
    });
}

// Call this function when the document is fully loaded
document.addEventListener('DOMContentLoaded', loadBasketFromLocalStorage);