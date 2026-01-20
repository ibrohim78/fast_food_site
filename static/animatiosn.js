// Animatsiyalar JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Scroll animatsiyalari
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-up');
                entry.target.style.opacity = '1';
            }
        });
    }, {
        threshold: 0.1
    });
    
    // Elementlarni animatsiya qilish
    document.querySelectorAll('.menu-item, .animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
    
    // Parallax effekti
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
});