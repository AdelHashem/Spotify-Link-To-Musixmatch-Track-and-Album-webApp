// Get the form and button elements
const form = document.querySelector("form");
const button = document.querySelector("#process_button");

// Add event listener for form submit
form.addEventListener("submit", (event) => {
  event.preventDefault();

  button.disabled = true;

  const loadingSpinner = document.querySelector("#loading");
  loadingSpinner.style.display = "block";

  const inputLink = document.querySelector("#input_link").value.trim();

  if (!inputLink) {
    loadingSpinner.style.display = "none";
    button.disabled = false;
    return Promise.resolve(); // Resolve with a void value
  }

  if (window.location.pathname === "/abstrack") { 
    window.location.href =
    window.location.href.split("?")[0] +
    "?id=" +
    encodeURIComponent(inputLink);
  }else{
    window.location.href =
    window.location.href.split("?")[0] +
    "?link=" +
    encodeURIComponent(inputLink);
  }
  
});

// Get the how-to-use link and modal elements
const howToUseLink = document.querySelector("#how_to_use");
const modal = document.querySelector(".modal");
const closeBtn = document.querySelector(".close");

// Add click event listener for the how-to-use link
howToUseLink.addEventListener("click", (event) => {
  event.preventDefault();
  modal.style.display = "block";
});

// Add click event listener for the close button in the modal
closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

// Add click event listener for clicks outside the modal
window.addEventListener("click", (event) => {
  if (event.target === modal) {
    modal.style.display = "none";
  }
});

// Get the close button element and note element
const closeButton = document.getElementById("closenote");
const note = document.querySelector(".note");

// If the close button and note elements exist
if (closeButton && note) {
  // Add an event listener to the close button
  closeButton.addEventListener("click", () => {
    // Hide the note element
    note.style.display = "none";
  });
}

window.addEventListener("load", () => {
  const offlineDiv = document.getElementById("offline-div");

  function handleOnlineStatus() {
    const elements = document.querySelectorAll(
      "body > *:not(head):not(script):not(meta)"
    );
    if (navigator.onLine) {
      for (const element of elements) {
        element.style.removeProperty("display");
      }
      offlineDiv.style.display = "none";
    } else {
      for (const element of elements) {
        element.style.display = "none";
      }
      offlineDiv.style.display = "block";
    }
  }

  handleOnlineStatus(); // Initial check

  // Listen for online/offline events
  window.addEventListener("online", () => {
    location.reload();
  });
  window.addEventListener("offline", handleOnlineStatus);
});

// Hide the note element if the current URL contains a query string
document.querySelector(".note").style.display = window.location.href.includes(
  "?"
)
  ? "none"
  : "block";
