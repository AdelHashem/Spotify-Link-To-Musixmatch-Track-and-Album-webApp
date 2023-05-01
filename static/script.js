// Get the form and button elements
const form = document.querySelector('form');
const button = document.querySelector('#process_button');

// Add event listener for form submit
form.addEventListener('submit', async (event) => {
  // Prevent the form's default action
  event.preventDefault();

  // Disable the button to prevent multiple submissions
  button.setAttribute('disabled', true);

  // Show the loading spinner
  const loadingSpinner = document.querySelector('#loading');
  loadingSpinner.style.display = 'block';

  // Get the input value
  const inputLink = document.querySelector('#input_link').value;

  // Make sure the input is not empty and is a valid Spotify link or ISRC
  if (!inputLink.trim()) {
    //alert('Please enter a valid Spotify link or ISRC.');
    // Hide the loading spinner and enable the button
    loadingSpinner.style.display = 'none';
    button.removeAttribute('disabled');
    return;
  }

  // Redirect to the same URL with the input value as a query parameter
  window.location.href = window.location.href.split('?')[0] + '?link=' + encodeURIComponent(inputLink);
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
document.querySelector('.note').style.display = currentUrl.includes('?') ? 'none' : 'block';

// Get the close button element
var closeButton = document.getElementById("closenote");

// Get the note element
var note = document.querySelector(".note");

// If the close button and note elements exist
if (closeButton && note) {
  // Add an event listener to the close button
  closeButton.addEventListener("click", function() {
    // Hide the note element
    note.style.display = "none";
  });
}