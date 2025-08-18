/**
 * Breadcrumb Navigation Enhancement
 * Provides interactive features for the breadcrumb navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects and smooth transitions
    const breadcrumbLinks = document.querySelectorAll('.breadcrumb-nav .breadcrumb-item a');
    
    breadcrumbLinks.forEach(link => {
        // Add tooltip for long breadcrumb items
        if (link.textContent.length > 20) {
            link.title = link.textContent;
        }
        
        // Add click tracking for analytics (optional)
        link.addEventListener('click', function(e) {
            // You can add analytics tracking here
            console.log('Breadcrumb navigation:', this.textContent.trim());
        });
    });
    
    // Add responsive behavior for mobile
    const breadcrumbNav = document.querySelector('.breadcrumb-nav');
    if (breadcrumbNav) {
        // On mobile, show only the last 2 breadcrumb items
        function handleResize() {
            const breadcrumbItems = breadcrumbNav.querySelectorAll('.breadcrumb-item');
            if (window.innerWidth < 768 && breadcrumbItems.length > 3) {
                breadcrumbItems.forEach((item, index) => {
                    if (index < breadcrumbItems.length - 2) {
                        item.style.display = 'none';
                    } else {
                        item.style.display = 'inline-block';
                    }
                });
                
                // Add ellipsis for hidden items
                const firstVisibleItem = breadcrumbNav.querySelector('.breadcrumb-item[style*="inline-block"]');
                if (firstVisibleItem && !breadcrumbNav.querySelector('.breadcrumb-ellipsis')) {
                    const ellipsis = document.createElement('li');
                    ellipsis.className = 'breadcrumb-item breadcrumb-ellipsis';
                    ellipsis.innerHTML = '<i class="fas fa-ellipsis-h"></i>';
                    breadcrumbNav.querySelector('.breadcrumb').insertBefore(ellipsis, firstVisibleItem);
                }
            } else {
                breadcrumbItems.forEach(item => {
                    item.style.display = 'inline-block';
                });
                
                // Remove ellipsis
                const ellipsis = breadcrumbNav.querySelector('.breadcrumb-ellipsis');
                if (ellipsis) {
                    ellipsis.remove();
                }
            }
        }
        
        // Handle initial load and resize
        handleResize();
        window.addEventListener('resize', handleResize);
    }
}); 