# Address Matching Frontend
This frontend provides a user-friendly interface for the address matching API, allowing users to:

- View system statistics and performance metrics
- Match addresses against the canonical database
- Monitor match rates and distribution

## Structure

```
frontend/
├── public/               # Static assets and HTML
├── src/                  # Application source code
│   ├── components/       # UI components
│   │   ├── Dashboard.js  # Homepage dashboard
│   │   ├── AddressMatcher.js # Address matching form
│   │   ├── Statistics.js # Detailed statistics page
│   │   └── Navbar.js     # Navigation component
│   ├── services/         # API integration
│   │   └── api.js        # Communication with backend API
│   ├── styles/           # CSS stylesheets
│   │   └── main.css      # Main application styles
│   ├── main.js           # Application entry point
│   └── router.js         # Client-side routing
└── nginx.conf            # Nginx configuration
```

## Technology Stack

- **Vanilla JavaScript** - No frameworks, just pure JS for simplicity
- **Bootstrap 5** - Responsive UI components and grid system
- **Chart.js** - Interactive data visualization
- **Nginx** - Static file serving and API proxy

## Development

### Local Development

To run the frontend locally for development:

1. Set up a local web server (like Python's built-in server):
   ```bash
   cd frontend
   python -m http.server 3000
   ```

2. Make sure the backend API is running on port 8000

### Building for Production

The frontend is deployed using Docker:

```bash
docker-compose up -d frontend
```

This will build and start the Nginx container serving the frontend.

## Features

### Dashboard

- Overview of key metrics
- Match rate and distribution visualization
- Quick access to main features

### Address Matcher

- Interactive form for address matching
- Real-time results with confidence scores
- Support for address components

### Statistics

- Detailed match statistics
- Performance metrics
- Interactive charts for data exploration

## Customization

- To modify colors and theme, edit `src/styles/main.css`
- To add new pages, update both `router.js` and create new component files
- To change API endpoints, modify `services/api.js` 