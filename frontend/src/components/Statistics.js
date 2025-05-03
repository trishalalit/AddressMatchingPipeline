export class Statistics {
    constructor(container) {
        this.container = container;
        this.stats = null;
    }
    
    async render() {
        this.container.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>Matching Statistics</h5>
                            <button id="refresh-stats" class="btn btn-sm btn-light">
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
            
            <div class="row">
                <div class="col-md-8 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Match Type Distribution</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="matchTypeChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-percent me-2"></i>Match Rate</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="matchRateChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Statistics Details</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table id="stats-table" class="table table-striped table-hover">
                                    <thead>
                                        <tr>
                                            <th>Metric</th>
                                            <th>Value</th>
                                            <th>Percentage</th>
                                        </tr>
                                    </thead>
                                    <tbody id="stats-table-body">
                                        <tr>
                                            <td colspan="3" class="text-center">Loading statistics...</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listener to refresh button
        const refreshBtn = this.container.querySelector('#refresh-stats');
        refreshBtn.addEventListener('click', () => this.loadData());
        
        // Load initial data
        await this.loadData();
    }
    
    async loadData() {
        try {
            this.stats = await window.apiService.getStatistics();
            this.renderStats();
            this.renderCharts();
            this.renderTable();
        } catch (error) {
            const statsContainer = this.container.querySelector('#stats-container');
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
        const formatNumber = (num) => new Intl.NumberFormat().format(num || 0);
        
        statsContainer.innerHTML = `
            <div class="row">
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="card stat-card h-100">
                        <i class="fas fa-database fa-2x text-primary"></i>
                        <div class="stat-value">${formatNumber(this.stats.total_transactions)}</div>
                        <div class="stat-label">Total Transactions</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="card stat-card h-100">
                        <i class="fas fa-check-circle fa-2x text-success"></i>
                        <div class="stat-value">${formatNumber(this.stats.matched_transactions)}</div>
                        <div class="stat-label">Matched Transactions</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="card stat-card h-100">
                        <i class="fas fa-percentage fa-2x text-primary"></i>
                        <div class="stat-value">${(this.stats.match_percentage || 0).toFixed(1)}%</div>
                        <div class="stat-label">Match Rate</div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6 mb-3">
                    <div class="card stat-card h-100">
                        <i class="fas fa-bolt fa-2x text-warning"></i>
                        <div class="stat-value">${formatNumber(this.stats.exact_matches)}</div>
                        <div class="stat-label">Exact Matches</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderCharts() {
        if (!this.stats) return;
        
        // Match Type Distribution Chart
        const matchTypeCanvas = document.getElementById('matchTypeChart');
        if (matchTypeCanvas) {
            const ctx = matchTypeCanvas.getContext('2d');
            
            // Destroy existing chart if it exists
            if (this.matchTypeChart) {
                this.matchTypeChart.destroy();
            }
            
            const matchTypes = ['Exact', 'Fuzzy', 'Phonetic', 'API'];
            const matchCounts = [
                this.stats.exact_matches || 0,
                this.stats.fuzzy_matches || 0,
                this.stats.phonetic_matches || 0,
                this.stats.api_matches || 0
            ];
            
            this.matchTypeChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: matchTypes,
                    datasets: [{
                        label: 'Number of Matches',
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
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Match Rate Chart
        const matchRateCanvas = document.getElementById('matchRateChart');
        if (matchRateCanvas) {
            const ctx = matchRateCanvas.getContext('2d');
            
            // Destroy existing chart if it exists
            if (this.matchRateChart) {
                this.matchRateChart.destroy();
            }
            
            const matchRate = this.stats.match_percentage || 0;
            const unmatchedRate = 100 - matchRate;
            
            this.matchRateChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Matched', 'Unmatched'],
                    datasets: [{
                        data: [matchRate, unmatchedRate],
                        backgroundColor: [
                            '#4cc9f0',
                            '#f1f1f1'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    return `${label}: ${value.toFixed(1)}%`;
                                }
                            }
                        }
                    }
                }
            });
            
            // Add center text
            Chart.register({
                id: 'centerText',
                afterDraw: (chart) => {
                    const width = chart.width;
                    const height = chart.height;
                    const ctx = chart.ctx;
                    
                    ctx.restore();
                    const fontSize = (height / 114).toFixed(2);
                    ctx.font = `${fontSize}em sans-serif`;
                    ctx.textBaseline = "middle";
                    
                    const text = `${matchRate.toFixed(1)}%`;
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    
                    ctx.fillStyle = "#4361ee";
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            });
        }
    }
    
    renderTable() {
        if (!this.stats) return;
        
        const tableBody = this.container.querySelector('#stats-table-body');
        const formatNumber = (num) => new Intl.NumberFormat().format(num || 0);
        const total = this.stats.total_transactions || 0;
        
        // Clear table
        tableBody.innerHTML = '';
        
        // Add rows
        const rows = [
            {
                metric: 'Total Transactions',
                value: this.stats.total_transactions || 0,
                percentage: 100
            },
            {
                metric: 'Matched Transactions',
                value: this.stats.matched_transactions || 0,
                percentage: total > 0 ? (this.stats.matched_transactions / total * 100) : 0
            },
            {
                metric: 'Unmatched Transactions',
                value: total - (this.stats.matched_transactions || 0),
                percentage: total > 0 ? ((total - (this.stats.matched_transactions || 0)) / total * 100) : 0
            },
            {
                metric: 'Exact Matches',
                value: this.stats.exact_matches || 0,
                percentage: total > 0 ? (this.stats.exact_matches / total * 100) : 0
            },
            {
                metric: 'Fuzzy Matches',
                value: this.stats.fuzzy_matches || 0,
                percentage: total > 0 ? (this.stats.fuzzy_matches / total * 100) : 0
            },
            {
                metric: 'Phonetic Matches',
                value: this.stats.phonetic_matches || 0,
                percentage: total > 0 ? (this.stats.phonetic_matches / total * 100) : 0
            },
            {
                metric: 'API Matches',
                value: this.stats.api_matches || 0,
                percentage: total > 0 ? (this.stats.api_matches / total * 100) : 0
            }
        ];
        
        rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.metric}</td>
                <td>${formatNumber(row.value)}</td>
                <td>
                    <div class="progress" style="height: 10px; width: 100px;">
                        <div class="progress-bar bg-primary" role="progressbar" style="width: ${row.percentage}%"></div>
                    </div>
                    <span class="ms-2">${row.percentage.toFixed(1)}%</span>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }
} 