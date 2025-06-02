async function testApi(endpoint, vpJwtInputId, resultDivId, successMessage) {
    try {
        const vpJwt = document.getElementById(vpJwtInputId).value.trim();
        if (!vpJwt) {
            throw new Error('Please paste a valid VP-JWT');
        }

        // Call API
        const apiResponse = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jwt: vpJwt })
        });
        if (!apiResponse.ok) {
            const errorData = await apiResponse.json();
            if (apiResponse.status === 422 && errorData.detail === "This API requires a VP-JWT in the request body.") {
                throw new Error(errorData.detail);
            }
            throw new Error(`Failed to call ${endpoint}: ${errorData.detail || await apiResponse.text()}`);
        }
        const apiData = await apiResponse.json();
        console.log(`${successMessage}:`, apiData);
        createToast(successMessage, 'success');

        const apiResult = document.getElementById(resultDivId);
        apiResult.querySelector('pre').textContent = JSON.stringify(apiData, null, 2);
        apiResult.classList.remove('hidden');
    } catch (error) {
        console.error(`Error testing ${endpoint}:`, error);
        createToast(error.message, 'error');
        showError(error.message);
    }
}

function showError(message) {
    const errorDiv = document.getElementById('generic-error');
    errorDiv.textContent = `Error: ${message}`;
    errorDiv.classList.remove('hidden');
}

function createToast(message, type) {
    console.log(`Toast: ${message} (${type})`);
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 p-4 rounded text-white ${
        type === 'success' ? 'bg-green-600' : 'bg-red-600'
    }`;
    toast.textContent = message;
    const toastContainer = document.getElementById('toast-container');
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Event listeners
document.getElementById('test-api').addEventListener('click', () => 
    testApi('/api/get-book-list', 'vp-jwt', 'api-result', 'Book list retrieved successfully')
);
document.getElementById('test-patient-api').addEventListener('click', () => 
    testApi('/api/get-patient-records', 'patient-vp-jwt', 'patient-api-result', 'Patient records retrieved successfully')
);