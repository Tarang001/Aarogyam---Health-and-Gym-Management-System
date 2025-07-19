AOS.init({
  duration: 1000,
  once: true
});

// Handle Read More functionality
document.querySelectorAll('.read-more-btn').forEach(button => {
  button.addEventListener('click', function() {
      const container = this.closest('.read-more-container');
      const hiddenContent = container.querySelector('.hidden-content');
      const transformationImages = hiddenContent.querySelector('.transformation-images');
      const isHidden = hiddenContent.style.display === 'none' || hiddenContent.style.display === '';
      
      if (isHidden) {
          hiddenContent.style.display = 'block';
          setTimeout(() => {
              hiddenContent.classList.add('visible');
              transformationImages.classList.add('visible');
          }, 50);
          this.textContent = 'Read Less';
      } else {
          hiddenContent.classList.remove('visible');
          transformationImages.classList.remove('visible');
          setTimeout(() => {
              hiddenContent.style.display = 'none';
          }, 300);
          this.textContent = 'Read More';
      }
      
      if (isHidden) {
          setTimeout(() => {
              container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }, 100);
      }
  });
});