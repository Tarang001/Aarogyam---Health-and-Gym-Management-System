// Initialize AOS animation library
AOS.init({
  duration: 1000,
  once: true
});

// Handle Read More functionality
document.querySelectorAll('.read-more').forEach(button => {
  button.addEventListener('click', function() {
      const previewText = this.parentElement.querySelector('.preview-text');
      const fullText = this.parentElement.querySelector('.full-text');
      
      previewText.classList.toggle('hidden');
      fullText.classList.toggle('hidden');
      
      this.textContent = fullText.classList.contains('hidden') ? 'Read More' : 'Read Less';
  });
});

// Handle mobile navigation
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('active');
  hamburger.classList.toggle('active');
});

// Load and display videos
let allVideos = [];
let showingAllVideos = false;

async function loadVideos() {
  try {
      const response = await fetch('/api/videos');
      const videos = await response.json();
      allVideos = videos;
      displayVideos(videos);
  } catch (error) {
      console.error('Error loading videos:', error);
  }
}

function displayVideos(videos) {
  const container = document.getElementById('videoContainer');
  container.innerHTML = '';
  
  videos.forEach(video => {
      const videoCard = document.createElement('div');
      videoCard.className = 'video-card';
      videoCard.setAttribute('data-aos', 'fade-up');
      
      videoCard.innerHTML = `
          <div class="video-thumbnail">
              <img src="${video.thumbnail}" alt="${video.title}">
          </div>
          <div class="video-info">
              <h3>${video.title}</h3>
          </div>
      `;
      
      videoCard.addEventListener('click', () => {
          // Handle video playback or redirect to YouTube
          window.open(video.url, '_blank');
      });
      
      container.appendChild(videoCard);
  });
}

// Handle View All button
document.getElementById('viewAllBtn').addEventListener('click', async function() {
  if (!showingAllVideos) {
      try {
          const response = await fetch('/api/all-videos');
          const allVideos = await response.json();
          displayVideos(allVideos);
          this.textContent = 'Show Less';
          showingAllVideos = true;
      } catch (error) {
          console.error('Error loading all videos:', error);
      }
  } else {
      displayVideos(allVideos.slice(0, 8));
      this.textContent = 'View All Tutorials';
      showingAllVideos = false;
  }
});

// Load initial videos
loadVideos();

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
          behavior: 'smooth'
      });
  });
});