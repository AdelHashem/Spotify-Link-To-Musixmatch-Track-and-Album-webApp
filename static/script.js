// Get the form and button elements
const form = document.querySelector('form');
const button = document.querySelector('#process_button');

// Add event listener for form submit
form.addEventListener('submit', (event) => {
  event.preventDefault();

  button.setAttribute('disabled', true);

  const loadingSpinner = document.querySelector('#loading');
  loadingSpinner.style.display = 'block';

  const inputLink = document.querySelector('#input_link').value;

  if (!inputLink.trim()) {
    loadingSpinner.style.display = 'none';
    button.removeAttribute('disabled');
    return Promise.resolve(); // Resolve with a void value
  }

  window.location.href =
    window.location.href.split('?')[0] +
    '?link=' +
    encodeURIComponent(inputLink);
});
// Get the how-to-use link and modal elements
const howToUseLink = document.querySelector('#how_to_use');
const modal = document.querySelector('.modal');
const closeBtn = document.querySelector('.close');

// Add click event listener for the how-to-use link
howToUseLink.addEventListener('click', (event) => {
  event.preventDefault();
  modal.style.display = 'block';
});

// Add click event listener for the close button in the modal
closeBtn.addEventListener('click', () => {
  modal.style.display = 'none';
});

// Add click event listener for clicks outside the modal
window.addEventListener('click', (event) => {
  if (event.target == modal) {
    modal.style.display = 'none';
  }
});

const currentUrl = window.location.href;
document.querySelector('.note').style.display = currentUrl.includes('?')
  ? 'none'
  : 'block';

// Get the close button element
let closeButton = document.getElementById('closenote');

// Get the note element
let note = document.querySelector('.note');

// If the close button and note elements exist
if (closeButton && note) {
  // Add an event listener to the close button
  closeButton.addEventListener('click', function () {
    // Hide the note element
    note.style.display = 'none';
  });
}
window.addEventListener('load', function () {
  let offlineDiv = document.getElementById('offline-div');

  function handleOnlineStatus() {
    let elements = document.querySelectorAll(
      'body > *:not(head):not(script):not(meta)'
    );
    if (navigator.onLine) {
      for (let element of elements) {
        element.style.removeProperty('display');
      }
      offlineDiv.style.display = 'none';
    } else {
      for (let element of elements) {
        element.style.display = 'none';
      }
      offlineDiv.style.display = 'block';
    }
  }

  handleOnlineStatus(); // Initial check

  // Listen for online/offline events
  window.addEventListener('online', function () {
    location.reload();
  });
  window.addEventListener('offline', handleOnlineStatus);
});
