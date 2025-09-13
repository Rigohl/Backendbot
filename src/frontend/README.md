# BackendBot Frontend

A modern, responsive web dashboard for BackendBot system monitoring and management.

## Features

- **Real-time System Monitoring**: CPU, memory, disk usage, and process monitoring
- **RAM Optimization**: Built-in memory optimization tools
- **Activity History**: Track system activities and changes
- **Dark/Light Theme**: Automatic theme switching with system preference detection
- **Ultra Mode**: Enhanced performance mode with special visual effects
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Accessibility**: WCAG compliant with keyboard navigation and screen reader support
- **Internationalization**: Multi-language support (English, Spanish, French, German)

## Architecture

The frontend is built with modern JavaScript (ES6+) and follows a modular architecture:

```
src/frontend/
├── app.js              # Main application coordinator
├── main.js             # Entry point
├── index.html          # Main HTML template
├── components/         # UI components
│   ├── validation.js   # Form validation
│   ├── notifications.js # Notification system
│   ├── config.js       # Configuration modal
│   ├── theme.js        # Theme management
│   ├── metrics.js      # Metrics display
│   ├── auth.js         # Authentication
│   └── ultra.js        # Ultra mode
├── services/           # Business logic services
│   └── i18n.js         # Internationalization
├── utils/              # Utility functions
│   ├── dom.js          # DOM manipulation utilities
│   ├── api.js          # API communication utilities
│   └── utils.js        # General utilities
├── assets/             # Static assets
│   └── css/            # Stylesheets
└── tests/              # Unit tests
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- BackendBot backend server running

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd src/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

## Usage

### Basic Operation

1. **System Status**: View real-time CPU, memory, and disk usage
2. **RAM Monitor**: Monitor memory usage with optimization tools
3. **Process Monitor**: View and manage running processes
4. **Activity History**: Track system activities and changes

### Configuration

Access the settings modal by clicking the gear icon in the header:

- **Theme**: Switch between light, dark, and system themes
- **Language**: Change the interface language
- **Ultra Mode**: Enable enhanced performance mode
- **Notifications**: Configure notification preferences

### Keyboard Shortcuts

- `Ctrl/Cmd + K`: Open command palette
- `Ctrl/Cmd + ,`: Open settings
- `Ctrl/Cmd + Shift + T`: Toggle theme
- `Ctrl/Cmd + Shift + U`: Toggle ultra mode
- `Escape`: Close modals

## API Integration

The frontend communicates with the BackendBot backend via REST API:

### Endpoints

- `GET /api/health` - Health check
- `GET /api/metrics` - System metrics
- `GET /api/processes` - Process list
- `GET /api/history` - Activity history
- `POST /api/optimize` - Trigger optimization
- `POST /api/config` - Update configuration

### Authentication

The frontend supports token-based authentication. Set the auth token:

```javascript
import { api } from './utils/api.js';
api.setAuthToken('your-token-here');
```

## Development

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Code Style

The project uses ESLint for code linting. Run linting:

```bash
npm run lint
```

### Component Development

Components follow a consistent pattern:

```javascript
export class MyComponent {
    constructor(options = {}) {
        this.options = { ...defaultOptions, ...options };
        this.init();
    }

    init() {
        this.createUI();
        this.bindEvents();
    }

    createUI() {
        // Create component DOM
    }

    bindEvents() {
        // Bind event listeners
    }

    destroy() {
        // Cleanup
    }
}
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**Frontend not loading**
- Ensure the backend server is running
- Check browser console for errors
- Verify API endpoints are accessible

**Tests failing**
- Run `npm install` to ensure dependencies are installed
- Check Jest configuration in `package.json`
- Ensure test files are in the correct location

**Styling issues**
- Clear browser cache
- Check CSS custom properties support
- Verify theme application

### Debug Mode

Enable debug mode by adding `?debug=true` to the URL for additional logging and error information.
