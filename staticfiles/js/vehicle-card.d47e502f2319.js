// Handle favorite button clicks
function toggleFavorite(button) {
    const vehicleId = button.dataset.vehicleId;
    
    fetch(`/ads/toggle-favorite/${vehicleId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            button.classList.toggle('active');
        }
    });
}

// Handle layout switching
document.addEventListener('DOMContentLoaded', function() {
    const layoutSwitchers = document.querySelectorAll('.layout-switcher');
    
    layoutSwitchers.forEach((switcher, index) => {
        const layoutButtons = switcher.querySelectorAll('.layout-btn');
        const vehicleGrid = switcher.parentElement.nextElementSibling;
        const storageKey = `preferredLayout_${index}`;
        
        // Apply saved layout preference on page load
        const savedLayout = localStorage.getItem(storageKey);
        if (savedLayout === 'list') {
            vehicleGrid.classList.add('list-layout');
            layoutButtons.forEach(btn => {
                if (btn.title === 'List Layout') {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }
    
        layoutButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons in this switcher
                layoutButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                this.classList.add('active');
                
                // Toggle list layout class based on which button was clicked
                if (this.title === 'List Layout') {
                    vehicleGrid.classList.add('list-layout');
                    localStorage.setItem(storageKey, 'list');
                } else {
                    vehicleGrid.classList.remove('list-layout');
                    localStorage.setItem(storageKey, 'grid');
                }
            });
        });
    });
});