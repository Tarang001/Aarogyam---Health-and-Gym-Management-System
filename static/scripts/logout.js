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