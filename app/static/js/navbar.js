// Navbar JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Search Bar Functionality
    const searchInput = document.querySelector('.navbar input[type="text"]');
    
    if (searchInput) {
        // Focus on search with Cmd/Ctrl + K
        document.addEventListener('keydown', function(e) {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }
            
            // Escape to blur
            if (e.key === 'Escape' && document.activeElement === searchInput) {
                searchInput.blur();
            }
        });
        
        // Search functionality (placeholder - can be enhanced)
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            
            if (searchTerm.length >= 3) {
                // TODO: Implement actual search functionality
                console.log('Searching for:', searchTerm);
                
                // You can add AJAX search here
                // Example:
                // fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`)
                //     .then(response => response.json())
                //     .then(data => {
                //         // Display search results
                //     });
            }
        });
    }
    
    // Mobile Search Toggle
    const mobileSearchBtn = document.querySelector('.navbar .lg\\:hidden .fa-search');
    
    if (mobileSearchBtn) {
        mobileSearchBtn.closest('button').addEventListener('click', function() {
            // TODO: Implement mobile search modal/dropdown
            console.log('Mobile search clicked');
        });
    }
    
    // Notification Bell Animation
    const notificationBtn = document.querySelector('.navbar .fa-bell');
    
    if (notificationBtn) {
        notificationBtn.closest('button').addEventListener('click', function() {
            // TODO: Implement notification dropdown
            console.log('Notifications clicked');
            
            // Remove notification badge on click (example)
            const badge = this.querySelector('.bg-red-500');
            if (badge) {
                badge.style.display = 'none';
            }
        });
    }
    
    // Enhanced Dropdown Animations
    const dropdownToggle = document.getElementById('navbarDropdown');
    const dropdownMenu = document.querySelector('.navbar-dropdown');
    
    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', function() {
            // Add animation class
            setTimeout(() => {
                if (dropdownMenu.classList.contains('show')) {
                    dropdownMenu.style.animation = 'dropdownFadeIn 0.2s ease-out';
                }
            }, 10);
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.previousElementSibling;
            if (!dropdown.contains(event.target) && !toggle.contains(event.target)) {
                const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
                if (bsDropdown) {
                    bsDropdown.hide();
                }
            }
        });
    });
    
    // Avatar Initial Generation (if needed for dynamic users)
    function generateAvatarColor(name) {
        // Generate consistent color based on name
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        
        const hue = hash % 360;
        return `linear-gradient(135deg, hsl(${hue}, 70%, 50%), hsl(${hue + 30}, 70%, 40%))`;
    }
    
    // Add smooth hover effect to dropdown items
    const dropdownItems = document.querySelectorAll('.navbar-dropdown-item');
    
    dropdownItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(4px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
    
    // Accessibility: Keyboard navigation for dropdown
    if (dropdownToggle) {
        dropdownToggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    }
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.navbar button');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Notification count update (example function)
    function updateNotificationCount(count) {
        const badge = document.querySelector('.navbar .bg-gradient-to-br.from-red-500');
        if (badge && count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
        } else if (badge) {
            badge.style.display = 'none';
        }
    }
    
    // Example: Fetch notifications on load
    // updateNotificationCount(3);
    
    // Add loading state to search
    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            const searchIcon = this.previousElementSibling;
            searchIcon.classList.remove('fa-search');
            searchIcon.classList.add('fa-spinner', 'fa-spin');
            
            searchTimeout = setTimeout(() => {
                searchIcon.classList.remove('fa-spinner', 'fa-spin');
                searchIcon.classList.add('fa-search');
            }, 500);
        });
    }
});

// Ripple CSS (injected dynamically)
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

