// *************************************************************************
// Function to add an item to the basket when the user clicks the add button
// *************************************************************************
function addToBasket(element) {
  // Get the store, name, and price from the data attributes of the clicked element
  var store = element.getAttribute("data-store");
  var name = element.getAttribute("data-name");
  var price = element.getAttribute("data-price");

  const payload = { store: store, name: name, price: price };

  fetch("/asda/add_to_basket/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(payload),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json(); // Wait to parse the response
    })
    .then((data) => {
      if (data && data.store && data.name && data.price && data.itemId) {
        updateBasketUI(data.store, data.name, data.price, data.itemId); // Update UI
        updateTotalAfterOperation(); // Update total price after adding item

        // Add to local storage
        let basket = JSON.parse(localStorage.getItem("basket") || "[]");

        // Clear the basket if it's empty
        if (basket.length === 0) {
          localStorage.setItem("basket", JSON.stringify([]));
        }

        // Check if the item already exists in the basket
        if (!basket.some((item) => item.itemId === data.itemId)) {
          basket.push({
            store: data.store,
            name: data.name,
            price: data.price,
            itemId: data.itemId,
          });
          localStorage.setItem("basket", JSON.stringify(basket));
        } else {
          console.log("Item already exists in the basket.");
        }
      } else {
        console.error("Invalid or missing data from server:", data);
      }
    })
    .catch((error) => {
      // Log any errors
      console.error("Error during fetch:", error);
    });
}

// *************************************************************************
// Function to recalculate the total price after an item has been removed
// *************************************************************************
function recalculateTotalAfterRemoval() {
  // Retrieve the current basket from local storage
  let basket = JSON.parse(localStorage.getItem("basket") || "[]");

  // Calculate the new total price by summing the price of each item in the basket
  let newTotalPrice = basket.reduce((total, item) => {
    return total + parseFloat(item.price);
  }, 0);

  // Update the UI to reflect the new total price
  document.getElementById("asda-total").textContent = `£${newTotalPrice.toFixed(
    2
  )}`;

  // Update the total price in local storage
  localStorage.setItem("asdaTotalPrice", newTotalPrice.toFixed(2));

  // Ensure the UI accurately reflects an empty basket or the new total as appropriate
  if (basket.length === 0) {
    document.getElementById("asda-total").textContent = "£0.00";
    // Optionally, you might want to ensure any visual indication of an empty basket is also shown
  }
}

// *************************************************************************
// Function to remove an item to the basket when the user clicks the remove button
// *************************************************************************
function removeItemFromBasket(itemId) {
  console.log("Attempting to remove item from basket with ID:", itemId); // Debugging: Log the item ID being removed

  // Prepare the AJAX request to remove the item from the server's basket
  fetch("/asda/remove_from_basket/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"), // Ensure CSRF token is included for Django
    },
    body: JSON.stringify({ item_id: itemId }),
  })
    .then((response) => {
      console.log("Server responded with status:", response.status); // Debugging: Log the response status
      if (!response.ok) {
        throw new Error("Network response was not ok.");
      }
      return response.text(); // Use text() to read the response body as text
    })
    .then((text) => {
      try {
        const data = JSON.parse(text); // Try to parse the text as JSON
        console.log("Received data from server:", data); // Debugging: Log the parsed data

        if (data.success) {
          // Proceed to update the local storage and UI only if server removal was successful
          let basket = JSON.parse(localStorage.getItem("basket") || "[]");
          console.log("Current basket before removal:", basket); // Debugging: Log the current basket before removal

          let newBasket = basket.filter((item) => item.itemId !== itemId);
          console.log("New basket after removal:", newBasket); // Debugging: Log the new basket after removal

          localStorage.setItem("basket", JSON.stringify(newBasket));

          recalculateTotalAfterRemoval(); // Recalculate and update the total price
          removeItemRowFromUI(itemId); // Remove the item's row from the UI

          console.log("Item removed successfully, page will be reloaded"); // Debugging: Indicate item removal and page reload
          window.location.reload(); // Refresh the page to reflect changes
        } else {
          console.error("Failed to remove item from basket:", data.error); // If data.error exists in the parsed data
        }
      } catch (err) {
        console.error("Error parsing JSON:", err);
        console.error("Received text:", text); // Log the raw text for debugging
      }
    })
    .catch((error) => {
      console.error("Error in fetch operation:", error);
    });
}

// *************************************************************************
// Helper function to get CSRF token
// *************************************************************************
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// *************************************************************************
// Removes item from UI
// *************************************************************************
function removeItemRowFromUI(itemId) {
  console.log(`Attempting to remove UI element for item with ID: ${itemId}`);
  const itemRow = document.getElementById(`item-row-${itemId}`);
  if (itemRow) {
    itemRow.parentNode.removeChild(itemRow);
    console.log(`Removed item with ID: ${itemId}`);
  } else {
    console.error(
      `Could not find the item row to remove for itemId: ${itemId}`
    );
  }
}

