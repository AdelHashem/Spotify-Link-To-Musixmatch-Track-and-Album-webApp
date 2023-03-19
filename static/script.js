
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

  // Submit the form
  form.submit();
});
