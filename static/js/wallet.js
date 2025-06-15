document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('credential-modal');
    const viewButton = document.getElementById('view-credentials');
    const closeButton = document.getElementById('close-modal');
    const loadingDiv = document.getElementById('wallet-loading');
    const errorDiv = document.getElementById('wallet-error');
    const credentialList = document.getElementById('credential-list');

    function createToast(message, type = 'error') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `p-4 rounded-lg shadow-lg max-w-lg transition-opacity duration-300 ${
            type === 'error' ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'
        }`;
        toast.textContent = message;
        toast.style.opacity = '0';
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
        }, 100);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    async function fetchWalletCredentials() {
        loadingDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        credentialList.innerHTML = '';

        try {
            const response = await fetch('/wallet/credentials');
            if (!response.ok) throw new Error(`Failed to fetch wallet credentials: ${response.statusText}`);
            const data = await response.json();
            const credentials = data.results || [];

            if (credentials.length === 0) {
                errorDiv.textContent = 'No credentials found in wallet';
                errorDiv.classList.remove('hidden');
                return;
            }

            for (const cred of credentials) {
                let isRevoked = false;
                try {
                    // Check revocation status
                    const revokeResponse = await fetch(`/wallet/credential/revoked/${encodeURIComponent(cred.referent)}`);
                    if (!revokeResponse.ok) {
                        throw new Error(`Failed to fetch revocation status: ${revokeResponse.statusText}`);
                    }
                    const revokeData = await revokeResponse.json();
                    isRevoked = revokeData.revoked || false;
                } catch (error) {
                    console.error(`Error checking revocation status for credential ${cred.referent}:`, error);
                    // Assume not revoked if check fails to avoid blocking display
                }

                const credDiv = document.createElement('div');
                credDiv.className = `border border-gray-300 rounded-lg p-4 mb-4 ${
                    isRevoked ? 'bg-gray-100 opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-gray-50'
                }`;
                const attrs = Object.entries(cred.attrs)
                    .map(([key, value]) => `<p class="text-gray-700"><strong>${key}:</strong> ${value}</p>`)
                    .join('');
                credDiv.innerHTML = `
                    <h3 class="text-md font-semibold text-indigo-800 mb-2">${cred.schema_id} ${isRevoked ? '<span class="text-red-600 text-sm">(Revoked)</span>' : ''}</h3>
                    ${attrs}
                    <p class="text-gray-700 mt-2"><strong>Credential Definition ID:</strong> <span class="text-gray-600">${cred.cred_def_id}</span></p>
                `;
                if (!isRevoked) {
                    credDiv.addEventListener('click', () => {
                        window.location.href = `/credential/${encodeURIComponent(cred.referent)}`;
                    });
                }
                credentialList.appendChild(credDiv);
            }
        } catch (error) {
            console.error('Error fetching wallet credentials:', error);
            errorDiv.textContent = `Failed to load wallet: ${error.message}`;
            errorDiv.classList.add('hidden');
            createToast(`Failed to load wallet: ${error.message}`, 'error');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    }

    viewButton.addEventListener('click', () => {
        modal.classList.remove('hidden');
        fetchWalletCredentials();
    });

    closeButton.addEventListener('click', () => {
        modal.classList.add('hidden');
        credentialList.innerHTML = '';
    });

    // Close modal on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
            credentialList.innerHTML = '';
        }
    });
});