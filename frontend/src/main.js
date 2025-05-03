import { AppRouter } from './router.js';
import { ApiService } from './services/api.js';

// Initialize API service
const apiService = new ApiService('/api');
window.apiService = apiService;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing application');
    const app = document.getElementById('app');
    
    if (!app) {
        console.error('App container not found! Make sure the HTML has a div with id="app"');
        return;
    }
    
    // Initialize router
    console.log('Initializing router');
    const router = new AppRouter(app);
    router.init();
    
    // Check API health on startup
    console.log('Checking API health');
    apiService.getHealth()
        .then(data => {
            console.log('Health check response:', data);
            if (data.status === 'healthy') {
                console.log('API connection established');
            } else {
                showNotification('API connection error. Check server status.', 'error');
            }
        })
        .catch(err => {
            showNotification('Failed to connect to API. Ensure the server is running.', 'error');
            console.error('API connection error:', err);
        });
});

// Global notification function
window.showNotification = (message, type = 'info') => {
    console.log(`Showing notification: ${message} (${type})`);
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="close-btn"><i class="fas fa-times"></i></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 500);
    }, 5000);
    
    // Close button handler
    notification.querySelector('.close-btn').addEventListener('click', () => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 500);
    });
};
