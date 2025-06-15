document.addEventListener('DOMContentLoaded', () => {
    populateConnectionDropdown();
    populateCredRevDropdown();
});

// DOM elements
const toastMessage = document.getElementById('toast-message');
const toastClose = document.getElementById('toast-close');
const errorMessage = document.getElementById('error-message');
const connectionIdSelect = document.getElementById('connection-id');
const credRevIdSelect = document.getElementById('cred-rev-id');
const commentInput = document.getElementById('comment');
const revokeCredentialBtn = document.getElementById('revokeCredential');

// Handle toast close
toastClose.addEventListener('click', () => {
    toastMessage.classList.add('hidden');
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

// Fetch Connections and populate the dropdown
async function populateConnectionDropdown() {
  try {
    const response = await fetch('/connections/issuer');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const connections = data.results;

    connections.forEach(conn => {
      const option = document.createElement('option');
      option.value = conn.connection_id;
      option.textContent = `${conn.their_label} (${conn.connection_id})`;
      connectionIdSelect.appendChild(option);
    });
  } catch (error) {
    errorMessage.textContent = `Error fetching connections: ${error.message}`;
    errorMessage.classList.remove('hidden');
    showToast(`Error fetching connections: ${error.message}`, true);
  }
}

// Fetch Issued Credentials and populate the credential dropdown
async function populateCredRevDropdown() {
    credRevIdSelect.innerHTML = '<option value="">Select a credential</option>'; // Clear previous options
    try {
        const response = await fetch('/revocation/issued-credentials');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const credentials = await response.json();
        // Filter only credentials with state: "issued"
        const issuedCredentials = credentials.filter(cred => cred.state === "issued");
        if (issuedCredentials.length === 0) {
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "No credentials issued";
            option.disabled = true;
            credRevIdSelect.appendChild(option);
        } else {
            for (const cred of issuedCredentials) {
                try {
                    // Fetch credential definition details to get schemaId
                    const credDefResponse = await fetch(`/credential-definitions/issuer/${encodeURIComponent(cred.cred_def_id)}`);
                    if (!credDefResponse.ok) {
                        throw new Error(`HTTP error fetching cred def details! status: ${credDefResponse.status}`);
                    }
                    const credDefData = await credDefResponse.json();
                    const schemaId = credDefData.credential_definition.schemaId;

                    // Fetch schema details to get schema_name
                    const schemaResponse = await fetch(`/schemas/issuer/${schemaId}`);
                    if (!schemaResponse.ok) {
                        throw new Error(`HTTP error fetching schema! status: ${schemaResponse.status}`);
                    }
                    const schemaData = await schemaResponse.json();
                    const schemaName = schemaData.schema.name;

                    // Create dropdown option
                    const option = document.createElement('option');
                    option.value = cred.cred_rev_id;
                    option.textContent = `${schemaName} (Issued: ${cred.created_at})`;
                    option.dataset.revRegId = cred.rev_reg_id;
                    credRevIdSelect.appendChild(option);
                } catch (error) {
                    // Log error and skip this credential
                    console.error(`Error processing credential ${cred.cred_rev_id}: ${error.message}`);
                    continue;
                }
            }
        }
    } catch (error) {
        errorMessage.textContent = `Error fetching issued credentials: ${error.message}`;
        errorMessage.classList.remove('hidden');
        showToast(`Error fetching issued credentials: ${error.message}`, true);
    }
}

// Revoke Credential
revokeCredentialBtn.addEventListener('click', async () => {
    try {
        const connectionId = connectionIdSelect.value;
        const credRevId = credRevIdSelect.value;
        const selectedOption = credRevIdSelect.options[credRevIdSelect.selectedIndex];
        const revRegId = selectedOption.dataset.revRegId;
        const comment = commentInput.value.trim();

        if (!connectionId || !credRevId || !revRegId) {
            throw new Error('Please select a connection and credential');
        }

        const requestData = {
            connection_id: connectionId,
            comment: comment || 'Revoking credential',
            cred_rev_id: credRevId,
            rev_reg_id: revRegId,
            notify: true,
            publish: true
        };

        const response = await fetch('/revocation/revoke', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast(`Credential revoked successfully!`);
        errorMessage.classList.add('hidden');

        // Reset form
        connectionIdSelect.value = '';
        credRevIdSelect.innerHTML = '<option value="">Select a credential</option>';
        commentInput.value = '';
        // Refresh credential dropdown
        populateCredRevDropdown();
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.classList.remove('hidden');
        showToast(`Error: ${error.message}`, true);
    }
});