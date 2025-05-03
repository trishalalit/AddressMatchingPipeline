export class Dashboard {
    constructor(container) {
        this.container = container;
        this.stats = null;
    }
    
    async render() {
        this.container.innerHTML = `
            <div class="dashboard-header text-center p-4">
                <h2><i class="fas fa-tachometer-alt me-2"></i>Address Matching Dashboard</h2>
                <p class="lead mb-0">Monitor your address matching system performance and statistics</p>
            </div>
            
            <div class="row g-4">
                <div class="col-12">
                    <div class="card dashboard-card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i>System Overview</h5>
                            <button id="refresh-btn" class="btn btn-sm btn-light">
                                <i class="fas fa-sync-alt"></i> Refresh
                            </button>
                        </div>
                        <div class="card-body" id="stats-container">
                            <div class="spinner-container">
                                <div class="spinner"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row g-4 mt-1">
                <div class="col-lg-8">
                    <div class="card dashboard-card h-100">
                        <div class="card-header">
                            <h5><i class="fas fa-percentage"></i>Match Distribution</h5>
                            <div class="badge bg-primary rounded-pill" id="total-matches-badge">0 matches</div>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="matchChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card dashboard-card h-100">
                        <div class="card-header">
                            <h5><i class="fas fa-cogs"></i>Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="list-group">
                                <a href="/match" data-link class="list-group-item list-group-item-action d-flex align-items-center p-3">
                                    <div class="d-flex align-items-center">
                                        <div class="action-icon me-3">
                                            <i class="fas fa-search-location"></i>
                                        </div>
                                        <div>
                                            <h6 class="mb-1">Match Address</h6>
                                            <p class="mb-0 text-muted small">Match a single address against the database</p>
                                        </div>
                                    </div>
                                    <i class="fas fa-chevron-right ms-auto"></i>
                                </a>
                                <a href="/statistics" data-link class="list-group-item list-group-item-action d-flex align-items-center p-3">
                                    <div class="d-flex align-items-center">
                                        <div class="action-icon me-3">
                                            <i class="fas fa-chart-pie"></i>
                                        </div>
                                        <div>
                                            <h6 class="mb-1">View Statistics</h6>
                                            <p class="mb-0 text-muted small">Detailed system performance metrics</p>
                                        </div>
                                    </div>
                                    <i class="fas fa-chevron-right ms-auto"></i>
                                </a>
                                <a href="#" class="list-group-item list-group-item-action d-flex align-items-center p-3" id="run-pipeline-btn">
                                    <div class="d-flex align-items-center">
                                        <div class="action-icon me-3">
                                            <i class="fas fa-play-circle"></i>
                                        </div>
                                        <div>
                                            <h6 class="mb-1">Run Pipeline</h6>
                                            <p class="mb-0 text-muted small">Process all pending addresses</p>
                                        </div>
                                    </div>
                                    <i class="fas fa-chevron-right ms-auto"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row g-4 mt-1">
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-database"></i>
                        </div>
                        <div class="metric-value" id="total-transactions">0</div>
                        <div class="metric-label">Total Transactions</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="metric-value" id="matched-transactions">0</div>
                        <div class="metric-label">Matched Transactions</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div class="metric-value" id="match-rate">0%</div>
                        <div class="metric-label">Match Rate</div>
                        <div class="progress-container w-100">
                            <div class="progress">
                                <div class="progress-bar" id="match-rate-progress" style="width: 0%"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-bolt"></i>
                        </div>
                        <div class="metric-value" id="exact-matches">0</div>
                        <div class="metric-label">Exact Matches</div>
                    </div>
                </div>
            </div>
            
            <div class="row g-4 mt-1">
                <div class="col-12">
                    <div class="card dashboard-card">
                        <div class="card-header">
                            <h5><i class="fas fa-info-circle"></i>System Status</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="system-status-item" id="database-status">
                                        <h6><i class="fas fa-database me-2"></i>Database Connection</h6>
                                        <div class="status-badge badge bg-secondary">Checking...</div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="system-status-item" id="api-status">
                                        <h6><i class="fas fa-cloud me-2"></i>API Service</h6>
                                        <div class="status-badge badge bg-secondary">Checking...</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listener to refresh button
        const refreshBtn = this.container.querySelector('#refresh-btn');
        refreshBtn.addEventListener('click', () => this.loadData());
        
        // Add event listener to run pipeline button
        const runPipelineBtn = this.container.querySelector('#run-pipeline-btn');
        runPipelineBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.runPipeline();
        });
        
        // Load initial data
        await this.loadData();
        this.checkSystemStatus();
    }
    
    async loadData() {
        const statsContainer = this.container.querySelector('#stats-container');
        statsContainer.innerHTML = `
            <div class="spinner-container">
                <div class="spinner"></div>
            </div>
        `;
        
        try {
            this.stats = await window.apiService.getStatistics();
            this.renderStats();
            this.renderChart();
            this.updateMetricCards();
        } catch (error) {
            statsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Failed to load statistics. Please try again later.
                </div>
            `;
            console.error('Failed to load statistics:', error);
        }
    }
    
    renderStats() {
        if (!this.stats) return;
        
        const statsContainer = this.container.querySelector('#stats-container');
        statsContainer.innerHTML = '';
        
        const statContainer = document.createElement('div');
        statContainer.className = 'stat-container';
        
        const formatNumber = (num) => new Intl.NumberFormat().format(num || 0);
        
        // Stat cards
        const statCards = [
            {
                icon: 'fa-database',
                label: 'Total Transactions',
                value: formatNumber(this.stats.total_transactions)
            },
            {
                icon: 'fa-check-circle',
                label: 'Matched Transactions',
                value: formatNumber(this.stats.matched_transactions)
            },
            {
                icon: 'fa-percentage',
                label: 'Match Rate',
                value: `${(this.stats.match_percentage || 0).toFixed(1)}%`
            },
            {
                icon: 'fa-bolt',
                label: 'Exact Matches',
                value: formatNumber(this.stats.exact_matches)
            }
        ];
        
        statCards.forEach(stat => {
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `
                <i class="fas ${stat.icon} fa-2x text-primary"></i>
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            `;
            statContainer.appendChild(card);
        });
        
        statsContainer.appendChild(statContainer);
    }
    
    updateMetricCards() {
        if (!this.stats) return;
        
        const formatNumber = (num) => new Intl.NumberFormat().format(num || 0);
        
        // Update metric cards
        document.getElementById('total-transactions').textContent = formatNumber(this.stats.total_transactions || 0);
        document.getElementById('matched-transactions').textContent = formatNumber(this.stats.matched_transactions || 0);
        
        const matchRate = this.stats.match_percentage || 0;
        document.getElementById('match-rate').textContent = `${matchRate.toFixed(1)}%`;
        document.getElementById('match-rate-progress').style.width = `${matchRate}%`;
        
        document.getElementById('exact-matches').textContent = formatNumber(this.stats.exact_matches || 0);
        
        // Update total matches badge
        const totalMatches = this.stats.matched_transactions || 0;
        document.getElementById('total-matches-badge').textContent = `${formatNumber(totalMatches)} matches`;
    }
    
    renderChart() {
        if (!this.stats) return;
        
        const ctx = document.getElementById('matchChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }
        
        const matchCounts = [
            this.stats.exact_matches || 0,
            this.stats.fuzzy_matches || 0,
            this.stats.phonetic_matches || 0,
            this.stats.api_matches || 0
        ];
        
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Exact', 'Fuzzy', 'Phonetic', 'API'],
                datasets: [{
                    data: matchCounts,
                    backgroundColor: [
                        '#4361ee',
                        '#3f37c9',
                        '#4cc9f0',
                        '#f72585'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = matchCounts.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    async checkSystemStatus() {
        // Check database and API status
        try {
            const health = await window.apiService.getHealth();
            
            const databaseStatus = document.querySelector('#database-status .status-badge');
            const apiStatus = document.querySelector('#api-status .status-badge');
            
            if (health.status === 'healthy') {
                apiStatus.className = 'status-badge badge bg-success';
                apiStatus.textContent = 'Online';
            } else {
                apiStatus.className = 'status-badge badge bg-warning';
                apiStatus.textContent = 'Warning';
            }
            
            if (health.database === 'connected') {
                databaseStatus.className = 'status-badge badge bg-success';
                databaseStatus.textContent = 'Connected';
            } else {
                databaseStatus.className = 'status-badge badge bg-danger';
                databaseStatus.textContent = 'Disconnected';
            }
        } catch (error) {
            console.error('Health check failed:', error);
            
            const databaseStatus = document.querySelector('#database-status .status-badge');
            const apiStatus = document.querySelector('#api-status .status-badge');
            
            databaseStatus.className = 'status-badge badge bg-danger';
            databaseStatus.textContent = 'Error';
            
            apiStatus.className = 'status-badge badge bg-danger';
            apiStatus.textContent = 'Offline';
        }
    }
    
    runPipeline() {
        window.showNotification('Pipeline execution requested. This is a mock functionality in the UI demo.', 'info');
    }
} 