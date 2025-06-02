document.addEventListener('DOMContentLoaded', () => {
    const requestAutoButton = document.getElementById('request-presentation');
    const successDiv = document.getElementById('success-message');
    const errorDiv = document.getElementById('generic-error');

    function createToast(content, type = 'error') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `p-4 rounded-lg shadow-lg max-w-lg transition-opacity duration-300 ${
            type === 'error' ? 'bg-red-100 text-red-500' : 'bg-green-600 text-white'
        }`;
        toast.textContent = content;
        toast.style.opacity = '0';
        container.appendChild(toast);
        setTimeout(() => toast.style.opacity = '1', 100);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.parentNode?.removeChild(toast), 300);
        }, 3000);
    }

    function showSuccess(message) {
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.classList.remove('hidden');
        }
        if (errorDiv) errorDiv.classList.add('hidden');
        createToast(message, 'success');
    }

    function showError(message) {
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
        if (successDiv) successDiv.classList.add('hidden');
        createToast(message, 'error');
    }

    function mapErrorMessage(error) {
        if (error.includes("No matching Indy credentials found")) {
            return "No valid credential found in your wallet.";
        }
        if (error.includes("Presentation exchange ID not found")) {
            return "The requested presentation exchange ID is invalid or not found.";
        }
        if (error.includes("Network error connecting to holder agent")) {
            return "Unable to connect to the credential service. Please try again later.";
        }
        if (error.includes("Timeout waiting for holder's pres_ex_id")) {
            return "Timed out waiting for the holder's response.";
        }
        if (error.includes("Presentation abandoned")) {
            return "The presentation request was abandoned.";
        }
        if (error.includes("Verification timeout")) {
            return "Timed out waiting for verification result.";
        }
        if (error.includes("Credential revoked")) {
            return "The selected credential has been revoked.";
        }
        return error || "An error occurred during verification.";
    }

    async function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function waitForVerification(thread_id, maxAttempts = 10, delayMs = 1000) {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                const response = await fetch(`/presentations/verify/${thread_id}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (!response.ok) {
                    if (response.status === 425) {
                        if (attempt === maxAttempts - 1) {
                            throw new Error('Verification timeout');
                        }
                        await delay(delayMs);
                        continue;
                    }
                    // Parse error response if available
                    let errorData;
                    try {
                        errorData = await response.json();
                    } catch (e) {
                        throw new Error(`Failed to verify presentation: HTTP ${response.status}`);
                    }
                    throw new Error(errorData.error || errorData.detail || `Failed to verify presentation: HTTP ${response.status}`);
                }

                const data = await response.json();
                if (data.status === 'verified') {
                    return 'verified';
                } else if (data.status === 'failed') {
                    throw new Error(data.error || data.detail || 'Presentation verification failed');
                }

                // If status is neither verified nor failed (e.g., pending), retry
                if (attempt === maxAttempts - 1) {
                    throw new Error('Verification timeout');
                }
                await delay(delayMs);

            } catch (error) {
                console.error(`Verification attempt ${attempt + 1} failed:`, error.message);
                throw error; // Re-throw to propagate to caller
            }
        }
    }

    async function requestPresentation() {
        try {
            // Send proof request
            const response = await fetch('/presentations/send-request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            if (!response.ok) throw new Error(`Failed to send proof request: ${response.statusText}`);
            const result = await response.json();
            // console.log('Presentation request response:', result);
            const thread_id = result.thread_id;
            // console.log('Thread ID:', thread_id);
            // console.log('Presentation request sent successfully');
            if (!thread_id) throw new Error('No thread_id in response');

            showSuccess('Presentation processing, awaiting verification...');

            const verificationStatus = await waitForVerification(thread_id);
            if (verificationStatus === 'verified') {
                showSuccess(`Presentation verified successfully: thread_id=${thread_id}`);
            }
        } catch (error) {
            console.error('Error requesting presentation:', error);
            showError(mapErrorMessage(error.message));
        }
    }

    requestAutoButton.addEventListener('click', requestPresentation);
});