// *************************************************************************
// Clear local storage
// *************************************************************************
function emptyBasket() {
  localStorage.removeItem("basket"); // If using localStorage
  localStorage.removeItem("asdaTotalPrice");

  sessionStorage.removeItem("basket"); // If using sessionStorage
  sessionStorage.removeItem("asdaTotalPrice");
  // Update UI accordingly to reflect an empty basket
  updateUIForEmptyBasket();
}

// *************************************************************************
// Update UI For Empty Basket
// *************************************************************************
function updateUIForEmptyBasket() {
  // Clear local storage items related to the basket
  localStorage.removeItem("basket");
  localStorage.removeItem("asdaTotalPrice");

  // Update the UI to reflect an empty basket
  // For example, clear the basket display, reset the total price, etc.
  document.getElementById("asda-total").textContent = "£0.00";
  // Assuming you have a container for the basket items
  const basketContainer = document.getElementById("basket-container");
  if (basketContainer) {
    basketContainer.innerHTML = ""; // or however you want to indicate it's empty
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("empty-basket-form");
  if (form) {
    form.onsubmit = function (event) {
      // Prevent the form from submitting immediately
      event.preventDefault();

      // Call the function to update the UI for an empty basket
      updateUIForEmptyBasket();

      // Now submit the form programmatically
      form.submit();
    };
  }
});

// **********************************************************************
// Function to update the basket UI with a new item
// **********************************************************************
function updateBasketUI(store, name, price, itemId) {
  var basketTableBody = document
    .getElementById("asda-basket")
    ?.getElementsByTagName("tbody")[0];
  if (!basketTableBody) {
    console.error("Basket table body not found");
    return;
  }
  try {
    // Add a new row at the end of the basket table
    var newRow = basketTableBody.insertRow(-1);
    newRow.id = `item-row-${itemId}`;

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
    // Optional: Hide the "No items" row if it exists
    var noItemsRow = document.getElementById("no-items-row");
    if (noItemsRow) {
      noItemsRow.style.display = "none";
    }
  } catch (error) {
    console.error("Error updating basket UI:", error);
  }
}

// *************************************************************************
// Functions remove button setup
// *************************************************************************
function setupRemoveButton(buttonElement, itemId) {
  buttonElement.addEventListener("click", () => {
    removeItemFromLocalStorage(itemId);
  });
}

// *************************************************************************
// Returns a button element which, when clicked, will remove the specified item from the user's
// *************************************************************************
function createRemoveButton(itemId, store) {
  var button = document.createElement("button");
  button.className = "btn btn-danger btn-sm";
  button.textContent = "REMOVE";
  button.setAttribute("data-item-id", itemId);
  button.setAttribute("data-store", store);
  button.onclick = function () {
    // Pass the itemId directly to the removeItemFromBasket function
    removeItemFromBasket(itemId);
  };
  return button;
}

// *************************************************************************
// PriceSpan
// *************************************************************************
function createPriceSpan(className, price) {
  var span = document.createElement("span");
  span.className = className;
  span.textContent = price;
  return span;
}

// *************************************************************************
// Local Storage for basket to remember across pagination
// *************************************************************************
function loadBasketFromLocalStorage() {
  // Retrieve the basket data from local storage using the "basket" key; if not found, initialize an empty array
  var basket = JSON.parse(localStorage.getItem("basket") || "[]");

  // Get the table body element with id "asda-basket" where the basket items will be displayed
  var basketTableBody = document
    .getElementById("asda-basket")
    .getElementsByTagName("tbody")[0];

  // Clear the existing content of the basket table body to ensure a clean slate
  basketTableBody.innerHTML = "";

  // Iterate over each item in the basket array to display them in the UI
  basket.forEach(function (item) {
    // Insert a new row into the table for each item
    var row = basketTableBody.insertRow();

    // Create and insert a table cell for the item name using a helper function
    createTableCell(row, item.name);

    // Create and insert a table cell for the item price (formatted as £x.xx) using a helper function
    createTableCell(row, `£${item.price}`);

    // Create and insert a table cell for the remove button using a helper function, passing the item's itemId
    createRemoveButtonCell(row, item.itemId);
  });
}

// *************************************************************************
// Helper function to create and append a table cell with specified content to a given row
// *************************************************************************
function createTableCell(row, content) {
  // Create a new table cell (td element)
  var cell = row.insertCell();
  // Set the text content of the cell to the specified content
  cell.textContent = content;
}

