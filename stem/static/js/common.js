// Common JavaScript functions for Tatlock
// Shared functionality used across both authenticated and non-authenticated pages

// Password visibility toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const toggleBtn = input.parentElement.querySelector('.password-toggle');
    const icon = toggleBtn.querySelector('.material-icons');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = 'visibility_off';
        toggleBtn.title = 'Hide password';
    } else {
        input.type = 'password';
        icon.textContent = 'visibility';
        toggleBtn.title = 'Show password';
    }
}

// Show/hide sections in pages with multiple sections (admin dashboard, chat, etc.)
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Remove active class from all nav items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // Show the selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
    
    // Add active class to the clicked nav item
    const activeNavItem = document.querySelector(`[onclick="showSection('${sectionId}')"]`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
} 