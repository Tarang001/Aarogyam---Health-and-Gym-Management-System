// Store all exercises data received from backend
let allExercises = [];
let currentBatch = 1;
const ITEMS_PER_BATCH = 6;
let showingAll = false;

// Define body part categories
const bodyPartCategories = [
    'Chest', 'Shoulders', 'Triceps', 'Back', 
    'Biceps', 'Legs', 'Core'
];

function initializeExercises(exercises) {
    allExercises = exercises;
    displayExercises(0, ITEMS_PER_BATCH);
    initializeFilters();
}

function createExerciseHTML(exercise) {
    return `
        <div class="exercise-box" data-difficulty="${exercise[4]}" data-bodypart="${exercise[6]}">
            <div class="loading-overlay">
                <div class="spinner"></div>
            </div>
            <div class="body-part-visual">
                ${createBodyPartVisual(exercise[6])}
            </div>
            <iframe 
                src="https://www.youtube.com/embed/${exercise[5].video_id}" 
                frameborder="0" 
                allowfullscreen
                onload="this.parentElement.querySelector('.loading-overlay').style.display='none'">
            </iframe>
            <h3><strong>Exercise Name: </strong>${exercise[1]}</h3>
            <p><strong>Difficulty Level:</strong> ${exercise[4]}</p>
            <p><strong>Target Area:</strong> ${exercise[6]}</p>
            <p><strong>Description:</strong>${exercise[2]}</p>
        </div>
    `;
}

function createBodyPartVisual(bodyPart) {
    // SVG body map with highlighted target areas
    return `
        <svg viewBox="0 0 100 160" class="body-map">
            <!-- Head -->
            <circle cx="50" cy="20" r="15" class="${bodyPart.includes('Shoulders') ? 'highlighted' : ''}"/>
            <!-- Torso -->
            <rect x="35" y="35" width="30" height="45" 
                class="${bodyPart.includes('Chest') || bodyPart.includes('Core') ? 'highlighted' : ''}"/>
            <!-- Arms -->
            <rect x="20" y="35" width="15" height="40" 
                class="${bodyPart.includes('Biceps') || bodyPart.includes('Triceps') ? 'highlighted' : ''}"/>
            <rect x="65" y="35" width="15" height="40"
                class="${bodyPart.includes('Biceps') || bodyPart.includes('Triceps') ? 'highlighted' : ''}"/>
            <!-- Back area -->
            <rect x="35" y="35" width="30" height="45" 
                class="${bodyPart.includes('Back') ? 'highlighted back-overlay' : 'back-overlay'}"/>
            <!-- Legs -->
            <rect x="35" y="80" width="15" height="50" 
                class="${bodyPart.includes('Legs') ? 'highlighted' : ''}"/>
            <rect x="50" y="80" width="15" height="50"
                class="${bodyPart.includes('Legs') ? 'highlighted' : ''}"/>
        </svg>
    `;
}

