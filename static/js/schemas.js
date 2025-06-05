// DOM elements
const toastMessage = document.getElementById('toast-message');
const toastClose = document.getElementById('toast-close');
const errorMessage = document.getElementById('error-message');
const createCanCuocCongDanBtn = document.getElementById('createCanCuocCongDan');
const createBangTotNghiepBtn = document.getElementById('createBangTotNghiep');
const createCustomSchemaBtn = document.getElementById('createCustomSchema');
const customSchemaName = document.getElementById('custom-schema-name');
const customSchemaVersion = document.getElementById('custom-schema-version');
const customSchemaAttributes = document.getElementById('custom-schema-attributes');

// Handle toast close
toastClose.addEventListener('click', () => {
    toastMessage.classList.add('hidden');
});

// Create Can_Cuoc_Cong_Dan Schema
createCanCuocCongDanBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/schemas/issuer/create-can-cuoc-cong-dan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast(`Can_Cuoc_Cong_Dan schema created! Schema ID: ${data.schema_id}`);
        errorMessage.classList.add('hidden');
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.classList.remove('hidden');
        showToast(`Error: ${error.message}`, true);
    }
});

// Create Bang_tot_nghiep Schema
createBangTotNghiepBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/schemas/issuer/create-bang-tot-nghiep', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast(`Bang_tot_nghiep schema created! Schema ID: ${data.schema_id}`);
        errorMessage.classList.add('hidden');
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.classList.remove('hidden');
        showToast(`Error: ${error.message}`, true);
    }
});

// Create Custom Schema
createCustomSchemaBtn.addEventListener('click', async () => {
    try {
        const schemaName = customSchemaName.value.trim();
        const schemaVersion = customSchemaVersion.value.trim();
        const attributes = customSchemaAttributes.value
            .split(',')
            .map(attr => attr.trim())
            .filter(attr => attr.length > 0);

        if (!schemaName || !schemaVersion || attributes.length === 0) {
            throw new Error('Please fill in all fields with valid values');
        }

        const response = await fetch('/schemas/issuer/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                schema_name: schemaName,
                schema_version: schemaVersion,
                attributes: attributes
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast(`Custom schema created! Schema ID: ${data.schema_id}`);
        errorMessage.classList.add('hidden');
        // Clear input fields
        customSchemaName.value = '';
        customSchemaVersion.value = '';
        customSchemaAttributes.value = '';
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.classList.remove('hidden');
        showToast(`Error: ${error.message}`, true);
    }
});

// Utility function to show toast notification
function showToast(message, isError = false) {
    toastMessage.classList.remove('hidden');
    toastMessage.firstElementChild.textContent = message;
    if (isError) {
        toastMessage.style.backgroundColor = '#fee2e2';
        toastMessage.style.color = '#991b1b';
        toastMessage.style.borderColor = '#f87171';
        toastMessage.firstElementChild.style.color = '#f87171';
    } else {
        toastMessage.style.backgroundColor = '#d1fae5';
        toastMessage.style.color = '#065f46';
        toastMessage.style.borderColor = '#10b981';
        toastMessage.firstElementChild.style.color = '#10b981';
    }

    setTimeout(() => {
        toastMessage.classList.add('hidden');
    }, 5000);
}