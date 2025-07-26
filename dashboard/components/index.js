/**
 * Component Index for Ash-Thrash Dashboard Integration
 * 
 * Central entry point for all dashboard components. Provides easy
 * initialization and management of multiple testing components.
 * 
 * Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
 * Discord: https://discord.gg/alphabetcartel
 */

// Import components (adjust paths as needed for your setup)
// Uncomment these if using ES6 modules:
// import TestingMetrics from './TestingMetrics.js';
// import TestRunner from './TestRunner.js';

/**
 * Dashboard Component Manager
 * Handles initialization and coordination of multiple testing components
 */
class AshThrashDashboard {
    constructor(options = {}) {
        this.options = {
            apiBaseUrl: '/api/testing',
            autoInit: true,
            globalRefreshInterval: 60000,
            theme: 'light',
            errorRetryAttempts: 3,
            errorRetryDelay: 5000,
            ...options
        };
        
        this.components = new Map();
        this.globalRefreshTimer = null;
        this.isInitialized = false;
        
        if (this.options.autoInit) {
            this.init();
        }
    }
    
    /**
     * Initialize the dashboard and auto-discover components
     */
    init() {
        if (this.isInitialized) return;
        
        this.log('info', 'Initializing Ash-Thrash Dashboard...');
        
        // Auto-discover and initialize components
        this.autoDiscoverComponents();
        
        // Set up global event listeners
        this.setupGlobalEvents();
        
        // Start global refresh if enabled
        if (this.options.globalRefreshInterval > 0) {
            this.startGlobalRefresh();
        }
        
        this.isInitialized = true;
        this.log('success', `Dashboard initialized with ${this.components.size} components`);
        
        // Emit ready event
        this.emit('ready', {
            componentCount: this.components.size,
            components: Array.from(this.components.keys())
        });
    }
    
    /**
     * Auto-discover components based on data attributes
     */
    autoDiscoverComponents() {
        // Discover TestingMetrics components
        document.querySelectorAll('[data-testing-metrics]').forEach(element => {
            if (!element.id) {
                element.id = `testing-metrics-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            }
            
            const options = this.parseDataOptions(element.dataset.testingMetrics);
            this.addTestingMetrics(element.id, options);
        });
        
        // Discover TestRunner components
        document.querySelectorAll('[data-test-runner]').forEach(element => {
            if (!element.id) {
                element.id = `test-runner-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            }
            
            const options = this.parseDataOptions(element.dataset.testRunner);
            this.addTestRunner(element.id, options);
        });
        
        // Discover combined dashboard containers
        document.querySelectorAll('[data-ash-thrash-dashboard]').forEach(element => {
            const options = this.parseDataOptions(element.dataset.ashThrashDashboard);
            this.createCombinedDashboard(element, options);
        });
    }
    
