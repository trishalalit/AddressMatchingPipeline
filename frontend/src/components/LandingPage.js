export class LandingPage {
    constructor(container) {
        this.container = container;
    }
    
    render() {
        this.container.innerHTML = `
            <div class="landing-page">
                <!-- Hero Section with Improved Design -->
                <div class="hero-section">
                    <div class="container py-5">
                        <div class="row align-items-center">
                            <div class="col-lg-6">
                                <h1 class="display-4 fw-bold mb-3">Address Matching Pipeline</h1>
                                <p class="lead mb-4">A smart system for matching transaction addresses against canonical records with high accuracy, developed by Trisha Lalit.</p>
                                <div class="cta-buttons">
                                    <a href="/dashboard" data-link class="btn btn-primary btn-lg me-3">
                                        <i class="fas fa-tachometer-alt me-2"></i>Launch Dashboard
                                    </a>
                                    <a href="/match" data-link class="btn btn-outline-primary btn-lg">
                                        <i class="fas fa-search-location me-2"></i>Try Address Matching
                                    </a>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="hero-illustration text-center">
                                    <div class="illustration-graphic">
                                        <i class="fas fa-map-marker-alt primary-icon"></i>
                                        <i class="fas fa-database secondary-icon"></i>
                                        <i class="fas fa-check-circle tertiary-icon"></i>
                                        <i class="fas fa-search-location quaternary-icon"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- What We Do Section -->
                <div class="features-section py-5 bg-light">
                    <div class="container">
                        <h2 class="text-center mb-4">What We Do</h2>
                        <p class="text-center mb-5">Our address matching system solves a common challenge: linking transaction records with their canonical address entries.</p>
                        
                        <div class="row g-4">
                            <div class="col-md-6 col-lg-3">
                                <div class="feature-card h-100">
                                    <div class="feature-icon">
                                        <i class="fas fa-file-import"></i>
                                    </div>
                                    <h5>Data Ingestion</h5>
                                    <p>Import address data from Excel/CSV files into our PostgreSQL database with automatic schema validation.</p>
                                </div>
                            </div>
                            
                            <div class="col-md-6 col-lg-3">
                                <div class="feature-card h-100">
                                    <div class="feature-icon">
                                        <i class="fas fa-magic"></i>
                                    </div>
                                    <h5>Address Parsing</h5>
                                    <p>Normalize raw address text into standardized components using specialized parsing libraries.</p>
                                </div>
                            </div>
                            
                            <div class="col-md-6 col-lg-3">
                                <div class="feature-card h-100">
                                    <div class="feature-icon">
                                        <i class="fas fa-layer-group"></i>
                                    </div>
                                    <h5>Multi-tier Matching</h5>
                                    <p>Employ a "waterfall" approach from exact to fuzzy to phonetic matching for optimal results.</p>
                                </div>
                            </div>
                            
                            <div class="col-md-6 col-lg-3">
                                <div class="feature-card h-100">
                                    <div class="feature-icon">
                                        <i class="fas fa-tachometer-alt"></i>
                                    </div>
                                    <h5>Performance Focus</h5>
                                    <p>Process data efficiently with optimized database queries, smart indexing, and batch processing.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- How It Works Section -->
                <div class="process-section py-5">
                    <div class="container">
                        <h2 class="text-center mb-5">How It Works</h2>
                        
                        <div class="row">
                            <div class="col-lg-10 mx-auto">
                                <div class="process-explanation p-4 bg-white rounded shadow-sm">
                                    <div class="process-steps">
                                        <div class="process-step">
                                            <div class="step-number">1</div>
                                            <div class="step-content">
                                                <h5>Address Ingestion</h5>
                                                <p>We load address data from various sources like Excel or CSV files into our PostgreSQL database, automatically validating the schema.</p>
                                            </div>
                                        </div>
                                        
                                        <div class="process-step">
                                            <div class="step-number">2</div>
                                            <div class="step-content">
                                                <h5>Normalization & Parsing</h5>
                                                <p>Raw addresses are broken down into standardized components (street numbers, names, units) using specialized libraries and custom logic.</p>
                                            </div>
                                        </div>
                                        
                                        <div class="process-step">
                                            <div class="step-number">3</div>
                                            <div class="step-content">
                                                <h5>Smart Matching</h5>
                                                <p>We use a tiered approach: exact matching first (fastest, most confident), then fuzzy matching for close matches, followed by phonetic matching for "sounds like" cases.</p>
                                            </div>
                                        </div>
                                        
                                        <div class="process-step">
                                            <div class="step-number">4</div>
                                            <div class="step-content">
                                                <h5>Results & Confidence</h5>
                                                <p>Each match receives a confidence score, allowing users to understand how reliable each match is and make informed decisions.</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Tech Stack Section -->
                <div class="tech-stack-section py-5 bg-light">
                    <div class="container">
                        <h2 class="text-center mb-5">Tech Stack</h2>
                        
                        <div class="row g-4 justify-content-center">
                            <div class="col-md-2 col-sm-4 col-6">
                                <div class="tech-item text-center">
                                    <i class="fas fa-database fa-2x text-primary mb-3"></i>
                                    <h6>PostgreSQL</h6>
                                </div>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <div class="tech-item text-center">
                                    <i class="fas fa-server fa-2x text-primary mb-3"></i>
                                    <h6>FastAPI</h6>
                                </div>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <div class="tech-item text-center">
                                    <i class="fab fa-python fa-2x text-primary mb-3"></i>
                                    <h6>Python</h6>
                                </div>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <div class="tech-item text-center">
                                    <i class="fab fa-js fa-2x text-primary mb-3"></i>
                                    <h6>JavaScript</h6>
                                </div>
                            </div>
                            <div class="col-md-2 col-sm-4 col-6">
                                <div class="tech-item text-center">
                                    <i class="fab fa-docker fa-2x text-primary mb-3"></i>
                                    <h6>Docker</h6>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Creator Section -->
                <div class="creator-section py-5">
                    <div class="container">
                        <div class="row align-items-center">
                            <div class="col-md-4 text-center mb-4 mb-md-0">
                                <div class="creator-avatar">
                                    <i class="fas fa-user-circle fa-6x text-primary"></i>
                                </div>
                            </div>
                            <div class="col-md-8">
                                <h2 class="mb-3">About the Creator</h2>
                                <p class="lead mb-3">This address matching pipeline was developed by Trisha Lalit, bringing together database optimization, smart matching algorithms, and user-friendly interfaces.</p>
                                <p>With a focus on real-world applications, this tool helps organizations efficiently match transaction addresses with their canonical records, improving data quality and analysis.</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- CTA Section -->
                <div class="cta-section py-5 bg-primary text-white text-center">
                    <div class="container">
                        <h2 class="mb-4">Ready to explore?</h2>
                        <p class="lead mb-4">See our address matching system in action and discover how it can transform your data management.</p>
                        <div class="d-flex justify-content-center gap-3">
                            <a href="/dashboard" data-link class="btn btn-light btn-lg px-4 py-2">
                                <i class="fas fa-tachometer-alt me-2"></i>View Dashboard
                            </a>
                            <a href="/match" data-link class="btn btn-outline-light btn-lg px-4 py-2">
                                <i class="fas fa-search-location me-2"></i>Try Matching
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add custom styling for new elements
        const style = document.createElement('style');
        style.textContent = `
            .feature-card {
                padding: 1.5rem;
                border-radius: 8px;
                background: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                color: var(--bs-primary);
                margin-bottom: 1rem;
            }
            
            .process-steps {
                display: flex;
                flex-direction: column;
                gap: 2rem;
            }
            
            .process-step {
                display: flex;
                gap: 1.5rem;
                align-items: flex-start;
            }
            
            .step-number {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: var(--bs-primary);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 1.25rem;
                flex-shrink: 0;
            }
            
            .step-content {
                flex: 1;
            }
            
            .creator-section {
                background-color: #f8f9fa;
            }
            
            .creator-avatar {
                padding: 1.5rem;
            }
        `;
        document.head.appendChild(style);
    }
} 