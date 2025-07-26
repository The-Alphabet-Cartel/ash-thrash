/**
 * Test Runner Component for Ash-Dash Integration
 * 
 * Interactive component for triggering and monitoring test execution
 * from the dashboard interface.
 * 
 * Repository: https://github.com/The-Alphabet-Cartel/ash-thrash
 * Discord: https://discord.gg/alphabetcartel
 */

class TestRunner {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            apiBaseUrl: '/api/testing',
            allowedTestTypes: ['quick', 'comprehensive', 'category'],
            showProgress: true,
            showLogs: true,
            autoRefreshResults: true,
            theme: 'light',
            ...options
        };
        
        this.isRunning = false;
        this.currentTest = null;
        this.progressTimer = null;
        this.logBuffer = [];
        
        if (!this.container) {
            console.error(`TestRunner: Container ${containerId} not found`);
            return;
        }
        
        this.init();
    }
    
    init() {
        this.container.className = `test-runner-component ${this.options.theme}`;
        this.render();
        this.bindEvents();
        this.checkRunningTests();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="test-runner-container">
                <div class="runner-header">
                    <h3 class="runner-title">
                        <i class="fas fa-play-circle"></i>
                        Test Runner
                    </h3>
                    <div class="runner-status">
                        <span class="status-indicator" data-status="idle">
                            <i class="fas fa-circle"></i>
                            <span class="status-text">Ready</span>
                        </span>
                    </div>
                </div>
                
                <div class="test-controls">
                    <div class="test-type-selector">
                        <label for="test-type-select">Test Type:</label>
                        <select id="test-type-select" data-control="test-type">
                            ${this.options.allowedTestTypes.map(type => 
                                `<option value="${type}">${this.formatTestTypeName(type)}</option>`
                            ).join('')}
                        </select>
                    </div>
                    
                    <div class="test-options">
                        <label class="checkbox-label">
                            <input type="checkbox" data-control="verbose" checked>
                            <span class="checkmark"></span>
                            Verbose Output
                        </label>
                        
                        <label class="checkbox-label">
                            <input type="checkbox" data-control="save-results" checked>
                            <span class="checkmark"></span>
                            Save Results
                        </label>
                    </div>
                    
                    <div class="action-buttons">
                        <button class="run-btn primary" data-action="run" disabled>
                            <i class="fas fa-play"></i>
                            <span class="btn-text">Run Test</span>
                        </button>
                        
                        <button class="stop-btn danger" data-action="stop" style="display: none;">
                            <i class="fas fa-stop"></i>
                            <span class="btn-text">Stop Test</span>
                        </button>
                        
                        <button class="clear-btn secondary" data-action="clear">
                            <i class="fas fa-trash"></i>
                            <span class="btn-text">Clear</span>
                        </button>
                    </div>
                </div>
                
                <div class="test-progress" style="display: none;" ${!this.options.showProgress ? 'data-hidden="true"' : ''}>
                    <div class="progress-header">
                        <span class="progress-label">Running: <span class="current-test-name">-</span></span>
                        <span class="progress-percentage">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-details">
                        <span class="tests-completed">0</span> of <span class="tests-total">0</span> tests completed
                        <span class="estimated-time">ETA: --</span>
                    </div>
                </div>
                
                <div class="test-output" ${!this.options.showLogs ? 'style="display: none;"' : ''}>
                    <div class="output-header">
                        <h4 class="output-title">
                            <i class="fas fa-terminal"></i>
                            Test Output
                        </h4>
                        <div class="output-controls">
                            <button class="scroll-btn" data-action="scroll-bottom" title="Scroll to Bottom">
                                <i class="fas fa-arrow-down"></i>
                            </button>
                            <button class="download-btn" data-action="download-log" title="Download Log">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                    <div class="console-output" data-output="console">
                        <div class="console-line info">
                            <span class="timestamp">[${new Date().toLocaleTimeString()}]</span>
                            <span class="message">Test runner initialized. Ready to run tests.</span>
                        </div>
                    </div>
                </div>
                
                <div class="test-results" style="display: none;">
                    <div class="results-header">
                        <h4 class="results-title">
                            <i class="fas fa-chart-bar"></i>
                            Test Results
                        </h4>
                        <div class="results-controls">
                            <button class="view-details-btn" data-action="view-details">
                                <i class="fas fa-eye"></i>
                                View Details
                            </button>
                        </div>
                    </div>
                    <div class="results-summary" data-section="results-summary">
                        <!-- Results populated dynamically -->
                    </div>
                </div>
            </div>
        `;
        
        // Enable run button after render
        setTimeout(() => {
            this.container.querySelector('[data-action="run"]').disabled = false;
        }, 100);
    }
    
    bindEvents() {
        this.container.addEventListener('click', (e) => {
            const action = e.target.closest('[data-action]')?.dataset.action;
            
            switch (action) {
                case 'run':
                    this.runTest();
                    break;
                case 'stop':
                    this.stopTest();
                    break;
                case 'clear':
                    this.clearOutput();
                    break;
                case 'scroll-bottom':
                    this.scrollToBottom();
                    break;
                case 'download-log':
                    this.downloadLog();
                    break;
                case 'view-details':
                    this.viewDetailedResults();
                    break;
            }
        });
        
        // Auto-scroll console output
        const consoleOutput = this.container.querySelector('[data-output="console"]');
        if (consoleOutput) {
            consoleOutput.addEventListener('DOMNodeInserted', () => {
                this.scrollToBottom();
            });
        }
    }
    
    async runTest() {
        if (this.isRunning) return;
        
        const testType = this.container.querySelector('[data-control="test-type"]').value;
        const verbose = this.container.querySelector('[data-control="verbose"]').checked;
        const saveResults = this.container.querySelector('[data-control="save-results"]').checked;
        
        this.isRunning = true;
        this.updateStatus('running', 'Running Test...');
        this.showProgress();
        this.toggleButtons(true);
        
        this.logMessage('info', `Starting ${this.formatTestTypeName(testType)} test...`);
        
        try {
            const response = await fetch(`${this.options.apiBaseUrl}/trigger`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    test_type: testType,
                    verbose: verbose,
                    save_results: saveResults,
                    triggered_by: 'dashboard-test-runner'
                })
            });
            
            if (!response.ok) {
                throw new Error(`Test trigger failed: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            this.currentTest = result;
            
            this.logMessage('success', `Test initiated successfully. Test ID: ${result.test_id}`);
            this.logMessage('info', `Estimated duration: ${result.estimated_duration || 'Unknown'}`);
            
            // Start monitoring progress
            this.startProgressMonitoring();
            
        } catch (error) {
            this.logMessage('error', `Failed to start test: ${error.message}`);
            this.updateStatus('error', 'Test Failed');
            this.isRunning = false;
            this.hideProgress();
            this.toggleButtons(false);
        }
    }
    
    async stopTest() {
        if (!this.isRunning || !this.currentTest) return;
        
        this.logMessage('warning', 'Stopping test...');
        
        try {
            const response = await fetch(`${this.options.apiBaseUrl}/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    test_id: this.currentTest.test_id
                })
            });
            
            if (response.ok) {
                this.logMessage('warning', 'Test stopped successfully');
            } else {
                this.logMessage('warning', 'Test may not have stopped cleanly');
            }
            
        } catch (error) {
            this.logMessage('error', `Error stopping test: ${error.message}`);
        } finally {
            this.testCompleted(false);
        }
    }
    
    async startProgressMonitoring() {
        if (!this.currentTest) return;
        
        const updateProgress = async () => {
            try {
                const response = await fetch(`${this.options.apiBaseUrl}/progress/${this.currentTest.test_id}`);
                
                if (response.ok) {
                    const progress = await response.json();
                    this.updateProgress(progress);
                    
                    if (progress.status === 'completed') {
                        this.testCompleted(true, progress.results);
                        return;
                    } else if (progress.status === 'failed') {
                        this.testCompleted(false, null, progress.error);
                        return;
                    }
                }
                
                // Continue monitoring if test is still running
                if (this.isRunning) {
                    this.progressTimer = setTimeout(updateProgress, 2000);
                }
                
            } catch (error) {
                this.logMessage('warning', `Progress monitoring error: ${error.message}`);
                
                // Retry monitoring
                if (this.isRunning) {
                    this.progressTimer = setTimeout(updateProgress, 5000);
                }
            }
        };
        
        // Start monitoring after a brief delay
        this.progressTimer = setTimeout(updateProgress, 1000);
    }
    
    updateProgress(progress) {
        const progressBar = this.container.querySelector('.progress-fill');
        const progressPercentage = this.container.querySelector('.progress-percentage');
        const testsCompleted = this.container.querySelector('.tests-completed');
        const testsTotal = this.container.querySelector('.tests-total');
        const estimatedTime = this.container.querySelector('.estimated-time');
        const currentTestName = this.container.querySelector('.current-test-name');
        
        if (progressBar) {
            progressBar.style.width = `${progress.percentage || 0}%`;
        }
        
        if (progressPercentage) {
            progressPercentage.textContent = `${Math.round(progress.percentage || 0)}%`;
        }
        
        if (testsCompleted) {
            testsCompleted.textContent = progress.completed || 0;
        }
        
        if (testsTotal) {
            testsTotal.textContent = progress.total || 0;
        }
        
        if (estimatedTime && progress.eta) {
            estimatedTime.textContent = `ETA: ${progress.eta}`;
        }
        
        if (currentTestName && progress.current_test) {
            currentTestName.textContent = progress.current_test;
        }
        
        // Log progress messages
        if (progress.messages) {
            progress.messages.forEach(msg => {
                this.logMessage(msg.level || 'info', msg.message);
            });
        }
    }
    
    testCompleted(success, results = null, error = null) {
        this.isRunning = false;
        this.currentTest = null;
        
        if (this.progressTimer) {
            clearTimeout(this.progressTimer);
            this.progressTimer = null;
        }
        
        this.hideProgress();
        this.toggleButtons(false);
        
        if (success) {
            this.updateStatus('success', 'Test Completed');
            this.logMessage('success', 'Test completed successfully!');
            
            if (results) {
                this.displayResults(results);
            }
        } else {
            this.updateStatus('error', 'Test Failed');
            this.logMessage('error', error || 'Test failed or was stopped');
        }
    }
    
    displayResults(results) {
        const resultsSection = this.container.querySelector('.test-results');
        const resultsSummary = this.container.querySelector('[data-section="results-summary"]');
        
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        if (resultsSummary) {
            resultsSummary.innerHTML = `
                <div class="summary-metrics">
                    <div class="summary-item success">
                        <div class="summary-value">${Math.round(results.overall_pass_rate || 0)}%</div>
                        <div class="summary-label">Pass Rate</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">${results.tests_passed || 0}</div>
                        <div class="summary-label">Passed</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">${results.tests_failed || 0}</div>
                        <div class="summary-label">Failed</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">${Math.round(results.avg_response_time || 0)}ms</div>
                        <div class="summary-label">Avg Time</div>
                    </div>
                </div>
                
                <div class="goals-summary">
                    <h5>Goal Achievement</h5>
                    <div class="goals-list">
                        ${Object.entries(results.category_results || {}).map(([category, data]) => `
                            <div class="goal-item ${data.goal_met ? 'achieved' : 'not-achieved'}">
                                <span class="goal-name">${category.replace('_', ' ').toUpperCase()}</span>
                                <span class="goal-rate">${Math.round(data.pass_rate || 0)}%</span>
                                <i class="fas ${data.goal_met ? 'fa-check' : 'fa-times'}"></i>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }
    
    updateStatus(status, text) {
        const statusIndicator = this.container.querySelector('.status-indicator');
        const statusText = this.container.querySelector('.status-text');
        
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${status}`;
        }
        
        if (statusText) {
            statusText.textContent = text;
        }
    }
    
    showProgress() {
        const progressSection = this.container.querySelector('.test-progress');
        if (progressSection && !progressSection.dataset.hidden) {
            progressSection.style.display = 'block';
        }
    }
    
    hideProgress() {
        const progressSection = this.container.querySelector('.test-progress');
        if (progressSection) {
            progressSection.style.display = 'none';
        }
    }
    
    toggleButtons(running) {
        const runBtn = this.container.querySelector('[data-action="run"]');
        const stopBtn = this.container.querySelector('[data-action="stop"]');
        
        if (runBtn) {
            runBtn.disabled = running;
            runBtn.style.display = running ? 'none' : 'inline-flex';
        }
        
        if (stopBtn) {
            stopBtn.style.display = running ? 'inline-flex' : 'none';
        }
    }
    
    logMessage(level, message) {
        const consoleOutput = this.container.querySelector('[data-output="console"]');
        if (!consoleOutput) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = {
            timestamp,
            level,
            message
        };
        
        this.logBuffer.push(logEntry);
        
        const logLine = document.createElement('div');
        logLine.className = `console-line ${level}`;
        logLine.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="level">[${level.toUpperCase()}]</span>
            <span class="message">${message}</span>
        `;
        
        consoleOutput.appendChild(logLine);
        
        // Limit log lines to prevent memory issues
        const lines = consoleOutput.querySelectorAll('.console-line');
        if (lines.length > 1000) {
            lines[0].remove();
        }
        
        this.scrollToBottom();
    }
    
    clearOutput() {
        const consoleOutput = this.container.querySelector('[data-output="console"]');
        const resultsSection = this.container.querySelector('.test-results');
        
        if (consoleOutput) {
            consoleOutput.innerHTML = `
                <div class="console-line info">
                    <span class="timestamp">[${new Date().toLocaleTimeString()}]</span>
                    <span class="message">Output cleared.</span>
                </div>
            `;
        }
        
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        this.logBuffer = [];
        this.updateStatus('idle', 'Ready');
    }
    
    scrollToBottom() {
        const consoleOutput = this.container.querySelector('[data-output="console"]');
        if (consoleOutput) {
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }
    }
    
    downloadLog() {
        if (this.logBuffer.length === 0) {
            this.logMessage('warning', 'No log data to download');
            return;
        }
        
        const logContent = this.logBuffer.map(entry => 
            `[${entry.timestamp}] [${entry.level.toUpperCase()}] ${entry.message}`
        ).join('\n');
        
        const blob = new Blob([logContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test-runner-log-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.logMessage('info', 'Log downloaded successfully');
    }
    
    viewDetailedResults() {
        // Emit event for parent dashboard to handle
        const event = new CustomEvent('test-runner-view-details', {
            detail: { 
                component: this, 
                results: this.container.querySelector('[data-section="results-summary"]')?.dataset.results 
            }
        });
        this.container.dispatchEvent(event);
    }
    
    async checkRunningTests() {
        try {
            const response = await fetch(`${this.options.apiBaseUrl}/status`);
            if (response.ok) {
                const data = await response.json();
                if (data.data.testing_status.current_test) {
                    // There's a test already running
                    this.logMessage('info', 'Detected running test, monitoring progress...');
                    this.currentTest = { test_id: data.data.testing_status.current_test };
                    this.isRunning = true;
                    this.updateStatus('running', 'Running Test...');
                    this.showProgress();
                    this.toggleButtons(true);
                    this.startProgressMonitoring();
                }
            }
        } catch (error) {
            this.logMessage('warning', 'Could not check for running tests');
        }
    }
    
    formatTestTypeName(type) {
        const names = {
            quick: 'Quick Validation (10 tests)',
            comprehensive: 'Comprehensive Suite (350 tests)',
            category: 'Category-Specific Test'
        };
        return names[type] || type.charAt(0).toUpperCase() + type.slice(1);
    }
    
    destroy() {
        if (this.progressTimer) {
            clearTimeout(this.progressTimer);
        }
        
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestRunner;
}

// Auto-initialize components with data-test-runner attribute
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-test-runner]').forEach(element => {
        const options = element.dataset.testRunner ? 
            JSON.parse(element.dataset.testRunner) : {};
        new TestRunner(element.id, options);
    });
});