    /**
     * Add a TestingMetrics component
     */
    addTestingMetrics(containerId, options = {}) {
        const mergedOptions = {
            ...this.options,
            ...options,
            apiBaseUrl: options.apiBaseUrl || this.options.apiBaseUrl
        };
        
        try {
            const component = new TestingMetrics(containerId, mergedOptions);
            this.components.set(containerId, {
                type: 'TestingMetrics',
                instance: component,
                options: mergedOptions
            });
            
            this.log('info', `Added TestingMetrics component: ${containerId}`);
            return component;
        } catch (error) {
            this.log('error', `Failed to create TestingMetrics component: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Add a TestRunner component
     */
    addTestRunner(containerId, options = {}) {
        const mergedOptions = {
            ...this.options,
            ...options,
            apiBaseUrl: options.apiBaseUrl || this.options.apiBaseUrl
        };
        
        try {
            const component = new TestRunner(containerId, mergedOptions);
            this.components.set(containerId, {
                type: 'TestRunner',
                instance: component,
                options: mergedOptions
            });
            
            this.log('info', `Added TestRunner component: ${containerId}`);
            return component;
        } catch (error) {
            this.log('error', `Failed to create TestRunner component: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Create a combined dashboard with both metrics and runner
     */
    createCombinedDashboard(container, options = {}) {
        const dashboardId = container.id || `ash-dashboard-${Date.now()}`;
        
        // Create HTML structure for combined dashboard
        container.innerHTML = `
            <div class="ash-thrash-combined-dashboard">
                <div class="dashboard-header">
                    <h2 class="dashboard-title">
                        <i class="fas fa-vial"></i>
                        Ash Crisis Detection Testing
                    </h2>
                    <div class="dashboard-subtitle">
                        Real-time monitoring and testing control for 
                        <a href="https://discord.gg/alphabetcartel" target="_blank">The Alphabet Cartel</a>
                    </div>
                </div>
                
                <div class="dashboard-grid">
                    <div class="metrics-section">
                        <div id="${dashboardId}-metrics" data-testing-metrics='${JSON.stringify(options.metrics || {})}'></div>
                    </div>
                    
                    <div class="runner-section">
                        <div id="${dashboardId}-runner" data-test-runner='${JSON.stringify(options.runner || {})}'></div>
                    </div>
                </div>
                
                <div class="dashboard-footer">
                    <div class="footer-links">
                        <a href="https://github.com/The-Alphabet-Cartel/ash-thrash" target="_blank">
                            <i class="fab fa-github"></i> ash-thrash
                        </a>
                        <a href="https://github.com/The-Alphabet-Cartel/ash-dash" target="_blank">
                            <i class="fab fa-github"></i> ash-dash
                        </a>
                        <a href="https://discord.gg/alphabetcartel" target="_blank">
                            <i class="fab fa-discord"></i> Discord
                        </a>
                    </div>
                    <div class="footer-status">
                        <span id="${dashboardId}-status">Dashboard Ready</span>
                    </div>
                </div>
            </div>
        `;
        
        // Add CSS for combined dashboard
        if (!document.querySelector('#ash-thrash-combined-css')) {
            const style = document.createElement('style');
            style.id = 'ash-thrash-combined-css';
            style.textContent = this.getCombinedDashboardCSS();
            document.head.appendChild(style);
        }
        
        // Initialize components
        const metricsComponent = this.addTestingMetrics(`${dashboardId}-metrics`, options.metrics);
        const runnerComponent = this.addTestRunner(`${dashboardId}-runner`, options.runner);
        
        // Set up cross-component communication
        this.setupCombinedDashboardEvents(dashboardId, metricsComponent, runnerComponent);
        
        return { metrics: metricsComponent, runner: runnerComponent };
    }
    
    /**
     * Set up events for combined dashboard
     */
    setupCombinedDashboardEvents(dashboardId, metrics, runner) {
        const container = document.getElementById(dashboardId.replace('-metrics', '').replace('-runner', ''));
        if (!container) return;
        
        // Listen for test completion to refresh metrics
        container.addEventListener('test-runner-completed', () => {
            if (metrics) {
                setTimeout(() => metrics.loadData(true), 2000);
            }
        });
        
        // Listen for metrics expand to show detailed view
        container.addEventListener('testing-metrics-expand', (e) => {
            this.emit('metrics-expand', e.detail);
        });
        
        // Update dashboard status
        const updateStatus = (status) => {
            const statusElement = document.getElementById(`${dashboardId}-status`);
            if (statusElement) {
                statusElement.textContent = status;
            }
        };
        
        // Monitor component health
        const healthCheck = async () => {
            try {
                const response = await fetch(`${this.options.apiBaseUrl}/health`);
                updateStatus(response.ok ? 'All Systems Operational' : 'Service Degraded');
            } catch (error) {
                updateStatus('Connection Issues');
            }
        };
        
        // Run health check every 30 seconds
        setInterval(healthCheck, 30000);
        healthCheck(); // Initial check
    }
    
    /**
     * Set up global event listeners
     */
    setupGlobalEvents() {
        // Handle component errors
        document.addEventListener('component-error', (e) => {
            this.log('error', `Component error: ${e.detail.message}`);
            this.emit('error', e.detail);
        });
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseRefresh();
            } else {
                this.resumeRefresh();
            }
        });
        
        // Handle network status changes
        window.addEventListener('online', () => {
            this.log('info', 'Network connection restored');
            this.refreshAllComponents();
        });
        
        window.addEventListener('offline', () => {
            this.log('warning', 'Network connection lost');
        });
    }
    
    /**
     * Start global refresh timer
     */
    startGlobalRefresh() {
        if (this.globalRefreshTimer) return;
        
        this.globalRefreshTimer = setInterval(() => {
            if (!document.hidden) {
                this.refreshAllComponents();
            }
        }, this.options.globalRefreshInterval);
    }
    
    /**
     * Stop global refresh timer
     */
    stopGlobalRefresh() {
        if (this.globalRefreshTimer) {
            clearInterval(this.globalRefreshTimer);
            this.globalRefreshTimer = null;
        }
    }
    
    /**
     * Pause refresh (e.g., when page is hidden)
     */
    pauseRefresh() {
        this.stopGlobalRefresh();
    }
    
    /**
     * Resume refresh
     */
    resumeRefresh() {
        this.startGlobalRefresh();
    }
    
    /**
     * Refresh all components
     */
    refreshAllComponents() {
        this.components.forEach((component, id) => {
            try {
                if (component.instance && typeof component.instance.loadData === 'function') {
                    component.instance.loadData(true);
                }
            } catch (error) {
                this.log('error', `Failed to refresh component ${id}: ${error.message}`);
            }
        });
    }
    
    /**
     * Get a component by ID
     */
    getComponent(id) {
        return this.components.get(id);
    }
    