// *************************************************************************
// Helper function to create and append a table cell containing a remove button for the specified itemId to a given row
// *************************************************************************
function createRemoveButtonCell(row, itemId) {
  // Create a new table cell (td element) to hold the remove button
  var removeButtonCell = row.insertCell();
  // Create a new button element for the remove button
  var removeButton = document.createElement("button");
  // Set the text content of the remove button to "Remove"
  removeButton.textContent = "Remove";
  // Add CSS classes to style the remove button
  removeButton.className = "btn btn-danger";
  // Set the onclick event handler for the remove button to call the removeItemFromBasket function with the item's itemId
  removeButton.onclick = function () {
    removeItemFromBasket(itemId);
  };
  // Append the remove button to the removeButtonCell in the current row
  removeButtonCell.appendChild(removeButton);
}

// *************************************************************************
// Function to update the total price for Asda
// *************************************************************************
function updateAsdaTotalPrice() {
  fetch("/interface/calculate_asda_total/", {
    method: "GET",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      if (data.total_price !== undefined) {
        document.getElementById(
          "asda-total"
        ).textContent = `£${data.total_price.toFixed(2)}`;
        // Store total price in local storage
        localStorage.setItem("asdaTotalPrice", data.total_price.toFixed(2));
      } else if (data.error) {
        console.error("Error calculating total:", data.error);
      }
    })
    .catch((error) => console.error("Error updating Asda total price:", error));
}

// *************************************************************************
// Function to load total price from session storage
// *************************************************************************
function loadTotalPriceFromStorage() {
  const basket = JSON.parse(sessionStorage.getItem("basket") || "[]");
  const totalPriceElement = document.getElementById("asda-total");

  if (basket.length === 0) {
    // If the basket is empty, hide the total price element and clear the total price from session storage
    totalPriceElement.textContent = "£0.00";
    sessionStorage.removeItem("asdaTotalPrice");
  } else {
    // If the basket is not empty, display the total price from session storage
    const totalPrice = sessionStorage.getItem("asdaTotalPrice");
    if (totalPrice !== null) {
      totalPriceElement.textContent = `£${totalPrice}`;
    }
  }
}

// *************************************************************************
// Call the updateAsdaTotalPrice function after any operation that adds or removes items
// *************************************************************************
function updateTotalAfterOperation() {
  // Recalculate total price after adding or removing items
  updateAsdaTotalPrice(); // Assuming this function correctly recalculates the total based on server response

  // Retrieve the basket from local storage
  const basket = JSON.parse(localStorage.getItem("basket") || "[]");

  // Check if the basket is empty to reset the total price accordingly
  if (basket.length === 0) {
    // If the basket is empty, set the total price to 0
    document.getElementById("asda-total").textContent = "£0.00";
    localStorage.setItem("asdaTotalPrice", "0.00");
  } else {
    // If basket is not empty, ensure the total price reflects the sum of items in the basket
    // This could involve fetching the updated total from the server or recalculating client-side
    // For simplicity, let's assume updateAsdaTotalPrice already updates the UI and storage accurately
  }
}

// Attach event listener to a stable parent element, for example, the basket table body
document.addEventListener("DOMContentLoaded", function () {
  const basketTableBody = document
    .getElementById("asda-basket")
    .getElementsByTagName("tbody")[0];

  basketTableBody.addEventListener("click", function (event) {
    // Check if the clicked element is a remove button
    if (event.target && event.target.className.includes("btn-remove-item")) {
      const itemId = event.target.getAttribute("data-item-id");
      if (itemId) {
        removeItemFromBasket(itemId);
      }
    }
  });

  // Ensure basket is correctly loaded and displayed
  loadBasketFromLocalStorage();
});

// *************************************************************************
// Call this function when the document is fully loaded
// *************************************************************************
document.addEventListener("DOMContentLoaded", loadBasketFromLocalStorage);

// *************************************************************************
// Call the loadTotalPriceFromStorage function when the document is fully loaded
// *************************************************************************
document.addEventListener("DOMContentLoaded", loadTotalPriceFromStorage);

document.addEventListener("DOMContentLoaded", function () {
  loadBasketFromLocalStorage();
});

document.addEventListener("DOMContentLoaded", function () {
  // Retrieve the total price from local storage
  let storedTotalPrice = localStorage.getItem("asdaTotalPrice");

  if (storedTotalPrice) {
    // Update the UI with the stored total price
    document.getElementById("asda-total").textContent = `£${storedTotalPrice}`;
  } else {
    // Default to £0.00 if no total price is found (e.g., the basket is empty)
    document.getElementById("asda-total").textContent = "£0.00";
  }
});
