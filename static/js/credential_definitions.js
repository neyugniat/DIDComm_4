// DOM elements
const toastMessage = document.getElementById('toast-message');
const toastClose = document.getElementById('toast-close');
const errorMessage = document.getElementById('error-message');
const createCredDefBtn = document.getElementById('createCredDef');
const credDefSchemaId = document.getElementById('cred-def-schema-id');
const credDefTag = document.getElementById('cred-def-tag');
const credDefSupportRevocation = document.getElementById('cred-def-support-revocation');
const schemaDetails = document.getElementById('schema-details');
const schemaName = document.getElementById('schema-name');
const schemaVersion = document.getElementById('schema-version');
const schemaAttributes = document.getElementById('schema-attributes');

// Handle toast close
toastClose.addEventListener('click', () => {
    toastMessage.classList.add('hidden');
});

// Fetch schema IDs and populate the dropdown
async function populateSchemaDropdown() {
    try {
        const response = await fetch('/schemas/issuer');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const schemas = await response.json();
        schemas.forEach(schema => {
            const option = document.createElement('option');
            option.value = schema.schema_id;
            option.textContent = schema.schema_id;
            credDefSchemaId.appendChild(option);
        });
    } catch (error) {
        errorMessage.textContent = `Error fetching schemas: ${error.message}`;
        errorMessage.classList.remove('hidden');
        showToast(`Error fetching schemas: ${error.message}`, true);
    }
}

// Fetch schema details when a schema is selected
credDefSchemaId.addEventListener('change', async () => {
    const schemaId = credDefSchemaId.value;
    if (!schemaId) {
        schemaDetails.classList.add('hidden');
        return;
    }

    try {
        const response = await fetch(`/schemas/issuer/${schemaId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const schema = data.schema;

        // Populate schema details
        schemaName.textContent = schema.name;
        schemaVersion.textContent = schema.version;
        schemaAttributes.textContent = schema.attrNames.join(', ');
        schemaDetails.classList.remove('hidden');
    } catch (error) {
        errorMessage.textContent = `Error fetching schema details: ${error.message}`;
        errorMessage.classList.remove('hidden');
        showToast(`Error fetching schema details: ${error.message}`, true);
        schemaDetails.classList.add('hidden');
    }
});

// Call the function to populate the dropdown when the page loads
document.addEventListener('DOMContentLoaded', populateSchemaDropdown);

// Create Credential Definition
createCredDefBtn.addEventListener('click', async () => {
    try {
        const schemaId = credDefSchemaId.value;
        const tag = credDefTag.value.trim() || undefined;
        const supportRevocation = credDefSupportRevocation.checked;

        if (!schemaId) {
            throw new Error('Please select a Schema ID');
        }

        const response = await fetch('/credential-definitions/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                schema_id: schemaId,
                support_revocation: supportRevocation,
                tag: tag
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showToast(`Credential Definition created! CredDef ID: ${data.credential_definition_id}`);
        errorMessage.classList.add('hidden');
        // Clear input fields
        credDefSchemaId.value = '';
        credDefTag.value = '';
        credDefSupportRevocation.checked = false;
        schemaDetails.classList.add('hidden');
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