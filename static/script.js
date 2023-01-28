// Add event listener for button click
button.addEventListener('click', async (event) => {
  // Prevent the button's default action
  event.preventDefault();

  // Disable the button to prevent multiple submissions
  button.setAttribute('disabled', true);

  // Show the loading spinner
  loadingSpinner.style.display = 'block';

  // Get the input value
  const inputLink = document.querySelector('#input_link').value;

  // Make sure the input is a valid Spotify link
  if (!inputLink.includes('spotify')) {
      alert('Please enter a valid Spotify link.');
      return;
  }

  // Send a POST request to the server
  const response = await fetch('/', {
      method: 'POST',
      body: JSON.stringify({link: inputLink}),
      headers: {
          'Content-Type': 'application/json'
      }
  });

  // Get the JSON data from the response
  const data = await response.json();

  // Update the output elements with the returned data
  outputId.innerHTML = `Musixmatch Track ID: ${data.id}`;
  outputTrackLink.innerHTML = `Musixmatch Track Link: ${data.track_link}`;
  outputAlbumLink.innerHTML = `Musixmatch Album Link: ${data.album_link}`;

  // Hide the loading spinner
  loadingSpinner.style.display = 'none';

  // Enable the button
  button.removeAttribute('disabled');
});
