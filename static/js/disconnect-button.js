/**
 * Disconnect Button Component
 * 
 * Handles client PPPoE session disconnection with confirmation.
 * Requirements: 4.1, 4.3, 4.4, 4.5, 4.6, 4.8
 */

class DisconnectButton {
    constructor(clientId, clientName) {
        this.clientId = clientId;
        this.clientName = clientName;
    }

    /**
     * Show confirmation dialog
     * Requirements: 4.3
     */
    showConfirmation() {
        return confirm(
            `Are you sure you want to disconnect ${this.clientName}?\n\n` +
            `This will terminate their active PPPoE session.`
        );
    }

    /**
     * Disconnect client session
     * Requirements: 4.4, 4.5
     */
    async disconnect(buttonElement) {
        // Show confirmation first
        if (!this.showConfirmation()) {
            return;
        }
        
        // Disable button during request
        buttonElement.disabled = true;
        buttonElement.textContent = 'Disconnecting...';
        
        try {
            const response = await fetch(`/clients/${this.clientId}/disconnect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update client status display
                this.updateClientStatus(buttonElement);
                this.showSuccess(result.message || 'Client disconnected successfully');
            } else {
                // Show error
                this.showError(result.error || 'Failed to disconnect client');
                // Re-enable button
                buttonElement.disabled = false;
                buttonElement.textContent = 'Disconnect';
            }
        } catch (error) {
            this.showError('Connection error: ' + error.message);
            // Re-enable button
            buttonElement.disabled = false;
            buttonElement.textContent = 'Disconnect';
        }
    }

    /**
     * Update client status display after disconnect
     * Requirements: 4.8
     */
    updateClientStatus(buttonElement) {
        const row = buttonElement.closest('tr');
        if (!row) return;
        
        // Hide disconnect button
        buttonElement.style.display = 'none';
        
        // Update bandwidth display to "Offline"
        const rxCell = row.querySelector('.bandwidth-rx');
        const txCell = row.querySelector('.bandwidth-tx');
        const statusCell = row.querySelector('.connection-status');
        
        if (rxCell) rxCell.textContent = 'Offline';
        if (txCell) txCell.textContent = 'Offline';
        if (statusCell) {
            statusCell.textContent = 'Offline';
            statusCell.className = 'connection-status status-offline';
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'disconnect-success';
        successDiv.textContent = message;
        successDiv.style.position = 'fixed';
        successDiv.style.top = '20px';
        successDiv.style.right = '20px';
        successDiv.style.padding = '10px 20px';
        successDiv.style.backgroundColor = '#4CAF50';
        successDiv.style.color = 'white';
        successDiv.style.borderRadius = '4px';
        successDiv.style.zIndex = '9999';
        
        document.body.appendChild(successDiv);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    /**
     * Show error message
     * Requirements: 4.6, 6.3
     */
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'disconnect-error';
        errorDiv.textContent = message;
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '20px';
        errorDiv.style.right = '20px';
        errorDiv.style.padding = '10px 20px';
        errorDiv.style.backgroundColor = '#f44336';
        errorDiv.style.color = 'white';
        errorDiv.style.borderRadius = '4px';
        errorDiv.style.zIndex = '9999';
        
        document.body.appendChild(errorDiv);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DisconnectButton;
}
