// Energy Forecasting Script
// Main JavaScript for EcoGrid AI Forecasting Page

class EnergyForecastingSystem {
    constructor() {
        this.forecastChart = null;
        this.forecastData = [];
        this.modelMetrics = {};
        this.isTraining = false;
        this.isGenerating = false;
        
        this.initializeChart();
        this.loadModelStatus();
        this.bindEvents();
    }

    // Initialize Chart.js forecast chart
    initializeChart() {
        const ctx = document.getElementById('forecastChart');
        if (!ctx) return;

        this.forecastChart = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Solar Energy Forecast',
                        data: [],
                        borderColor: 'rgb(255, 206, 86)',
                        backgroundColor: 'rgba(255, 206, 86, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Wind Energy Forecast',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Total Energy Production',
                        data: [],
                        borderColor: 'rgb(139, 92, 246)',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: { 
                        labels: { color: 'white', font: { size: 14 } },
                        position: 'top'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' kWh';
                            }
                        }
                    }
                },
                scales: {
                    x: { 
                        ticks: { color: 'white', font: { size: 12 } },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        title: {
                            display: true,
                            text: 'Date',
                            color: 'white'
                        }
                    },
                    y: { 
                        ticks: { color: 'white', font: { size: 12 } },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        title: {
                            display: true,
                            text: 'Energy Production (kWh)',
                            color: 'white'
                        }
                    }
                }
            }
        });
    }

    // Load model status
    async loadModelStatus() {
        try {
            const response = await fetch('/forecast/model/status');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateModelStatus(data.model);
            }
        } catch (error) {
            console.log('Model status not available, using defaults');
            this.updateModelStatus({
                trained: false,
                accuracy: 0,
                data_points: 0,
                last_updated: null
            });
        }
    }

    // Update model status display
    updateModelStatus(model) {
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const accuracy = document.getElementById('model-accuracy');
        const trainingStatus = document.getElementById('training-status');
        const dataPoints = document.getElementById('data-points');
        const lastUpdated = document.getElementById('last-updated');

        if (model.trained) {
            indicator.className = 'w-3 h-3 bg-green-500 rounded-full';
            statusText.textContent = 'Model Trained';
            trainingStatus.textContent = 'Trained';
            accuracy.textContent = `${model.accuracy || 85}%`;
        } else {
            indicator.className = 'w-3 h-3 bg-yellow-500 rounded-full';
            statusText.textContent = 'Model Ready';
            trainingStatus.textContent = 'Not Trained';
            accuracy.textContent = '--%';
        }

        dataPoints.textContent = model.data_points || '--';
        
        if (model.last_updated) {
            const date = new Date(model.last_updated);
            lastUpdated.textContent = date.toLocaleDateString();
        } else {
            lastUpdated.textContent = '--';
        }
    }

    // Train the Prophet model
    async trainModel() {
        if (this.isTraining) return;
        
        const trainBtn = document.getElementById('train-btn');
        const originalText = trainBtn.innerHTML;
        
        try {
            this.isTraining = true;
            trainBtn.innerHTML = '<div class="loading-spinner inline-block mr-2"></div>Training...';
            trainBtn.disabled = true;

            this.updateModelStatus({ trained: false, training: true });

            const response = await fetch('/forecast/model/train', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('✅ Model trained successfully!', 'success');
                this.updateModelStatus(data.model);
                this.modelMetrics = data.model;
            } else {
                throw new Error(data.error || 'Training failed');
            }

        } catch (error) {
            console.error('Training error:', error);
            this.showNotification('❌ Training failed: ' + error.message, 'error');
        } finally {
            this.isTraining = false;
            trainBtn.innerHTML = originalText;
            trainBtn.disabled = false;
        }
    }

    // Generate energy forecast
    async generateForecast() {
        if (this.isGenerating) return;
        
        const forecastBtn = document.getElementById('forecast-btn');
        const originalText = forecastBtn.innerHTML;
        
        try {
            this.isGenerating = true;
            forecastBtn.innerHTML = '<div class="loading-spinner inline-block mr-2"></div>Generating...';
            forecastBtn.disabled = true;

            const response = await fetch('/forecast/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.forecastData = data.forecast;
                this.updateForecastDisplay(data.forecast);
                this.updateStatistics(data.statistics);
                this.updateForecastTable(data.forecast);
                this.showNotification('✅ Forecast generated successfully!', 'success');
            } else {
                throw new Error(data.error || 'Forecast generation failed');
            }

        } catch (error) {
            console.error('Forecast error:', error);
            this.showNotification('❌ Forecast failed: ' + error.message, 'error');
        } finally {
            this.isGenerating = false;
            forecastBtn.innerHTML = originalText;
            forecastBtn.disabled = false;
        }
    }

    // Update forecast chart
    updateForecastDisplay(forecastData) {
        if (!this.forecastChart || !forecastData.length) return;

        const labels = forecastData.map(d => d.date);
        const solarData = forecastData.map(d => parseFloat(d.solar_energy) || 0);
        const windData = forecastData.map(d => parseFloat(d.wind_energy) || 0);
        const totalData = forecastData.map(d => parseFloat(d.total_generation) || 0);

        this.forecastChart.data.labels = labels;
        this.forecastChart.data.datasets[0].data = solarData;
        this.forecastChart.data.datasets[1].data = windData;
        this.forecastChart.data.datasets[2].data = totalData;
        this.forecastChart.update();

        // Add fade-in animation
        document.getElementById('forecastChart').parentElement.classList.add('fade-in');
    }

    // Update statistics display
    updateStatistics(stats) {
        if (!stats) return;

        // Production statistics
        const totalSolar = stats.total_solar || 0;
        const totalWind = stats.total_wind || 0;
        const avgDaily = stats.average_daily || 0;
        const peakDay = stats.peak_day || 0;

        document.getElementById('total-solar').textContent = `${totalSolar.toFixed(1)} kWh`;
        document.getElementById('total-wind').textContent = `${totalWind.toFixed(1)} kWh`;
        document.getElementById('avg-daily').textContent = `${avgDaily.toFixed(1)} kWh`;
        document.getElementById('peak-day').textContent = `${peakDay.toFixed(1)} kWh`;

        // Model performance
        document.getElementById('trend-direction').textContent = stats.trend_direction || '→';
        document.getElementById('volatility').textContent = `${stats.volatility || 0}%`;
        document.getElementById('confidence').textContent = `${stats.confidence || 85}%`;
        document.getElementById('seasonal').textContent = stats.seasonal_pattern || 'Detecting...';
    }

    // Update forecast table
    updateForecastTable(forecastData) {
        const tbody = document.getElementById('forecast-table');
        tbody.innerHTML = '';

        forecastData.forEach((day, index) => {
            const solar = parseFloat(day.solar_energy || 0);
            const wind = parseFloat(day.wind_energy || 0);
            const total = parseFloat(day.total_generation || 0);
            
            const confidence = this.calculateConfidence(solar, wind);
            const pattern = this.detectPattern(solar, wind, index);

            const tr = document.createElement('tr');
            tr.className = 'border-b border-white/20 hover:bg-white/10 transition-colors fade-in';
            tr.style.animationDelay = `${index * 0.05}s`;
            
            tr.innerHTML = `
                <td class="py-3">${day.date}</td>
                <td class="py-3">${solar.toFixed(2)}</td>
                <td class="py-3">${wind.toFixed(2)}</td>
                <td class="py-3 font-semibold">${total.toFixed(2)}</td>
                <td class="py-3">
                    <span class="px-2 py-1 rounded text-xs ${
                        confidence > 80 ? 'bg-green-600' : 
                        confidence > 60 ? 'bg-yellow-600' : 'bg-red-600'
                    }">
                        ${confidence}%
                    </span>
                </td>
                <td class="py-3">${pattern}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Calculate prediction confidence
    calculateConfidence(solar, wind) {
        const total = solar + wind;
        if (total > 15) return 90;
        if (total > 10) return 75;
        if (total > 5) return 60;
        return 45;
    }

    // Detect energy pattern
    detectPattern(solar, wind, dayIndex) {
        const total = solar + wind;
        
        if (solar > wind * 2) return '☀️ Solar Dominant';
        if (wind > solar * 2) return '💨 Wind Dominant';
        if (total > 15) return '⚡ High Production';
        if (total > 8) return '⚖️ Balanced';
        return '🔋 Low Production';
    }

    // Export forecast data to CSV
    exportData() {
        if (!this.forecastData.length) {
            this.showNotification('❌ No data to export', 'error');
            return;
        }

        let csv = 'Date,Solar Energy (kWh),Wind Energy (kWh),Total Generation (kWh)\n';
        
        this.forecastData.forEach(day => {
            csv += `${day.date},${day.solar_energy},${day.wind_energy},${day.total_generation}\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `energy_forecast_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        this.showNotification('✅ Data exported successfully!', 'success');
    }

    // Show notification
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white font-medium z-50 fade-in ${
            type === 'success' ? 'bg-green-600' : 'bg-red-600'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Bind event listeners
    bindEvents() {
        // Auto-refresh model status every 30 seconds
        setInterval(() => {
            this.loadModelStatus();
        }, 30000);

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 't':
                        e.preventDefault();
                        this.trainModel();
                        break;
                    case 'g':
                        e.preventDefault();
                        this.generateForecast();
                        break;
                    case 'e':
                        e.preventDefault();
                        this.exportData();
                        break;
                }
            }
        });
    }
}

// Global functions for button onclick handlers
let forecastingSystem;

function trainModel() {
    forecastingSystem.trainModel();
}

function generateForecast() {
    forecastingSystem.generateForecast();
}

function exportData() {
    forecastingSystem.exportData();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    forecastingSystem = new EnergyForecastingSystem();
    console.log('Energy Forecasting System initialized');
});
