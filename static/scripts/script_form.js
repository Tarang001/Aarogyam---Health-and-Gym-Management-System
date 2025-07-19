// Form validation: check if passwords match
function validateForm() {
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm_password').value;

  if (password !== confirmPassword) {
      alert('Passwords do not match. Please try again.');
      return false;
  }

  return true; // Submit form if everything is valid
}

// FORMS THING CREATION
 // Get the logout button element
 const logoutBtn = document.getElementById('logout-btn');

 // Add a click event listener to the logout button
 logoutBtn.addEventListener('click', function(event) {
     event.preventDefault();  // Prevent the default link behavior

     // Display the confirmation alert box
     const isConfirmed = confirm("Are you sure you want to logout?");

     // If the user confirms, redirect to the logout route
     if (isConfirmed) {
         window.location.href = "/logout";
     }
     // Otherwise, the user stays on the same page
 });


 