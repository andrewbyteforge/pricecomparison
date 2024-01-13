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

// Function to add an item to the basket when the user clicks the add button
function addToBasket(element) {
    // Get the store, name, and price from the data attributes of the clicked element
    var store = element.getAttribute('data-store');
    var name = element.getAttribute('data-name');
    var price = element.getAttribute('data-price');

    

    

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
        // Check if the response from the server is not successful
        if (!response.ok) {
            // If not successful, throw an error
            throw new Error('Network response was not ok');
        }
        // If successful, parse the JSON body of the response
        location.reload();
        return response.json();
    })
    .then(data => {
        if (data && data.store && data.name && data.price && data.itemId) {
            // Update the UI with the new item, including the itemId
            updateBasketUI(data.store, data.name, data.price, data.itemId);
        } else {
            console.error("Invalid or missing data from server:", data);
        }
    })
    .catch((error) => {
        // Log any errors to the console
        console.error('Error:', error);
    });
}

// Function to remove an item from the basket and recalculate total price
function removeItemFromBasket(buttonElement) {
    console.log("removeItemFromBasket called");
    
    var itemId = buttonElement.getAttribute('data-item-id');
    console.log("Item ID:", itemId);

    if (!itemId) {
        console.error("Item ID is not provided or invalid.");
        return;
    }

    fetch('/asda/remove_from_basket/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 'item_id': itemId })
    })
    .then(response => {
        if (!response.ok) {
            console.error(`Server responded with status: ${response.status}`);
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            buttonElement.closest('tr').remove();
            recalculateTotalPrice();
            showAlert('alert-info', "The product has been successfully removed from your basket!");
        

            // Call the function to update the total price from the server
            fetchUpdatedTotalPrice();           
        } else {
            console.error("Failed to remove item: ", data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

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



// Function to update the basket UI with a new item
function updateBasketUI(store, name, price, itemId) {
    // Input validation
    if (!store || !name || !price || !itemId) {
        console.error('Invalid input parameters provided to updateBasketUI');
        return;
    }

    // Reference to the basket table body
    var basketTableBody = document.getElementById('basket')?.getElementsByTagName('tbody')[0];
    if (!basketTableBody) {
        console.error('Basket table body not found');
        return;
    }

    try {
        // Add a new row at the end of the basket table
        var newRow = basketTableBody.insertRow(-1);

        // Create and append cells to the new row
        for (var i = 0; i < 6; i++) {
            var cell = newRow.insertCell(i);
            if (store === 'Tesco' && i === 1) {
                cell.appendChild(createPriceSpan('tesco-price', price));
                cell.appendChild(createRemoveButton(itemId, 'Tesco'));
            } else if (store === 'Asda' && i === 3) {
                cell.appendChild(createPriceSpan('asda-price', price));
                cell.appendChild(createRemoveButton(itemId, 'Asda'));
            } else if (store === 'Sainsburys' && i === 5) {
                cell.appendChild(createPriceSpan('sainsburys-price', price));
                cell.appendChild(createRemoveButton(itemId, 'Sainsburys'));
            }
        }

        // Set the name in the corresponding cell based on the store
        if (store === 'Tesco') {
            newRow.cells[0].textContent = name;
        } else if (store === 'Asda') {
            newRow.cells[2].textContent = name;
        } else if (store === 'Sainsburys') {
            newRow.cells[4].textContent = name;
        }

        // Update the total price
        if (typeof updateTotalPrice === 'function') {
            updateTotalPrice(store, parseFloat(price));
        } else {
            console.error('updateTotalPrice is not a function');
        }
    } catch (error) {
        console.error('Error updating basket UI:', error);
    }
}

function createPriceSpan(className, price) {
    var span = document.createElement('span');
    span.className = className;
    span.textContent = price;
    return span;
}

function createRemoveButton(itemId, store) {
    var button = document.createElement('button');
    button.className = 'btn btn-danger btn-sm';
    button.textContent = 'REMOVE';
    button.setAttribute('data-item-id', itemId);
    button.setAttribute('data-store', store);
    button.onclick = function() { removeItemFromBasket(this); };
    return button;
}





// Function to recalculate the total price of items in the shopping basket
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



// Function to update the total price for a specific store
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



// Helper function to get the value of a specified cookie by name
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
