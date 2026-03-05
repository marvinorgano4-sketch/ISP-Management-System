/**
 * Bandwidth Monitor Component
 * 
 * Polls bandwidth data from the API and updates the UI in real-time.
 * Requirements: 2.5, 3.5
 */

class BandwidthMonitor {
    constructor() {
        this.updateInterval = 10000; // 10 seconds
        this.intervalId = null;
        this.isLoading = false;
    }

    /**
     * Start polling for bandwidth data
     */
    start() {
        // Fetch immediately
        this.fetchBandwidthData();
        this.fetchTotalBandwidth();
        
        // Then poll every 10 seconds
        this.intervalId = setInterval(() => {
            this.fetchBandwidthData();
            this.fetchTotalBandwidth();
        }, this.updateInterval);
    }

    /**
     * Stop polling
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Fetch bandwidth data for all clients
     * Requirements: 2.2, 2.3, 2.4
     */
    async fetchBandwidthData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const response = await fetch('/api/bandwidth/all');
            const result = await response.json();
            
            if (result.success) {
                // Update each client row
                result.data.forEach(clientData => {
                    this.updateClientRow(clientData);
                });
                this.hideError();
            } else {
                this.showError(result.error || 'Failed to fetch bandwidth data');
            }
        } catch (error) {
            this.showError('Connection error: ' + error.message);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    /**
     * Fetch total bandwidth aggregated data
     * Requirements: 3.3, 3.4
     */
    async fetchTotalBandwidth() {
        try {
            const response = await fetch('/api/bandwidth/total');
            const result = await response.json();
            
            if (result.success) {
                this.updateTotalDisplay(result.data);
                this.showCongestionIndicator(result.data);
            }
        } catch (error) {
            console.error('Error fetching total bandwidth:', error);
        }
    }

    /**
     * Update a specific client row with bandwidth data
     * Requirements: 2.2, 2.3, 2.4
     */
    updateClientRow(clientData) {
        const row = document.querySelector(`tr[data-client-id="${clientData.client_id}"]`);
        if (!row) return;
        
        const rxCell = row.querySelector('.bandwidth-rx');
        const txCell = row.querySelector('.bandwidth-tx');
        const statusCell = row.querySelector('.connection-status');
        
        if (clientData.is_online) {
            if (rxCell) rxCell.textContent = clientData.rx_mbps.toFixed(2) + ' Mbps';
            if (txCell) txCell.textContent = clientData.tx_mbps.toFixed(2) + ' Mbps';
            if (statusCell) {
                statusCell.textContent = 'Online';
                statusCell.className = 'connection-status status-online';
            }
        } else {
            if (rxCell) rxCell.textContent = 'Offline';
            if (txCell) txCell.textContent = 'Offline';
            if (statusCell) {
                statusCell.textContent = 'Offline';
                statusCell.className = 'connection-status status-offline';
            }
        }
    }

    /**
     * Update total bandwidth display
     * Requirements: 3.3, 3.4
     */
    updateTotalDisplay(data) {
        const totalRxEl = document.getElementById('total-rx');
        const totalTxEl = document.getElementById('total-tx');
        const activeSessionsEl = document.getElementById('active-sessions');
        
        if (totalRxEl) {
            totalRxEl.textContent = data.total_rx_mbps.toFixed(2) + ' Mbps';
        }
        
        if (totalTxEl) {
            totalTxEl.textContent = data.total_tx_mbps.toFixed(2) + ' Mbps';
        }
        
        if (activeSessionsEl) {
            activeSessionsEl.textContent = data.active_sessions;
        }
    }

    /**
     * Show congestion indicator based on status
     * Requirements: 3.6, 3.7
     */
    showCongestionIndicator(data) {
        const rxIndicator = document.getElementById('rx-congestion-indicator');
        const txIndicator = document.getElementById('tx-congestion-indicator');
        
        if (rxIndicator) {
            rxIndicator.className = 'congestion-indicator';
            rxIndicator.classList.add('status-' + data.rx_congestion_status);
            rxIndicator.textContent = this.getStatusLabel(data.rx_congestion_status);
        }
        
        if (txIndicator) {
            txIndicator.className = 'congestion-indicator';
            txIndicator.classList.add('status-' + data.tx_congestion_status);
            txIndicator.textContent = this.getStatusLabel(data.tx_congestion_status);
        }
    }

    /**
     * Get human-readable status label
     */
    getStatusLabel(status) {
        const labels = {
            'normal': 'Normal',
            'warning': 'Warning',
            'critical': 'Critical'
        };
        return labels[status] || status;
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        const loader = document.getElementById('bandwidth-loader');
        if (loader) loader.style.display = 'block';
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        const loader = document.getElementById('bandwidth-loader');
        if (loader) loader.style.display = 'none';
    }

    /**
     * Show error banner
     * Requirements: 6.1, 6.4, 7.5
     */
    showError(message) {
        const errorBanner = document.getElementById('bandwidth-error');
        if (errorBanner) {
            errorBanner.textContent = message;
            errorBanner.style.display = 'block';
        }
    }

    /**
     * Hide error banner
     */
    hideError() {
        const errorBanner = document.getElementById('bandwidth-error');
        if (errorBanner) {
            errorBanner.style.display = 'none';
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BandwidthMonitor;
}
