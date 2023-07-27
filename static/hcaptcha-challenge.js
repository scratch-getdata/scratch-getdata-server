// Replace 'YOUR-SITE-KEY' with your actual hCaptcha site key
var siteKey = '566a29ce-8845-45f9-9982-246d8a4d9670';


// Function to handle form submission
function handleSubmit(event) {
  event.preventDefault();

  // Get the hCaptcha response token
  var responseToken = document.getElementById('h-captcha-response').value;

  // Verify hCaptcha on the client-side
  fetch('https://hcaptcha.com/siteverify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'response=' + responseToken + '&secret=YOUR-SECRET'
  })
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      // Check the verification response
      if (data.success) {
        // Display the content section if hCaptcha is verified
        document.getElementById('content').style.display = 'block';
        document.getElementById('hcaptcha-error').style.display = 'none';
      } else {
        // Show error message if hCaptcha verification fails
        document.getElementById('content').style.display = 'none';
        document.getElementById('hcaptcha-error').style.display = 'block';
      }
    })
    .catch(function(error) {
      console.log('Error:', error);
      // Show error message if an error occurs during verification
      document.getElementById('content').style.display = 'none';
      document.getElementById('hcaptcha-error').style.display = 'block';
    });
}

// Execute the following code when the document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Attach form submission event listener
  var form = document.getElementById('hcaptcha-form');
  form.addEventListener('submit', handleSubmit);

  // Load hCaptcha widget
  hcaptcha.render('hcaptcha-form', {
    sitekey: siteKey,
    callback: handleSubmit
  });
});
