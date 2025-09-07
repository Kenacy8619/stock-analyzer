// Stock Financial Analyzer JavaScript
class StockAnalyzer {
    constructor() {
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.tickerInput = document.getElementById('tickerInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.loading = document.getElementById('loading');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        this.stockTitle = document.getElementById('stockTitle');
        this.scoreCircle = document.getElementById('scoreCircle');
        this.scoreText = document.getElementById('scoreText');
        this.scoreLabel = document.getElementById('scoreLabel');
        this.detailedData = document.getElementById('detailedData');
        this.errorText = document.getElementById('errorText');
        this.retryBtn = document.getElementById('retryBtn');
    }

    bindEvents() {
        this.analyzeBtn.addEventListener('click', () => this.analyzeStock());
        this.tickerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeStock();
            }
        });
        this.retryBtn.addEventListener('click', () => this.hideError());
    }

    async analyzeStock() {
        const ticker = this.tickerInput.value.trim().toUpperCase();
        
        if (!ticker) {
            this.showError('Please enter a valid ticker symbol');
            return;
        }

        this.showLoading();
        
        try {
            // Simulate API call - replace with actual backend call
            const data = await this.fetchStockData(ticker);
            this.displayResults(ticker, data);
        } catch (error) {
            this.showError(`Error analyzing ${ticker}: ${error.message}`);
        }
    }

    async fetchStockData(ticker) {
        // Call Flask backend API
        try {
            const response = await fetch(`/analyze/${ticker}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Analysis failed');
            }
            
            return data;
        } catch (error) {
            throw new Error(`Failed to fetch data: ${error.message}`);
        }
        
    }

    showLoading() {
        this.hideAllSections();
        this.loading.classList.remove('hidden');
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.textContent = 'Analyzing...';
    }

    hideLoading() {
        this.loading.classList.add('hidden');
        this.analyzeBtn.disabled = false;
        this.analyzeBtn.textContent = 'Analyze Stock';
    }

    displayResults(ticker, data) {
        this.hideLoading();
        this.hideAllSections();
        
        // Update stock title
        this.stockTitle.textContent = `Financial Health Analysis - ${ticker}`;
        
        // Calculate and display score
        const passedChecks = data.checks.filter(check => check.passed).length;
        const totalChecks = data.checks.length;
        const percentage = (passedChecks / totalChecks) * 100;
        
        this.updateScoreCircle(passedChecks, totalChecks, percentage);
        
        // Update check cards
        this.updateCheckCards(data.checks);
        
        // Display detailed analysis with better formatting
        this.displayDetailedAnalysis(data.detailedAnalysis);
        
        // Show results section
        this.resultsSection.classList.remove('hidden');
        
        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    updateScoreCircle(passed, total, percentage) {
        this.scoreText.textContent = `${passed}/${total}`;
        
        // Update circle progress
        const degrees = (percentage / 100) * 360;
        this.scoreCircle.style.background = `conic-gradient(#58cc02 0deg, #58cc02 ${degrees}deg, #e5e5e5 ${degrees}deg)`;
        
        // Update score label with assessment
        let assessment;
        if (percentage >= 80) {
            assessment = 'EXCELLENT - Strong financial health';
        } else if (percentage >= 60) {
            assessment = 'GOOD - Solid financial position';
        } else if (percentage >= 40) {
            assessment = 'FAIR - Some concerns present';
        } else {
            assessment = 'POOR - Significant financial risks';
        }
        
        this.scoreLabel.textContent = `${percentage.toFixed(1)}% - ${assessment}`;
    }

    updateCheckCards(checks) {
        checks.forEach(check => {
            const card = document.querySelector(`[data-check="${check.id}"]`);
            if (card) {
                const resultIcon = card.querySelector('.result-icon');
                
                // Update card styling
                card.classList.remove('pass', 'fail');
                card.classList.add(check.passed ? 'pass' : 'fail');
                
                // Update icon
                resultIcon.textContent = check.passed ? '✅' : '❌';
                resultIcon.classList.remove('pass', 'fail');
                resultIcon.classList.add(check.passed ? 'pass' : 'fail');
                
                // Update content if provided
                const content = card.querySelector('.check-content h3');
                if (content) {
                    content.textContent = check.name;
                }
                
                const description = card.querySelector('.check-description');
                if (description) {
                    description.textContent = check.description;
                }
                
                // Add tooltip with details
                card.title = check.details || '';
            }
        });
    }

    showError(message) {
        this.hideLoading();
        this.hideAllSections();
        this.errorText.textContent = message;
        this.errorSection.classList.remove('hidden');
    }

    hideError() {
        this.errorSection.classList.add('hidden');
    }

    displayDetailedAnalysis(analysisText) {
        // Parse and format the detailed analysis for better readability
        const sections = analysisText.split('\n\n');
        let formattedHTML = '';
        
        sections.forEach(section => {
            if (section.trim() === '') return;
            
            const lines = section.split('\n');
            const firstLine = lines[0].trim();
            
            if (firstLine.includes('STOCK ANALYSIS FOR')) {
                formattedHTML += `<div class="financial-section">
                    <h4>${firstLine}</h4>
                </div>`;
            } else if (firstLine.match(/^\d+\./)) {
                // This is a numbered section
                const title = firstLine;
                formattedHTML += `<div class="financial-section">
                    <h4>${title}</h4>`;
                
                // Process the data lines
                for (let i = 1; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (line === '') continue;
                    
                    if (line.includes(':')) {
                        const [label, value] = line.split(':');
                        const cleanLabel = label.trim().replace(/^\s*/, '');
                        const cleanValue = value.trim();
                        
                        // Check if it's a financial value
                        if (cleanValue.includes('$') || cleanValue.includes('%')) {
                            const isNegative = cleanValue.includes('-');
                            formattedHTML += `<div class="financial-item">
                                <span class="financial-year">${cleanLabel}</span>
                                <span class="financial-value ${isNegative ? 'negative' : ''}">${cleanValue}</span>
                            </div>`;
                        } else {
                            formattedHTML += `<div class="financial-item">
                                <span class="financial-year">${cleanLabel}</span>
                                <span class="ratio-display">${cleanValue}</span>
                            </div>`;
                        }
                    } else {
                        formattedHTML += `<div class="financial-item">
                            <span>${line}</span>
                        </div>`;
                    }
                }
                formattedHTML += '</div>';
            }
        });
        
        this.detailedData.innerHTML = formattedHTML;
    }

    hideAllSections() {
        this.resultsSection.classList.add('hidden');
        this.errorSection.classList.add('hidden');
        this.loading.classList.add('hidden');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StockAnalyzer();
});

// Add some interactive animations
document.addEventListener('DOMContentLoaded', () => {
    // Add hover effects to check cards
    const checkCards = document.querySelectorAll('.check-card');
    checkCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'none';
        });
    });
});
