export class Navbar {
    render(currentRoute) {
        const navbar = document.createElement('nav');
        navbar.className = 'navbar navbar-expand-lg navbar-dark';
        navbar.innerHTML = `
            <div class="container">
                <a class="navbar-brand" href="/" data-link>
                    <i class="fas fa-map-marker-alt me-2"></i>
                    Address Matcher
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <a class="nav-link ${currentRoute === '/dashboard' ? 'active' : ''}" href="/dashboard" data-link>
                                <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link ${currentRoute === '/match' ? 'active' : ''}" href="/match" data-link>
                                <i class="fas fa-search-location me-1"></i> Match Address
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link ${currentRoute === '/statistics' ? 'active' : ''}" href="/statistics" data-link>
                                <i class="fas fa-chart-pie me-1"></i> Statistics
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        `;
        
        // Initialize Bootstrap navbar toggler
        const toggler = navbar.querySelector('.navbar-toggler');
        if (toggler) {
            toggler.addEventListener('click', () => {
                const target = document.querySelector(toggler.getAttribute('data-bs-target'));
                if (target) {
                    target.classList.toggle('show');
                }
            });
        }
        
        return navbar;
    }
} 