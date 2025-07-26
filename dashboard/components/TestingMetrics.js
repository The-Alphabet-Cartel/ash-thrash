/**
 * Testing Metrics Component for Ash-Dash Integration
 * 
 * Reusable React/JavaScript component for displaying ash-thrash
 * testing metrics in various dashboard configurations.
 * 
 * Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
 * Discord: https://discord.gg/alphabetcartel
 */

class TestingMetrics {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            apiBaseUrl: '/api/testing',
            refreshInterval: 60000,
            compact: false,
            showAlerts: true,
            showCategories: true,
            theme: 'light',
            ...options
        };
        
        this.data = null;
        this.refreshTimer = null;
        this.isLoading = false;
        
        if (!this.container) {
            console.error(`TestingMetrics: Container ${containerId} not found`);
            return;
        }
        
        this.init();
    }
    
    init() {
        this.container.className = `testing-metrics-component ${this.options.theme}`;
        this.render();
        this.loadData();
        this.startAutoRefresh();
    }
    
    render() {
        const compactClass = this.options.compact ? 'compact' : '';
        
        this.container.innerHTML = `
            <div class="testing-metrics-container ${compactClass}">
                <div class="metrics-header">
                    <h3 class="metrics-title">
                        <i class="fas fa-vial"></i>
                        Testing Metrics
                    </h3>
                    <div class="metrics-controls">
                        <button class="refresh-btn" data-action="refresh" title="Refresh Data">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        ${!this.options.compact ? '<button class="expand-btn" data-action="expand" title="Expand View"><i class="fas fa-expand"></i></button>' : ''}
                    </div>
                </div>
                
                <div class="metrics-content">
                    <div class="loading-state" style="display: none;">
                        <div class="spinner"></div>
                        <span>Loading metrics...</span>
                    </div>
                    
                    <div class="error-state" style="display: none;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span class="error-message">Failed to load data</span>
                    </div>
                    
                    <div class="metrics-data" style="display: none;">
                        <div class="primary-metrics">
                            <div class="metric-card primary">
                                <div class="metric-icon">
                                    <i class="fas fa-bullseye"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-value" data-metric="pass-rate">0%</div>
                                    <div class="metric-label">Pass Rate</div>
                                    <div class="metric-change" data-metric="pass-rate-trend"></div>
                                </div>
                            </div>
                            
                            <div class="metric-card secondary">
                                <div class="metric-icon">
                                    <i class="fas fa-trophy"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-value" data-metric="goals-achieved">0</div>
                                    <div class="metric-label">Goals Met</div>
                                    <div class="metric-sublabel" data-metric="goals-total">of 0 total</div>
                                </div>
                            </div>
                            
                            <div class="metric-card secondary">
                                <div class="metric-icon">
                                    <i class="fas fa-clock"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-value" data-metric="response-time">0ms</div>
                                    <div class="metric-label">Response Time</div>
                                    <div class="metric-sublabel">Average</div>
                                </div>
                            </div>
                            
                            <div class="metric-card secondary">
                                <div class="metric-icon">
                                    <i class="fas fa-list-check"></i>
                                </div>
                                <div class="metric-content">
                                    <div class="metric-value" data-metric="total-tests">0</div>
                                    <div class="metric-label">Total Tests</div>
                                    <div class="metric-sublabel" data-metric="test-ratio">0 passed</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="secondary-metrics" ${this.options.compact ? 'style="display: none;"' : ''}>
                            <div class="categories-section" ${!this.options.showCategories ? 'style="display: none;"' : ''}>
                                <h4 class="section-title">Category Performance</h4>
                                <div class="categories-grid" data-section="categories">
                                    <!-- Categories populated dynamically -->
                                </div>
                            </div>
                            
                            <div class="alerts-section" ${!this.options.showAlerts ? 'style="display: none;"' : ''}>
                                <h4 class="section-title">
                                    <i class="fas fa-bell"></i>
                                    Active Alerts
                                    <span class="alert-count" data-metric="alert-count">0</span>
                                </h4>
                                <div class="alerts-list" data-section="alerts">
                                    <!-- Alerts populated dynamically -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="metrics-footer">
                    <div class="last-updated">
                        Last updated: <span data-metric="last-updated">Never</span>
                    </div>
                    <div class="status-indicator">
                        <span class="status-dot" data-metric="status"></span>
                        <span data-metric="status-text">Unknown</span>
                    </div>
                </div>
            </div>
        `;
        
        this.bindEvents();
    }
    
    bindEvents() {
        this.container.addEventListener('click', (e) => {
            const action = e.target.closest('[data-action]')?.dataset.action;
            
            switch (action) {
                case 'refresh':
                    this.loadData(true);
                    break;
                case 'expand':
                    this.expandView();
                    break;
            }
        });
    }
    
    async loadData(force = false) {
        if (this.isLoading && !force) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const [statusResponse, goalsResponse] = await Promise.all([
                fetch(`${this.options.apiBaseUrl}/status`),
                fetch(`${this.options.apiBaseUrl}/goals`)
            ]);
            
            if (!statusResponse.ok) {
                throw new Error(`Status API error: ${statusResponse.status}`);
            }
            
            if (!goalsResponse.ok) {
                throw new Error(`Goals API error: ${goalsResponse.status}`);
            }
            
            const statusData = await statusResponse.json();
            const goalsData = await goalsResponse.json();
            
            this.data = {
                status: statusData.data,
                goals: goalsData.data,
                timestamp: new Date().toISOString()
            };
            
            this.updateDisplay();
            this.showData();
            
        } catch (error) {
            console.error('TestingMetrics: Failed to load data', error);
            this.showError(error.message);
        } finally {
            this.isLoading = false;
        }
    }
    
    updateDisplay() {
        if (!this.data) return;
        
        const { status, goals } = this.data;
        
        // Update primary metrics
        this.updateMetric('pass-rate', `${Math.round(status.metrics.overall_pass_rate || 0)}%`);
        this.updateMetric('goals-achieved', goals.summary.goals_achieved || 0);
        this.updateMetric('goals-total', `of ${goals.summary.total_goals || 0} total`);
        this.updateMetric('response-time', `${Math.round(status.metrics.avg_response_time || 0)}ms`);
        this.updateMetric('total-tests', status.metrics.total_tests || 0);
        this.updateMetric('test-ratio', `${status.metrics.tests_passed || 0} passed`);
        
        // Update status
        this.updateStatus(status.testing_status.overall_health);
        
        // Update timestamp
        this.updateMetric('last-updated', this.formatTime(this.data.timestamp));
        
        // Update categories
        if (this.options.showCategories) {
            this.updateCategories(status.categories);
        }
        
        // Update alerts
        if (this.options.showAlerts) {
            this.updateAlerts(status.alerts);
        }
        
        // Update trends
        this.updateTrends(status.metrics);
    }
    
    updateMetric(key, value) {
        const element = this.container.querySelector(`[data-metric="${key}"]`);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateStatus(health) {
        const statusDot = this.container.querySelector('[data-metric="status"]');
        const statusText = this.container.querySelector('[data-metric="status-text"]');
        
        if (statusDot) {
            statusDot.className = 'status-dot';
            switch (health) {
                case 'healthy':
                    statusDot.classList.add('healthy');
                    break;
                case 'warning':
                    statusDot.classList.add('warning');
                    break;
                case 'error':
                    statusDot.classList.add('error');
                    break;
                default:
                    statusDot.classList.add('unknown');
            }
        }
        
        if (statusText) {
            statusText.textContent = health || 'Unknown';
        }
    }
    
    updateCategories(categories) {
        const grid = this.container.querySelector('[data-section="categories"]');
        if (!grid || !categories) return;
        
        grid.innerHTML = '';
        
        Object.entries(categories).forEach(([key, category]) => {
            const categoryElement = document.createElement('div');
            categoryElement.className = 'category-item';
            
            const statusClass = category.goal_met ? 'success' : 
                               category.pass_rate >= 80 ? 'warning' : 'danger';
            
            categoryElement.innerHTML = `
                <div class="category-header">
                    <span class="category-name">${category.display_name || key}</span>
                    <span class="category-status ${statusClass}">
                        <i class="fas ${category.goal_met ? 'fa-check' : 'fa-times'}"></i>
                    </span>
                </div>
                <div class="category-progress">
                    <div class="progress-bar">
                        <div class="progress-fill ${statusClass}" style="width: ${Math.min(category.pass_rate || 0, 100)}%"></div>
                    </div>
                    <div class="progress-text">${Math.round(category.pass_rate || 0)}%</div>
                </div>
            `;
            
            grid.appendChild(categoryElement);
        });
    }
    
    updateAlerts(alerts) {
        const alertsList = this.container.querySelector('[data-section="alerts"]');
        const alertCount = this.container.querySelector('[data-metric="alert-count"]');
        
        if (alertCount) {
            alertCount.textContent = alerts ? alerts.length : 0;
        }
        
        if (!alertsList) return;
        
        if (!alerts || alerts.length === 0) {
            alertsList.innerHTML = '<div class="no-alerts">No active alerts</div>';
            return;
        }
        
        alertsList.innerHTML = '';
        
        alerts.slice(0, 3).forEach(alert => { // Show max 3 alerts in component
            const alertElement = document.createElement('div');
            alertElement.className = `alert-item ${alert.severity || 'info'}`;
            
            alertElement.innerHTML = `
                <div class="alert-content">
                    <div class="alert-title">${alert.title || 'Alert'}</div>
                    <div class="alert-message">${alert.message || 'No details'}</div>
                </div>
                <div class="alert-time">${this.formatTime(alert.timestamp)}</div>
            `;
            
            alertsList.appendChild(alertElement);
        });
        
        if (alerts.length > 3) {
            const moreElement = document.createElement('div');
            moreElement.className = 'more-alerts';
            moreElement.textContent = `+${alerts.length - 3} more alerts`;
            alertsList.appendChild(moreElement);
        }
    }
    
    updateTrends(metrics) {
        // This would be enhanced with actual trend data from the API
        const trendElement = this.container.querySelector('[data-metric="pass-rate-trend"]');
        if (trendElement) {
            const passRate = metrics.overall_pass_rate || 0;
            let trendClass = 'stable';
            let trendIcon = 'fa-minus';
            let trendText = 'Stable';
            
            // This would use real trend calculation in production
            if (passRate >= 95) {
                trendClass = 'positive';
                trendIcon = 'fa-arrow-up';
                trendText = '+2.3%';
            } else if (passRate < 80) {
                trendClass = 'negative';
                trendIcon = 'fa-arrow-down';
                trendText = '-1.5%';
            }
            
            trendElement.className = `metric-change ${trendClass}`;
            trendElement.innerHTML = `<i class="fas ${trendIcon}"></i> ${trendText}`;
        }
    }
    
    showLoading() {
        this.container.querySelector('.loading-state').style.display = 'flex';
        this.container.querySelector('.metrics-data').style.display = 'none';
        this.container.querySelector('.error-state').style.display = 'none';
    }
    
    showData() {
        this.container.querySelector('.loading-state').style.display = 'none';
        this.container.querySelector('.metrics-data').style.display = 'block';
        this.container.querySelector('.error-state').style.display = 'none';
    }
    
    showError(message) {
        this.container.querySelector('.loading-state').style.display = 'none';
        this.container.querySelector('.metrics-data').style.display = 'none';
        this.container.querySelector('.error-state').style.display = 'flex';
        this.container.querySelector('.error-message').textContent = message;
    }
    
    expandView() {
        // Emit custom event for parent dashboard to handle
        const event = new CustomEvent('testing-metrics-expand', {
            detail: { component: this, data: this.data }
        });
        this.container.dispatchEvent(event);
    }
    
    formatTime(timestamp) {
        if (!timestamp) return 'Never';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString();
    }
    
    startAutoRefresh() {
        if (this.options.refreshInterval > 0) {
            this.refreshTimer = setInterval(() => {
                this.loadData();
            }, this.options.refreshInterval);
        }
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    setOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
        this.render();
        this.loadData();
    }
    
    getData() {
        return this.data;
    }
    
    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestingMetrics;
}

// Auto-initialize components with data-testing-metrics attribute
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-testing-metrics]').forEach(element => {
        const options = element.dataset.testingMetrics ? 
            JSON.parse(element.dataset.testingMetrics) : {};
        new TestingMetrics(element.id, options);
    });
});