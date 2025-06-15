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

// Endpoint configurations
const endpointConfigs = {
    'book-list': {
        endpoint: '/api/get-book-list',
        vpJwtInputId: 'vp-jwt',
        resultDivId: 'api-result',
        successMessage: 'Book list retrieved successfully'
    },
    'patient-records': {
        endpoint: '/api/get-patient-records',
        vpJwtInputId: 'vp-jwt',
        resultDivId: 'api-result',
        successMessage: 'Patient records retrieved successfully'
    }
};

// Event listeners
document.getElementById('endpoint-select').addEventListener('change', () => {
    const endpointKey = document.getElementById('endpoint-select').value;
    const testButton = document.getElementById('test-api');
    testButton.disabled = !endpointKey;
    if (!endpointKey) {
        document.getElementById('api-result').classList.add('hidden');
    }
});

document.getElementById('test-api').addEventListener('click', () => {
    const endpointKey = document.getElementById('endpoint-select').value;
    if (!endpointKey) {
        createToast('Please select an endpoint', 'error');
        return;
    }
    const config = endpointConfigs[endpointKey];
    testApi(config.endpoint, config.vpJwtInputId, config.resultDivId, config.successMessage);
});