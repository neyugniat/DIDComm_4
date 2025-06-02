document.addEventListener('DOMContentLoaded', () => {
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

    async function fetchCredentialDetails() {
        const referent = decodeURIComponent(window.location.pathname.split('/').pop());
        const loadingDiv = document.getElementById('loading');
        const errorDiv = document.getElementById('error-message');
        const detailsDiv = document.getElementById('credential-details');

        const referentSpan = document.getElementById('credential-referent');
        const schemaIdSpan = document.getElementById('credential-schema-id');
        const credDefIdSpan = document.getElementById('credential-cred-def-id');
        const attributesTableBody = document.getElementById('credential-attributes-table');

        if (!detailsDiv || !errorDiv || !loadingDiv || !referentSpan || !schemaIdSpan || !credDefIdSpan || !attributesTableBody) {
            console.error('One or more DOM elements are missing');
            createToast('Internal error: Page elements not found', 'error');
            return;
        }

        loadingDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        detailsDiv.classList.add('hidden');

        try {
            const response = await fetch(`/wallet/credential/${encodeURIComponent(referent)}`);
            if (!response.ok) throw new Error(`Failed to fetch credential: ${response.statusText}`);
            const credential = await response.json();

            referentSpan.textContent = credential.referent || 'N/A';
            schemaIdSpan.textContent = credential.schema_id || 'N/A';
            credDefIdSpan.textContent = credential.cred_def_id || 'N/A';

            // Render attributes table rows
            attributesTableBody.innerHTML = '';
            const attributes = credential.attrs || {};
            if (Object.keys(attributes).length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-4 py-2 border-b italic text-gray-500" colspan="2">No attributes available</td>
                `;
                attributesTableBody.appendChild(row);
            } else {
                for (const [key, value] of Object.entries(attributes)) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="px-4 py-2 border-b">${key}</td>
                        <td class="px-4 py-2 border-b">${value}</td>
                    `;
                    attributesTableBody.appendChild(row);
                }
            }

            detailsDiv.classList.remove('hidden');
        } catch (error) {
            console.error('Error fetching credential:', error);
            errorDiv.textContent = `Failed to load credential: ${error.message}`;
            errorDiv.classList.remove('hidden');
            createToast(`Failed to load credential: ${error.message}`, 'error');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    }

    fetchCredentialDetails();
});