    /**
     * Remove a component
     */
    removeComponent(id) {
        const component = this.components.get(id);
        if (component) {
            try {
                if (component.instance && typeof component.instance.destroy === 'function') {
                    component.instance.destroy();
                }
            } catch (error) {
                this.log('error', `Error destroying component ${id}: ${error.message}`);
            }
            
            this.components.delete(id);
            this.log('info', `Removed component: ${id}`);
        }
    }
    
    /**
     * Update global options
     */
    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
        
        // Update component options
        this.components.forEach((component, id) => {
            if (component.instance && typeof component.instance.setOptions === 'function') {
                component.instance.setOptions(newOptions);
            }
        });
    }
    
    /**
     * Parse data attribute options
     */
    parseDataOptions(optionsString) {
        if (!optionsString) return {};
        
        try {
            return JSON.parse(optionsString);
        } catch (error) {
            this.log('warning', `Invalid JSON in data options: ${optionsString}`);
            return {};
        }
    }
    
    /**
     * Get CSS for combined dashboard
     */
    getCombinedDashboardCSS() {
        return `
            .ash-thrash-combined-dashboard {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .dashboard-header {
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 2px solid #e5e7eb;
            }
            
            .dashboard-title {
                font-size: 2rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0 0 0.5rem 0;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.75rem;
            }
            
            .dashboard-subtitle {
                color: #6b7280;
                font-size: 1rem;
            }
            
            .dashboard-subtitle a {
                color: #3b82f6;
                text-decoration: none;
                font-weight: 600;
            }
            
            .dashboard-subtitle a:hover {
                text-decoration: underline;
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 2rem;
                margin-bottom: 2rem;
            }
            
            @media (min-width: 1024px) {
                .dashboard-grid {
                    grid-template-columns: 2fr 1fr;
                }
            }
            
            .dashboard-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-top: 1rem;
                border-top: 1px solid #e5e7eb;
                font-size: 0.875rem;
                color: #6b7280;
            }
            
            .footer-links {
                display: flex;
                gap: 1rem;
            }
            
            .footer-links a {
                color: #6b7280;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                transition: color 0.2s ease;
            }
            
            .footer-links a:hover {
                color: #3b82f6;
            }
            
            @media (max-width: 768px) {
                .ash-thrash-combined-dashboard {
                    padding: 1rem;
                }
                
                .dashboard-title {
                    font-size: 1.5rem;
                    flex-direction: column;
                    gap: 0.5rem;
                }
                
                .dashboard-footer {
                    flex-direction: column;
                    gap: 1rem;
                    text-align: center;
                }
                
                .footer-links {
                    justify-content: center;
                }
            }
        `;
    }
    
    /**
     * Emit custom events
     */
    emit(eventName, detail = {}) {
        const event = new CustomEvent(`ash-thrash-dashboard-${eventName}`, {
            detail: { dashboard: this, ...detail }
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Logging helper
     */
    log(level, message) {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [AshThrashDashboard] [${level.toUpperCase()}] ${message}`;
        
        switch (level) {
            case 'error':
                console.error(logMessage);
                break;
            case 'warning':
                console.warn(logMessage);
                break;
            case 'success':
            case 'info':
            default:
                console.log(logMessage);
        }
    }
    
    /**
     * Destroy the dashboard and all components
     */
    destroy() {
        this.stopGlobalRefresh();
        
        this.components.forEach((component, id) => {
            this.removeComponent(id);
        });
        
        this.components.clear();
        this.isInitialized = false;
        
        this.log('info', 'Dashboard destroyed');
    }
}

// Global instance for easy access
let globalDashboard = null;

/**
 * Initialize dashboard with default settings
 */
function initAshThrashDashboard(options = {}) {
    if (globalDashboard) {
        globalDashboard.destroy();
    }
    
    globalDashboard = new AshThrashDashboard(options);
    return globalDashboard;
}

/**
 * Get the global dashboard instance
 */
function getAshThrashDashboard() {
    return globalDashboard;
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AshThrashDashboard,
        initAshThrashDashboard,
        getAshThrashDashboard,
        TestingMetrics: typeof TestingMetrics !== 'undefined' ? TestingMetrics : null,
        TestRunner: typeof TestRunner !== 'undefined' ? TestRunner : null
    };
}

// Make available globally
if (typeof window !== 'undefined') {
    window.AshThrashDashboard = AshThrashDashboard;
    window.initAshThrashDashboard = initAshThrashDashboard;
    window.getAshThrashDashboard = getAshThrashDashboard;
}

// Auto-initialize on DOM ready if not already initialized
document.addEventListener('DOMContentLoaded', () => {
    // Only auto-init if there are components to discover and no manual init
    const hasComponents = document.querySelector('[data-testing-metrics], [data-test-runner], [data-ash-thrash-dashboard]');
    
    if (hasComponents && !globalDashboard) {
        initAshThrashDashboard();
    }
});