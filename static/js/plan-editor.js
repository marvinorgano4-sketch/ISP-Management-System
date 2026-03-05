/**
 * Inline Plan Editor Component
 * 
 * Allows inline editing of client plan name and amount.
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
 */

class InlinePlanEditor {
    constructor(clientId, fieldName, currentValue) {
        this.clientId = clientId;
        this.fieldName = fieldName; // 'plan_name' or 'plan_amount'
        this.currentValue = currentValue;
        this.originalValue = currentValue;
        this.isEditing = false;
    }

    /**
     * Activate edit mode
     * Requirements: 1.1
     */
    activate(cellElement) {
        if (this.isEditing) return;
        
        this.isEditing = true;
        this.cellElement = cellElement;
        
        // Store original HTML
        this.originalHTML = cellElement.innerHTML;
        
        // Create input field
        const inputType = this.fieldName === 'plan_amount' ? 'number' : 'text';
        const input = document.createElement('input');
        input.type = inputType;
        input.value = this.currentValue;
        input.className = 'inline-edit-input';
        
        if (this.fieldName === 'plan_amount') {
            input.step = '0.01';
            input.min = '0';
        }
        
        // Create buttons
        const saveBtn = document.createElement('button');
        saveBtn.textContent = '✓';
        saveBtn.className = 'inline-edit-btn save-btn';
        saveBtn.onclick = () => this.save();
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = '✗';
        cancelBtn.className = 'inline-edit-btn cancel-btn';
        cancelBtn.onclick = () => this.cancel();
        
        // Create container
        const container = document.createElement('div');
        container.className = 'inline-edit-container';
        container.appendChild(input);
        container.appendChild(saveBtn);
        container.appendChild(cancelBtn);
        
        // Replace cell content
        cellElement.innerHTML = '';
        cellElement.appendChild(container);
        
        // Focus on input
        input.focus();
        input.select();
        
        // Handle Enter key
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.save();
            }
        });
        
        // Handle Escape key
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.cancel();
            }
        });
    }

    /**
     * Validate input
     * Requirements: 1.3
     */
    validate(value) {
        if (this.fieldName === 'plan_name') {
            if (!value || value.trim() === '') {
                return { valid: false, error: 'Plan name cannot be empty' };
            }
            if (value.length > 100) {
                return { valid: false, error: 'Plan name must be 100 characters or less' };
            }
        } else if (this.fieldName === 'plan_amount') {
            const amount = parseFloat(value);
            if (isNaN(amount) || amount <= 0) {
                return { valid: false, error: 'Plan amount must be a positive number' };
            }
        }
        
        return { valid: true };
    }

    /**
     * Save changes
     * Requirements: 1.2, 1.4
     */
    async save() {
        const input = this.cellElement.querySelector('.inline-edit-input');
        const newValue = input.value;
        
        // Validate
        const validation = this.validate(newValue);
        if (!validation.valid) {
            this.showError(validation.error);
            return;
        }
        
        // Show loading
        input.disabled = true;
        
        try {
            // Get current plan data
            const row = this.cellElement.closest('tr');
            const planNameCell = row.querySelector('.plan-name');
            const planAmountCell = row.querySelector('.plan-amount');
            
            const currentPlanName = planNameCell ? planNameCell.textContent.trim() : '';
            const currentPlanAmount = planAmountCell ? parseFloat(planAmountCell.textContent.replace(/[^0-9.]/g, '')) : 0;
            
            // Prepare update data
            const updateData = {
                plan_name: this.fieldName === 'plan_name' ? newValue : currentPlanName,
                plan_amount: this.fieldName === 'plan_amount' ? parseFloat(newValue) : currentPlanAmount
            };
            
            // Send PATCH request
            const response = await fetch(`/clients/${this.clientId}/plan`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updateData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update display
                this.currentValue = newValue;
                this.cellElement.innerHTML = this.formatValue(newValue);
                this.isEditing = false;
                this.showSuccess('Plan updated successfully');
            } else {
                this.showError(result.error || 'Failed to update plan');
                input.disabled = false;
            }
        } catch (error) {
            this.showError('Connection error: ' + error.message);
            input.disabled = false;
        }
    }

    /**
     * Cancel editing
     * Requirements: 1.5
     */
    cancel() {
        this.cellElement.innerHTML = this.originalHTML;
        this.isEditing = false;
    }

    /**
     * Format value for display
     */
    formatValue(value) {
        if (this.fieldName === 'plan_amount') {
            return '₱' + parseFloat(value).toFixed(2);
        }
        return value;
    }

    /**
     * Show error message
     * Requirements: 6.2, 6.5
     */
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'inline-edit-error';
        errorDiv.textContent = message;
        
        const container = this.cellElement.querySelector('.inline-edit-container');
        if (container) {
            // Remove existing error
            const existingError = container.querySelector('.inline-edit-error');
            if (existingError) {
                existingError.remove();
            }
            
            container.appendChild(errorDiv);
        }
    }

    /**
     * Show success message
     * Requirements: 1.4
     */
    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'inline-edit-success';
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
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InlinePlanEditor;
}