function displayExercises(startIndex, endIndex, animate = true) {
    const container = document.querySelector('.exercise-container');
    
    if (animate) {
        container.classList.add('loading');
    }
    
    const exercisesToShow = allExercises.slice(startIndex, endIndex);
    const exercisesHTML = exercisesToShow.map(exercise => createExerciseHTML(exercise)).join('');
    
    setTimeout(() => {
        container.innerHTML = exercisesHTML;
        if (animate) {
            container.classList.remove('loading');
        }
        
        updateButtonsVisibility(endIndex);
        
        if (startIndex > 0 && animate) {
            const lastVisible = container.children[container.children.length - ITEMS_PER_BATCH];
            if (lastVisible) {
                lastVisible.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }, animate ? 300 : 0);
}

function initializeFilters() {
    const difficulties = [...new Set(allExercises.map(exercise => exercise[4]))];
    const filterContainer = document.createElement('div');
    filterContainer.className = 'filter-container';
    
    filterContainer.innerHTML = `
        <div class="filter-group">
            <label>Sort by:</label>
            <select id="sort-select">
                <option value="name">Name</option>
                <option value="difficulty">Difficulty</option>
            </select>
        </div>
        <div class="filter-group">
            <label>Difficulty:</label>
            <select id="difficulty-select">
                <option value="all">All Difficulties</option>
                ${difficulties.map(diff => `<option value="${diff}">${diff}</option>`).join('')}
            </select>
        </div>
        <div class="filter-group">
            <label>Target Area:</label>
            <select id="bodypart-select">
                <option value="all">All Areas</option>
                ${bodyPartCategories.map(part => `<option value="${part}">${part}</option>`).join('')}
            </select>
        </div>
        <button id="clear-filters" class="clear-filters-btn">Clear All Filters</button>
    `;
    
    document.querySelector('.main-heading').after(filterContainer);
    
    // Add event listeners
    document.getElementById('sort-select').addEventListener('change', handleSort);
    document.getElementById('difficulty-select').addEventListener('change', handleFilters);
    document.getElementById('bodypart-select').addEventListener('change', handleFilters);
    document.getElementById('clear-filters').addEventListener('click', clearFilters);
}

function handleSort() {
    const sortBy = document.getElementById('sort-select').value;
    const tempExercises = [...allExercises];
    
    tempExercises.sort((a, b) => {
        if (sortBy === 'name') {
            return a[1].localeCompare(b[1]);
        } else {
            return a[4].localeCompare(b[4]);
        }
    });
    
    allExercises = tempExercises;
    currentBatch = 1;
    displayExercises(0, ITEMS_PER_BATCH);
}

function handleFilters() {
    const difficulty = document.getElementById('difficulty-select').value;
    const bodyPart = document.getElementById('bodypart-select').value;
    
    const originalExercises = JSON.parse(document.getElementById('exercises-data').textContent);
    
    let filteredExercises = originalExercises;
    
    // Apply difficulty filter
    if (difficulty !== 'all') {
        filteredExercises = filteredExercises.filter(exercise => exercise[4] === difficulty);
    }
    
    // Apply body part filter
    if (bodyPart !== 'all') {
        filteredExercises = filteredExercises.filter(exercise => 
            exercise[6].includes(bodyPart)
        );
    }
    
    allExercises = filteredExercises;
    currentBatch = 1;
    displayExercises(0, ITEMS_PER_BATCH);
    
    updateResultsCount(filteredExercises.length);
}

function clearFilters() {
    // Reset all filter selections
    document.getElementById('sort-select').value = 'name';
    document.getElementById('difficulty-select').value = 'all';
    document.getElementById('bodypart-select').value = 'all';
    
    // Reset exercises to original state
    const originalExercises = JSON.parse(document.getElementById('exercises-data').textContent);
    allExercises = originalExercises;
    currentBatch = 1;
    displayExercises(0, ITEMS_PER_BATCH);
    
    // Update results count
    updateResultsCount(originalExercises.length);
}

function updateResultsCount(count) {
    let resultsCounter = document.getElementById('results-counter');
    if (!resultsCounter) {
        resultsCounter = document.createElement('div');
        resultsCounter.id = 'results-counter';
        document.querySelector('.filter-container').after(resultsCounter);
    }
    resultsCounter.textContent = `Showing ${Math.min(count, ITEMS_PER_BATCH)} of ${count} exercises`;
}

// Event listeners
document.getElementById('view-more-btn').addEventListener('click', () => {
    currentBatch++;
    displayExercises(0, currentBatch * ITEMS_PER_BATCH);
});

document.getElementById('show-less-btn').addEventListener('click', () => {
    currentBatch = 1;
    displayExercises(0, ITEMS_PER_BATCH);
});

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const exercisesData = JSON.parse(document.getElementById('exercises-data').textContent);
    initializeExercises(exercisesData);
});