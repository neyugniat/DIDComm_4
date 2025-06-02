document.addEventListener('DOMContentLoaded', () => {
    async function fetchCredentialDefinitionsAndSchemas() {
        try {
            // Fetch credential definitions
            const credDefResponse = await fetch('/credential-definitions/issuer');
            if (!credDefResponse.ok) throw new Error(`Failed to fetch credential definitions: ${credDefResponse.statusText}`);
            const credDefs = await credDefResponse.json();
            if (!credDefs.length) throw new Error('No credential definitions found');

            const schemas = [];
            for (const credDef of credDefs) {
                const credDefId = credDef.credential_definition_id;
                const credDefDetailsResponse = await fetch(`/credential-definitions/issuer/${encodeURIComponent(credDefId)}`);
                if (!credDefDetailsResponse.ok) {
                    console.warn(`Failed to fetch details for cred_def ${credDefId}: ${credDefDetailsResponse.statusText}`);
                    continue;
                }
                const credDefDetails = await credDefDetailsResponse.json();
                const schemaId = credDefDetails.credential_definition?.schemaId;
                if (!schemaId) {
                    console.warn(`No schemaId found for cred_def ${credDefId}`);
                    continue;
                }

                // Fetch schema details using schemaId as seqNo
                const schemaResponse = await fetch(`/schemas/issuer/${schemaId}`);
                if (!schemaResponse.ok) {
                    console.warn(`Failed to fetch schema for schemaId ${schemaId}: ${schemaResponse.statusText}`);
                    continue;
                }
                const schemaDetails = await schemaResponse.json();
                const schema = schemaDetails.schema;
                if (schema) {
                    schemas.push({ schema, credDefId });
                }
            }

            // Populate dropdown
            const select = document.getElementById('schema-select');
            if (!select) {
                console.error('Schema select element not found');
                showError('Internal error: Schema select element missing');
                return [];
            }
            select.innerHTML = '<option value="">Select a schema</option>';
            schemas.forEach(item => {
                const option = document.createElement('option');
                option.value = JSON.stringify({
                    schemaId: item.schema.id,
                    credDefId: item.credDefId,
                    name: item.schema.name,
                    version: item.schema.version,
                    attrNames: item.schema.attrNames,
                    seqNo: item.schema.seqNo
                });
                option.textContent = `${item.schema.name} (v${item.schema.version})`;
                select.appendChild(option);
            });
            return schemas;
        } catch (error) {
            console.error('Error fetching credential definitions and schemas:', error);
            showError(`Failed to load schemas: ${error.message}`);
            return [];
        }
    }

    function createAttributeInputs(attrNames) {
        const container = document.getElementById('attribute-inputs');
        if (!container) {
            console.error('Attribute inputs container not found');
            return;
        }
        container.innerHTML = '';
        attrNames.forEach(attr => {
            const div = document.createElement('div');
            div.className = 'mb-2';
            div.innerHTML = `
                <label class="block text-sm font-medium text-gray-700">${attr}</label>
                <input type="text" data-attr="${attr}" class="w-full p-2 border border-gray-300 rounded-lg" placeholder="Enter ${attr} value" required>
            `;
            container.appendChild(div);
        });
    }

    function displaySchemaDetails(item) {
        const detailsDiv = document.getElementById('schema-details');
        const errorDiv = document.getElementById('error-message');
        const successDiv = document.getElementById('success-message');
        const issueButton = document.getElementById('issue-credential');
        const schemaId = document.getElementById('schema-id');
        const schemaName = document.getElementById('schema-name');
        const schemaVersion = document.getElementById('schema-version');
        const schemaAttributes = document.getElementById('schema-attributes');
        const schemaSeq = document.getElementById('schema-seq');
        const credDefId = document.getElementById('cred-def-id');

        if (!detailsDiv || !errorDiv || !successDiv || !issueButton || !schemaId || !schemaName || !schemaVersion || !schemaAttributes || !schemaSeq || !credDefId) {
            console.error('One or more DOM elements are missing in schema-details');
            showError('Internal error: Page elements not found');
            return;
        }

        detailsDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        successDiv.classList.add('hidden');
        issueButton.classList.remove('hidden');

        schemaId.textContent = item.schemaId || 'N/A';
        schemaName.textContent = item.name || 'N/A';
        schemaVersion.textContent = item.version || 'N/A';
        schemaAttributes.textContent = (item.attrNames && Array.isArray(item.attrNames)) ? item.attrNames.join(', ') : 'None';
        schemaSeq.textContent = item.seqNo != null ? item.seqNo : 'N/A';
        credDefId.textContent = item.credDefId || 'None';

        createAttributeInputs(item.attrNames || []);
    }

    function showError(message) {
        const errorDiv = document.getElementById('error-message');
        const successDiv = document.getElementById('success-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
        if (successDiv) {
            successDiv.classList.add('hidden');
        }
        const detailsDiv = document.getElementById('schema-details');
        const issueButton = document.getElementById('issue-credential');
        const inputsContainer = document.getElementById('attribute-inputs');
        if (detailsDiv) detailsDiv.classList.add('hidden');
        if (issueButton) issueButton.classList.add('hidden');
        if (inputsContainer) inputsContainer.innerHTML = '';
    }

    function showSuccess(message) {
        const successDiv = document.getElementById('success-message');
        const errorDiv = document.getElementById('error-message');
        if (successDiv) {
            successDiv.textContent = message;
            successDiv.classList.remove('hidden');
        }
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
        const detailsDiv = document.getElementById('schema-details');
        const issueButton = document.getElementById('issue-credential');
        if (detailsDiv) detailsDiv.classList.remove('hidden');
        if (issueButton) issueButton.classList.remove('hidden');
    }

    async function pollCredentialState(cred_ex_id) {
        const maxAttempts = 30;
        const intervalMs = 1000;
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                const response = await fetch(`/issue-credentials/fetch_record/HOLDER/${cred_ex_id}`);
                if (!response.ok) {
                    if (response.status === 404) {
                        await new Promise(resolve => setTimeout(resolve, intervalMs));
                        continue;
                    }
                    throw new Error(`Failed to check credential state: ${response.statusText}`);
                }
                const result = await response.json();
                if (result.cred_ex_record.state === 'done') {
                    return result.cred_ex_record;
                }
                await new Promise(resolve => setTimeout(resolve, intervalMs));
            } catch (error) {
                console.error('Error polling credential state:', error);
                await new Promise(resolve => setTimeout(resolve, intervalMs));
            }
        }
        throw new Error('Credential issuance timed out');
    }

    async function requestCredentialIssuance(schemaId, credDefId, attributes) {
        try {
            const response = await fetch('/issue-credentials/proposal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ schemaId, credDefId, attributes })
            });
            if (!response.ok) throw new Error(`Failed to send proposal: ${response.statusText}`);
            const result = await response.json();
            const cred_ex_id = result.result.cred_ex_id;
            if (!cred_ex_id) throw new Error('No cred_ex_id in proposal response');

            showSuccess('Credential proposal sent, awaiting issuance...');
            const finalState = await pollCredentialState(cred_ex_id);
            showSuccess(`Credential issued and stored successfully: cred_ex_id=${finalState.cred_ex_id}`);
        } catch (error) {
            console.error('Error requesting issuance:', error);
            showError(`Failed to issue credential: ${error.message}`);
        }
    }

    document.getElementById('schema-select').addEventListener('change', async (event) => {
        const value = event.target.value;
        if (value) {
            try {
                const item = JSON.parse(value);
                if (!item || typeof item !== 'object') {
                    throw new Error('Parsed item is not a valid object');
                }
                displaySchemaDetails(item);
            } catch (error) {
                console.error('Error parsing selection:', error, { value });
                showError(`Failed to parse selection: ${error.message}`);
            }
        } else {
            document.getElementById('schema-details')?.classList.add('hidden');
            document.getElementById('error-message')?.classList.add('hidden');
            document.getElementById('success-message')?.classList.add('hidden');
            document.getElementById('issue-credential')?.classList.add('hidden');
            document.getElementById('attribute-inputs').innerHTML = '';
        }
    });

    document.getElementById('issue-credential').addEventListener('click', () => {
        const select = document.getElementById('schema-select');
        const value = select.value;
        if (value) {
            try {
                const item = JSON.parse(value);
                const credDefId = item.credDefId;
                if (credDefId && credDefId !== 'None') {
                    const inputs = document.querySelectorAll('#attribute-inputs input');
                    const attributes = Array.from(inputs).map(input => ({
                        name: input.getAttribute('data-attr'),
                        value: input.value.trim()
                    })).filter(attr => attr.value);
                    if (attributes.length !== (item.attrNames || []).length) {
                        showError('Please provide values for all attributes');
                        return;
                    }
                    requestCredentialIssuance(item.schemaId, credDefId, attributes);
                } else {
                    showError('No valid credential definition selected');
                }
            } catch (error) {
                console.error('Error processing selection:', error, { value });
                showError(`Failed to process selection: ${error.message}`);
            }
        }
    });

    fetchCredentialDefinitionsAndSchemas();
});