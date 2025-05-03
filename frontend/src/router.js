import { Dashboard } from './components/Dashboard.js';
import { AddressMatcher } from './components/AddressMatcher.js';
import { Statistics } from './components/Statistics.js';
import { Navbar } from './components/Navbar.js';
import { LandingPage } from './components/LandingPage.js';

export class AppRouter {
    constructor(appElement) {
        this.appElement = appElement;
        this.routes = {
            '/': LandingPage,
            '/dashboard': Dashboard,
            '/match': AddressMatcher,
            '/statistics': Statistics
        };
        
        this.navbar = new Navbar();
        this.currentComponent = null;
        
        // For debugging
        console.log('Router initialized with routes:', Object.keys(this.routes));
    }
    
    init() {
        // Handle navigation
        window.addEventListener('popstate', () => this.navigate(window.location.pathname));
        
        // Handle links
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[data-link]') || e.target.closest('a[data-link]')) {
                const link = e.target.matches('a[data-link]') ? e.target : e.target.closest('a[data-link]');
                e.preventDefault();
                this.navigateTo(link.getAttribute('href'));
            }
        });
        
        // Initial navigation
        this.navigate(window.location.pathname);
        console.log('Initial navigation to:', window.location.pathname);
    }
    
    navigate(route) {
        // Default to home if route not found
        if (!this.routes[route]) {
            console.log(`Route "${route}" not found, defaulting to /`);
            route = '/';
        }
        
        console.log('Navigating to:', route);
        this.renderPage(route);
    }
    
    navigateTo(route) {
        console.log('Navigating to:', route);
        window.history.pushState(null, null, route);
        this.navigate(route);
    }
    
    renderPage(route) {
        const ComponentClass = this.routes[route];
        console.log('Rendering component for route:', route, ComponentClass.name);
        
        // Clear content
        this.appElement.innerHTML = '';
        
        // Only add navbar for non-landing pages
        if (route !== '/') {
            this.appElement.appendChild(this.navbar.render(route));
        }
        
        // Create content container
        const contentContainer = document.createElement('main');
        contentContainer.className = route === '/' ? 'landing-container' : 'container mt-4';
        this.appElement.appendChild(contentContainer);
        
        // Instantiate and render component
        this.currentComponent = new ComponentClass(contentContainer);
        this.currentComponent.render();
    }
} 