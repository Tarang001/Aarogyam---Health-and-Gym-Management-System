 // Timer functionality
 let timerInterval;
 let isTimerRunning = false;
 let timeRemaining = 3600; // 1 hour in seconds

 function getDaysInCurrentMonth() {
    const now = new Date(); // Current date
    const year = now.getFullYear();
    const month = now.getMonth(); // Current month (0 for Jan, 11 for Dec)

    // Create a date for the first day of the next month, then go back one day
    const lastDayOfMonth = new Date(year, month + 1, 0);
    return lastDayOfMonth.getDate();
}

 function toggleTimer() {
     const timerBtn = document.getElementById('timer-btn');
     const timerDisplay = document.getElementById('workout-timer');

     if (!isTimerRunning) {
         // Start timer
         isTimerRunning = true;
         timerBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Timer';
         timerBtn.classList.add('btn-danger');
         timerBtn.classList.remove('btn-primary');
         timerDisplay.classList.add('timer-active');

         timerInterval = setInterval(() => {
             timeRemaining--;
             updateTimerDisplay();

             if (timeRemaining === 1800) {
                 markAttendance();
             }
         }, 1000);
     } else {
         stopTimer();
     }
 }

 function stopTimer() {
     isTimerRunning = false;
     clearInterval(timerInterval);
     const timerBtn = document.getElementById('timer-btn');
     const timerDisplay = document.getElementById('workout-timer');

     timerBtn.innerHTML = '<i class="fas fa-play"></i> Start Timer';
     timerBtn.classList.remove('btn-danger');
     timerBtn.classList.add('btn-primary');
     timerDisplay.classList.remove('timer-active');
 }

 function resetTimer() {
     stopTimer();
     timeRemaining = 3600;
     updateTimerDisplay();
 }

 function updateTimerDisplay() {
     const hours = Math.floor(timeRemaining / 3600);
     const minutes = Math.floor((timeRemaining % 3600) / 60);
     const seconds = timeRemaining % 60;

     document.getElementById('workout-timer').textContent =
         `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
 }

 // BMI Calculator
function calculateBMI() {
     weight = parseFloat(document.getElementById('weight').value);
     height = parseFloat(document.getElementById('height').value) / 100; // Convert cm to meters

     if (weight && height) {
         const bmi = weight / (height * height);
         const resultDiv = document.getElementById('bmi-result');

         let category;
         if (bmi < 18.5) category = 'Underweight';
         else if (bmi < 25) category = 'Normal weight';
         else if (bmi < 30) category = 'Overweight';
         else category = 'Obese';

         resultDiv.innerHTML = `
     <h4>Your BMI: ${bmi.toFixed(1)}</h4>
     <p>Category: ${category}</p>
 `;
     }
 }

 // Calorie Calculator
 function calculateCalories() {
     const weight = parseFloat(document.getElementById('weight').value);
     const height = parseFloat(document.getElementById('height').value);
     const age = parseFloat(document.getElementById('age').value);
     const activityLevel = parseFloat(document.getElementById('activity').value);

     if (weight && height && age && activityLevel) {
         // Using Harris-Benedict equation
         const bmr = 10 * weight + 6.25 * height - 5 * age + 5;
         const dailyCalories = bmr * activityLevel;
         const calories = Math.round(dailyCalories);
         const protein = weight*1.5;
         const carbs = weight*5.5;
         const fats = (0.27*calories)/4;
         
         document.getElementById('calorie-result').innerHTML = `
     <h4>Daily Calories: ${calories}calories</h4>
     <p>To maintain your current weight</p>
     <h5>Protein: ${Math.round(protein)}g </h5>
     <h5>Carbohydrates: ${Math.round(carbs)}g</h5>
     <h5>Fats: ${Math.round(fats)}g</h5>
     
 `;
     }
 }

 // Attendance Tracking
 async function initializeAttendanceGrid() {
     try{
     memberId = await getCurrentMemberId();
     const month_days = getDaysInCurrentMonth()
     const attendanceResponse = await fetch(`/user/profile/attendance?memberId=${memberId}`);
     const attendanceData = await attendanceResponse.json();
     const att_array = attendanceData.attendance_data;
     const grid = document.getElementById('attendance-grid');
     const today = new Date();

     for (let i = 1; i <= month_days; i++) {
         const cell = document.createElement('div');
         cell.className = 'attendance-cell';
         for(let j=0; j< att_array.length; j++){
            if(i == att_array[j]){
                cell.classList.add('present');
            }
         }      
         
         grid.appendChild(cell);
     }
    
     if(att_array.length<=1) {
        document.getElementById('largest_streak').textContent = `1 day streak`;
     }
     let current_seq = 1;
     let max_seq = 1;
     for(let i=0; i<att_array.length-1; i++)
     {
        if(parseInt(att_array[i])===parseInt(att_array[i+1])-1){current_seq++; max_seq = Math.max(max_seq,current_seq);}
        else{current_seq=1;}
     }
     document.getElementById('largest_streak').innerHTML = `<div id="largest_streak" class="achievement-badge">
                <i class="fas fa-fire"></i> ${max_seq} Day Streak
              </div>`;
    }
    catch{}
 }
 function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // Add to document
    document.body.appendChild(notification);

    // Remove the notification after 6 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300); // Wait for fade out animation to complete
    }, 6000);
}

async function markAttendance() {
    try{
    const response = await fetch('/user/markAttendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            timestamp: new Date().toISOString()
        })
    });

    if (!response.ok) {
        throw new Error('Failed to track click');
    }
    showNotification("Your Attendance has been marked!", 'success');
}
    catch (error) {
        showNotification("Issue while marking attendance!",'error')
    }     
 }



 // Image Preview
 function previewImage(event) {
    const preview = document.getElementById('daily-pic-preview');
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
        }
        reader.readAsDataURL(file);
    }
}

//  // Set workout day
//  function setWorkoutDay() {
//      const days = ['Rest Day', 'Chest & Triceps', 'Back & Biceps', 'Legs', 'Shoulders & Arms', 'Full Body', 'Cardio'];
//      const today = new Date().getDay();
//      document.getElementById('workout-day').textContent = days[today];
//  }

 // today's workout wala part ka code hai
 // Get workout day and exercises from database
async function fetchWorkoutData() {
try {
 const memberId = await getCurrentMemberId(); // Function to get logged-in member's ID
 console.log(memberId)
 const today = new Date().getDay();
 
 // Fetch workout day from routine table
 const response = await fetch(`/user/profile/workout-day?memberId=${memberId}&weekDay=${today}`);
 const workoutData = await response.json();
 
 // Update workout day display
 document.getElementById('workout-day').textContent = workoutData.gymDayName;
 
 // Fetch member's joining date to calculate experience level
 const memberResponse = await fetch(`/user/profile/member-info?memberId=${memberId}`);
 const memberData = await memberResponse.json();
 
 const joinDate = new Date(memberData.joinDate);
 const daysSinceJoining = Math.floor((new Date() - joinDate) / (1000 * 60 * 60 * 24));
 
 // Determine exercise difficulty distribution based on experience
 let difficultyDistribution;
 if (daysSinceJoining < 15) {
     difficultyDistribution = {
         beginner: 4,
         intermediate: 1,
         advanced: 0
     };
 } else if (daysSinceJoining < 30) {
     difficultyDistribution = {
         beginner: 3,
         intermediate: 2,
         advanced: 0
     };
 } else {
     difficultyDistribution = {
         beginner: 2,
         intermediate: 2,
         advanced: 1
     };
 }
 
 // Fetch exercises based on workout day and difficulty distribution
 if (workoutData.gymDayName === 'Rest Day')
 {
    const containe = document.getElementsByClassName('exercises-list mb-4')
    containe.innerHTML=`<h3>It's your REST DAY</h3>
    <h6>Gives your muscle rest and keep hydrated!</h6>`
 }
 else{
 target_muscle = workoutData.gymDayName.split(" ")[0]
 const exercisesResponse = await fetch(`/user/profile/exercises?target_muscle=${target_muscle}`)
 
 const exercises = await exercisesResponse.json();
 console.log(exercises)
 displayExercises(exercises);
}
 
} catch (error) {
 console.error('Error fetching workout data:', error);
 document.getElementById('workout-day').textContent = 'Error loading workout';
}
}

//Function for getting the current memberId
async function getCurrentMemberId() {
try {
 const response = await fetch('/member_id');
 if (!response.ok) {
     throw new Error(`HTTP error! status: ${response.status}`);
 }
 const data = await response.json();
 return data.member_id; // Returns the member_id as a string
} catch (error) {
 console.error('Error fetching member_id:', error);
 return ''; // Return empty string in case of error
}
}


// Display exercises in the UI
function displayExercises(exercises) {
const container = document.getElementById('exercises-container');
container.innerHTML = '';

exercises.forEach((exercise, index) => {
 const exerciseElement = document.createElement('div');
 exerciseElement.className = 'list-group-item';
 exerciseElement.innerHTML = `
     <div class="d-flex justify-content-between align-items-center">
         <div>
             <h6 class="mb-1">${index + 1}. ${exercise[0]}</h6>
             <p class="mb-1 small text-muted">${exercise[1]}</p>
         </div>
         <span class="badge ${getDifficultyBadgeClass(exercise[2])}">
             ${exercise[2]}
         </span>
     </div>
     ${exercise[3] ? `
     <div class="mt-2">
         <a href="https://www.youtube.com/watch?v=${exercise[3]}" target="_blank" class="btn btn-sm btn-outline-primary">
             <i class="fas fa-video" ></i> Watch Tutorial
         </a>
     </div>
     ` : ''}
 `;
 container.appendChild(exerciseElement);
});
}

// Helper function to get badge class based on difficulty level
function getDifficultyBadgeClass(difficulty) {
switch(difficulty.toLowerCase()) {
 case 'beginner':
     return 'bg-success';
 case 'intermediate':
     return 'bg-warning';
 case 'advanced':
     return 'bg-danger';
 default:
     return 'bg-secondary';
}
}
// Uploading pics of daily progress usi ka implementation hai
function uploadProgressPic(event) {
    event.preventDefault();
    
    const fileInput = document.querySelector('input[type="file"]');
    const descriptionInput = document.querySelector('input[name="description"]');
    
    if (!fileInput.files[0]) {
        showNotification('Please select an image to upload', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('description', descriptionInput.value);
    
    fetch('/user/upload_prog_pics', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Progress picture uploaded successfully', 'success');
            loadLatestProgressPic();
        } else {
            showNotification(data.error || 'Upload failed', 'error');
        }
    })
    .catch(error => {
        showNotification('Error uploading image', 'error');
        console.error('Error:', error);
    });
}

function loadLatestProgressPic() {
    fetch('/user/get_prog_pics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const preview = document.getElementById('daily-pic-preview');
                preview.src = `/static/progress_pics/${data.image_path}`;
                
                // Update description if you have an element for it
                const descriptionElement = document.querySelector('input[name="description"]');
                if (descriptionElement) {
                    descriptionElement.value = data.description || '';
                }
            }
        })
        .catch(error => {
            console.error('Error loading progress picture:', error);
            // Set default image if no progress pics are found
            const preview = document.getElementById('daily-pic-preview');
            preview.src = "/api/placeholder/400/250";
        });
}


// Add to the existing DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', function () {
initializeAttendanceGrid();
updateTimerDisplay();
fetchWorkoutData();
loadLatestProgressPic();
const uploadForm = document.querySelector('.card-body form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', uploadProgressPic);
    }
});

// Modal functions
function openModal() {
    document.getElementById('routine-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('routine-modal').style.display = 'none';
    document.getElementById('itemForm').reset();
    currentItemId = null;
    document.getElementById('modalTitle').textContent = 'Update Your Schedule';
}

function openAddModal() {
    currentItemId = null;
    document.getElementById('modalTitle').textContent = 'Update Your Schedule';
    document.getElementById('itemForm').reset();
    openModal();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('itemModal');
    if (event.target === modal) {
        closeModal();
    }
}

function openEditProfileModal() {
    // Open the modal when the Edit Profile button is clicked
    const editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    editProfileModal.show();
}

// Optionally, handle form submission
document.getElementById('editProfileForm').addEventListener('submit', function(e) {
    e.preventDefault();
    // Handle the form submission here (AJAX request or other logic)
    alert('Profile updated successfully!');
});

document.getElementById('editProfileForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Collect form data
    const name = document.getElementById('editName').value;
    const dob = document.getElementById('editDob').value;
    const disease = document.getElementById('editDisease').value;

    try {
        // Send AJAX request to update profile
        const response = await fetch('/user/edit_profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                dob: dob,
                disease: disease
            })
        });

        const result = await response.json();

        if (result.success) {
            // Update profile details in the UI
            document.querySelector('.display-4').textContent = name;
            document.querySelector('.fa-cake-candles').nextSibling.textContent = ` DOB: ${dob}`;
            document.querySelector('.fa-disease').nextSibling.textContent = ` Any major disease: ${disease}`;

            // Close the modal
            const editProfileModal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
            editProfileModal.hide();

            // Show success notification
            showNotification('Profile updated successfully!', 'success');
        } else {
            // Show error notification
            showNotification(result.error || 'Failed to update profile', 'error');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        showNotification('An error occurred while updating profile', 'error');
    }
});