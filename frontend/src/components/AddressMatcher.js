export class AddressMatcher {
    constructor(container) {
        this.container = container;
    }
    
    render() {
        this.container.innerHTML = `
            <div class="row">
                <div class="col-lg-5 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-search-location me-2"></i>Match Address</h5>
                        </div>
                        <div class="card-body">
                            <form id="address-form">
                                <div class="mb-3">
                                    <label for="address-line-1" class="form-label">Address Line 1</label>
                                    <input type="text" class="form-control" id="address-line-1" placeholder="123 Main St">
                                </div>
                                <div class="mb-3">
                                    <label for="address-line-2" class="form-label">Address Line 2 (Optional)</label>
                                    <input type="text" class="form-control" id="address-line-2" placeholder="Apt 4B">
                                </div>
                                <div class="mb-3">
                                    <label for="city" class="form-label">City</label>
                                    <input type="text" class="form-control" id="city" placeholder="Brooklyn">
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <label for="state" class="form-label">State</label>
                                        <input type="text" class="form-control" id="state" placeholder="NY" maxlength="2">
                                    </div>
                                    <div class="col-md-6">
                                        <label for="zip-code" class="form-label">ZIP Code</label>
                                        <input type="text" class="form-control" id="zip-code" placeholder="11211" pattern="[0-9]{5}">
                                    </div>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-search me-2"></i>Match Address
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-7 mb-4">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-list-ul me-2"></i>Match Results</h5>
                            <span id="processing-time" class="text-light small"></span>
                        </div>
                        <div class="card-body" id="results-container">
                            <div class="text-center p-5">
                                <i class="fas fa-search fa-3x mb-3 text-muted"></i>
                                <h5>Enter an address to see matching results</h5>
                                <p class="text-muted">Results will appear here after submitting the form</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listener to form
        const form = this.container.querySelector('#address-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.matchAddress();
        });
    }
    
    async matchAddress() {
        const form = this.container.querySelector('#address-form');
        const resultsContainer = this.container.querySelector('#results-container');
        const processingTime = this.container.querySelector('#processing-time');
        
        // Get form values
        const addressData = {
            address_line_1: form.querySelector('#address-line-1').value,
            address_line_2: form.querySelector('#address-line-2').value || null,
            city: form.querySelector('#city').value,
            state: form.querySelector('#state').value,
            zip_code: parseInt(form.querySelector('#zip-code').value, 10)
        };
        
        // Validate required fields
        if (!addressData.address_line_1 || !addressData.city || !addressData.state || isNaN(addressData.zip_code)) {
            window.showNotification('Please fill out all required fields', 'error');
            return;
        }
        
        // Show loading spinner
        resultsContainer.innerHTML = `
            <div class="spinner-container">
                <div class="spinner"></div>
            </div>
        `;
        processingTime.textContent = '';
        
        try {
            const response = await window.apiService.matchAddress(addressData);
            
            // Display processing time
            processingTime.textContent = `Processed in ${response.processing_time_ms.toFixed(0)}ms`;
            
            // No matches found
            if (!response.matches || response.matches.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No matches found for this address.
                    </div>
                    <div class="text-center text-muted">
                        <p>Try adjusting the address or using different search terms.</p>
                    </div>
                `;
                return;
            }
            
            // Render matches
            this.renderMatches(response.matches);
            
        } catch (error) {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Failed to match address. Please try again later.
                </div>
            `;
            console.error('Address matching error:', error);
        }
    }
    
    renderMatches(matches) {
        const resultsContainer = this.container.querySelector('#results-container');
        resultsContainer.innerHTML = '';
        
        if (matches.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No matches found for this address.
                </div>
            `;
            return;
        }
        
        // Create results header
        const resultsHeader = document.createElement('div');
        resultsHeader.className = 'mb-3';
        resultsHeader.innerHTML = `
            <h6 class="text-muted mb-3">Found ${matches.length} match${matches.length !== 1 ? 'es' : ''}</h6>
        `;
        resultsContainer.appendChild(resultsHeader);
        
        // Create results list
        const resultsList = document.createElement('div');
        resultsList.className = 'results-list';
        
        matches.forEach((match, index) => {
            const confidenceClass = match.confidence_score > 0.8 ? 'high-confidence' : 'medium-confidence';
            const confidencePercentage = (match.confidence_score * 100).toFixed(1);
            
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            resultItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0">
                        <i class="fas fa-map-marker-alt me-2 text-primary"></i>
                        <span class="fw-bold">${match.address}</span>
                    </h6>
                    <span class="confidence-badge ${confidenceClass}">
                        ${confidencePercentage}%
                    </span>
                </div>
                <div class="d-flex justify-content-between text-muted small">
                    <div>
                        <span class="badge bg-light text-dark me-2">ID: ${match.hhid}</span>
                        <span class="badge bg-light text-dark">${match.match_type.toUpperCase()}</span>
                    </div>
                    <div>
                        <span class="text-muted">#${index + 1}</span>
                    </div>
                </div>
            `;
            resultsList.appendChild(resultItem);
        });
        
        resultsContainer.appendChild(resultsList);
    }
}