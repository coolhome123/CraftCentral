// Function to set up child forms based on selected count
function setupChildForms() {
    const childrenCountElement = document.getElementById('children_count');
    if (!childrenCountElement) return;
    
    const childrenCount = parseInt(childrenCountElement.value);
    const container = document.getElementById('childFormsContainer');
    if (!container) return;
    
    // Store existing values if any
    const existingValues = collectExistingValues();
    
    // Clear container
    container.innerHTML = '';
    
    // Generate forms for each child
    for (let i = 1; i <= childrenCount; i++) {
        const childForm = createChildForm(i, existingValues[i] || {});
        container.appendChild(childForm);
    }
    
    // Set up event listeners for all date of birth inputs
    setupDobListeners();
}

// Collect existing values from the form before regenerating
function collectExistingValues() {
    const values = {};
    const childForms = document.querySelectorAll('.child-form');
    
    childForms.forEach((form, index) => {
        const childNum = index + 1;
        values[childNum] = {
            name: document.getElementById(`child_${childNum}-name`)?.value || '',
            dob: document.getElementById(`child_${childNum}-date_of_birth`)?.value || '',
            maritalStatus: document.getElementById(`child_${childNum}-marital_status`)?.value || ''
        };
    });
    
    return values;
}

// Create a single child form
function createChildForm(index, existingValues = {}) {
    const div = document.createElement('div');
    div.id = `child_form_${index}`;
    div.className = 'child-form mb-4';
    
    div.innerHTML = `
        <div class="card">
            <div class="card-header bg-secondary">
                <h5 class="mb-0">Child ${index}</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label for="child_${index}-name" class="form-label">Name <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="child_${index}-name" name="child_${index}-name" 
                            value="${existingValues.name || ''}" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label for="child_${index}-date_of_birth" class="form-label">Date of Birth <span class="text-danger">*</span></label>
                        <input type="date" class="form-control dob-input" id="child_${index}-date_of_birth" 
                            name="child_${index}-date_of_birth" value="${existingValues.dob || ''}" required>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label for="child_${index}-age" class="form-label">Age</label>
                        <input type="text" class="form-control age-field" id="child_${index}-age" readonly>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="child_${index}-marital_status" class="form-label">Marital Status</label>
                        <select class="form-select" id="child_${index}-marital_status" name="child_${index}-marital_status">
                            <option value="" ${!existingValues.maritalStatus ? 'selected' : ''}>Select Status</option>
                            <option value="single" ${existingValues.maritalStatus === 'single' ? 'selected' : ''}>Single</option>
                            <option value="married" ${existingValues.maritalStatus === 'married' ? 'selected' : ''}>Married</option>
                            <option value="divorced" ${existingValues.maritalStatus === 'divorced' ? 'selected' : ''}>Divorced</option>
                            <option value="widowed" ${existingValues.maritalStatus === 'widowed' ? 'selected' : ''}>Widowed</option>
                            <option value="minor" ${existingValues.maritalStatus === 'minor' ? 'selected' : ''}>Minor (Not Applicable)</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return div;
}

// Set up event listeners for date of birth inputs
function setupDobListeners() {
    const dobInputs = document.querySelectorAll('.dob-input');
    
    dobInputs.forEach(input => {
        input.addEventListener('change', function() {
            calculateAge(this);
        });
        
        // Calculate age for existing values
        if (input.value) {
            calculateAge(input);
        }
    });
}

// Calculate age based on date of birth
function calculateAge(dobInput) {
    const dob = dobInput.value;
    if (!dob) return;
    
    const id = dobInput.id;
    const childIndex = id.split('-')[0];
    const ageField = document.getElementById(`${childIndex}-age`);
    
    if (!ageField) return; // Guard against null ageField
    
    // Calculate age client-side
    const birthDate = new Date(dob);
    const today = new Date();
    
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    ageField.value = age + ' years';
    
    // Optionally, if age is under 18, automatically set marital status to "minor"
    const maritalStatusField = document.getElementById(`${childIndex}-marital_status`);
    if (age < 18 && maritalStatusField) {
        maritalStatusField.value = 'minor';
    }
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('familyForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Highlight all invalid fields
                const invalidInputs = form.querySelectorAll(':invalid');
                invalidInputs.forEach(input => {
                    input.classList.add('is-invalid');
                    
                    // Remove invalid class when input changes
                    input.addEventListener('input', function() {
                        if (this.checkValidity()) {
                            this.classList.remove('is-invalid');
                        }
                    });
                });
                
                // Show validation message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
                alertDiv.setAttribute('role', 'alert');
                alertDiv.innerHTML = `
                    <strong>Error!</strong> Please check the form for errors and try again.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                
                // Add alert only if it doesn't already exist
                if (!document.querySelector('.alert-danger')) {
                    form.prepend(alertDiv);
                }
                
                // Scroll to the first invalid field
                if (invalidInputs.length > 0) {
                    invalidInputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Set up validation for phone number
        const phoneInput = document.getElementById('phone');
        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                const pattern = /^[0-9\-\+\(\) ]{10,15}$/;
                if (this.value && !pattern.test(this.value)) {
                    this.setCustomValidity('Please enter a valid phone number.');
                } else {
                    this.setCustomValidity('');
                }
            });
        }
    }
    
    // Initial setup for child forms
    setupChildForms();
});
