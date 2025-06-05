let holderPresExId = null;
let credentials = [];
let threadId = null;
let selectedSchema = null;

async function fetchSchemas() {
    try {
        const response = await fetch('/schemas/issuer', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        if (!response.headers.get('content-type').includes('application/json')) {
            throw new Error('Unexpected response format');
        }
        const data = await response.json();
        const schemaSelect = document.getElementById('schemaSelect');
        schemaSelect.innerHTML = '<option value="">Select a schema</option>';
        data.forEach(schema => {
            const option = document.createElement('option');
            option.value = schema.schema_id;
            option.textContent = schema.schema_id.split(':2:')[1] || schema.schema_id;
            schemaSelect.appendChild(option);
        });
    } catch (error) {
        document.getElementById('error-message').textContent = `Error fetching schemas: ${error.message}`;
        document.getElementById('error-message').classList.remove('hidden');
    }
}

async function fetchSchemaAttributes(schemaId) {
    try {
        const response = await fetch(`/schemas/issuer/${encodeURIComponent(schemaId)}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        if (!response.headers.get('content-type').includes('application/json')) {
            throw new Error('Unexpected response format');
        }
        const data = await response.json();
        return data.schema.attrNames;
    } catch (error) {
        throw new Error(`Failed to fetch schema attributes: ${error.message}`);
    }
}

async function fetchHolderConnections() {
    try {
        const response = await fetch('/connections/verifier', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        if (!response.headers.get('content-type').includes('application/json')) {
            throw new Error('Unexpected response format');
        }
        const data = await response.json();
        const select = document.getElementById('connectionSelect');
        select.innerHTML = '<option value="">Select a connection</option>';
        data.results.forEach(conn => {
            const option = document.createElement('option');
            option.value = conn.connection_id;
            option.textContent = `${conn.their_label || 'Unknown'} (ID: ${conn.connection_id})`;
            select.appendChild(option);
        });
    } catch (error) {
        document.getElementById('error-message').textContent = `Error fetching connections: ${error.message}`;
        document.getElementById('error-message').classList.remove('hidden');
    }
}

function calculateUnixDobInDays(yearsAgo) {
    const currentDate = new Date();
    const thresholdDate = new Date(currentDate);
    thresholdDate.setFullYear(currentDate.getFullYear() - yearsAgo);
    const msPerDay = 1000 * 60 * 60 * 24;
    const unixEpoch = new Date('1970-01-01T00:00:00Z');
    const daysSinceEpoch = Math.floor((thresholdDate - unixEpoch) / msPerDay);
    return daysSinceEpoch;
}

async function sendProofRequest() {
    const connectionId = document.getElementById('connectionSelect').value;
    const schemaId = document.getElementById('schemaSelect').value;
    const errorMessage = document.getElementById('error-message');
    const credentialSelect = document.getElementById('credentialSelect');
    const credentialDetails = document.getElementById('credentialDetails');
    const toastMessage = document.getElementById('toast-message');
    const credentialSelectContainer = document.getElementById('credentialSelectContainer');
    

    toastMessage.classList.add('hidden');
    errorMessage.classList.add('hidden');
    credentialSelect.innerHTML = '<option value="">Select a credential</option>';
    credentialDetails.innerHTML = '';
    credentialDetails.classList.add('hidden');
    holderPresExId = null;
    credentials = [];
    threadId = null;
    selectedSchema = null;

    if (!connectionId) {
        errorMessage.textContent = 'Please select a connection';
        errorMessage.classList.remove('hidden');
        return;
    }
    if (!schemaId) {
        errorMessage.textContent = 'Please select a schema';
        errorMessage.classList.remove('hidden');
        return;
    }

    try {
        const attributes = await fetchSchemaAttributes(schemaId);
        selectedSchema = { schema_id: schemaId, attributes };

        const requestedAttributes = {};
        attributes.forEach(attr => {
            requestedAttributes[`${attr}_attributes`] = {
                name: attr,
                restrictions: [{ schema_id: schemaId }]
            };
        });

        const presentationRequest = {
            indy: {
                name: `${schemaId.split(':2:')[1]} Verification`,
                version: "1.0",
                requested_attributes: requestedAttributes,
                requested_predicates: {},
                non_revoked: { from: 0, to: Math.floor(Date.now() / 1000) }
            }
        };

        if (attributes.includes('unixdob')) {
            const targetAge = 18;
            const unixDobValue = calculateUnixDobInDays(targetAge);
            presentationRequest.indy.requested_predicates['age_predicate'] = {
                name: 'unixdob',
                p_type: '<',
                p_value: unixDobValue,
                restrictions: [{ schema_id: schemaId }]
            };
        }

        const response = await fetch('/manual_presentations/verifier/send-request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                connection_id: connectionId,
                auto_verify: true,
                presentation_request: presentationRequest,
                auto_remove: false
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! Status: ${response.status} - ${errorText}`);
        }
        if (!response.headers.get('content-type').includes('application/json')) {
            throw new Error('Unexpected response format');
        }
        const data = await response.json();
        holderPresExId = data.holder_pres_ex_id;
        credentials = data.credentials || [];
        threadId = data.thread_id;

        if (credentials.length > 0) {
            credentials.forEach(cred => {
                const option = document.createElement('option');
                option.value = cred.cred_info.referent;
                option.textContent = `${cred.cred_info.attrs[attributes[0]] || 'Unknown'} - ${schemaId.split(':2:')[1]}`;
                credentialSelect.appendChild(option);
            });
            credentialSelectContainer.classList.remove('hidden');
            
        } else {
            errorMessage.textContent = 'No credentials received from holder';
            errorMessage.classList.remove('hidden');
            return;
        }
        toastMessage.firstElementChild.textContent = 'Proof request sent successfully!';
        toastMessage.classList.remove('hidden');
        setTimeout(() => toastMessage.classList.add('hidden'), 5000);
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.classList.remove('hidden');
    }
}

function displayCredentialDetails(referent) {
    const credentialDetails = document.getElementById('credentialDetails');
    const sendPresentationButton = document.getElementById('sendPresentation');
    credentialDetails.innerHTML = '';

    if (!referent || !selectedSchema) {
        credentialDetails.classList.add('hidden');
        return;
    }

    const cred = credentials.find(c => c.cred_info.referent === referent);
    if (!cred) {
        credentialDetails.innerHTML = '<p class="text-gray-600">Credential not found.</p>';
        credentialDetails.classList.remove('hidden');
        return;
    }

    const attrs = cred.cred_info.attrs;
    let detailsHtml = `<div class="border p-4 rounded shadow"><h3 class="text-lg font-bold mb-2">${selectedSchema.schema_id.split(':2:')[1]} Credential Details</h3>`;
    selectedSchema.attributes.forEach(attr => {
        detailsHtml += `
            <div class="attribute">
                <span>${attr}: ${attrs[attr] || 'N/A'}</span>
                <button class="reveal-btn bg-blue-500" data-attr="${attr}">Reveal</button>
            </div>`;
    });
    detailsHtml += '</div>';
    credentialDetails.innerHTML = detailsHtml;
    credentialDetails.classList.remove('hidden');
    sendPresentationButton.classList.remove('hidden');
    document.querySelectorAll('.reveal-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('bg-blue-500');
            btn.classList.toggle('bg-gray-500');
            btn.textContent = btn.classList.contains('bg-gray-500') ? 'Hide' : 'Reveal';
        });
    });
    document.getElementById('sendPresentation').disabled = false;
}

async function sendPresentation() {
    const referent = document.getElementById('credentialSelect').value;
    const toastMessage = document.getElementById('toast-message');
    const errorMessage = document.getElementById('error-message');

    toastMessage.classList.add('hidden');
    errorMessage.classList.add('hidden');

    if (!holderPresExId) {
        errorMessage.textContent = 'No holder presentation exchange ID available';
        errorMessage.classList.remove('hidden');
        return;
    }

    if (!referent) {
        errorMessage.textContent = 'Please select a credential';
        errorMessage.classList.remove('hidden');
        return;
    }

    if (!selectedSchema) {
        errorMessage.textContent = 'No schema selected';
        errorMessage.classList.remove('hidden');
        return;
    }

    const selectedAttrs = {};
    document.querySelectorAll('.reveal-btn.bg-blue-500').forEach(btn => {
        selectedAttrs[btn.dataset.attr] = true;
    });

    const requestedAttributes = {};
    selectedSchema.attributes.forEach(attr => {
        requestedAttributes[`${attr}_attributes`] = {
            cred_id: referent,
            revealed: !!selectedAttrs[attr]
        };
    });

    try {
        const response = await fetch('/manual_presentations/holder/send-presentation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pres_ex_id: holderPresExId,
                presentation: {
                    indy: {
                        requested_attributes: requestedAttributes,
                        requested_predicates: selectedSchema.attributes.includes('unixdob') ? {
                            "age_predicate": { cred_id: referent }
                        } : {},
                        self_attested_attributes: {}
                    }
                }
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! Status: ${response.status} - ${errorText}`);
        }
        if (!response.headers.get('content-type').includes('application/json')) {
            throw new Error('Unexpected response format');
        }

        const data = await response.json();
        toastMessage.firstElementChild.textContent = 'Presentation sent successfully! Awaiting verification...';
        toastMessage.classList.remove('hidden');

        let attempts = 0;
        const maxAttempts = 10;
        let delay = 1000;

        while (attempts < maxAttempts) {
            try {
                const verifyResponse = await fetch(`/presentations/get-presentation-status/${threadId}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                if (!verifyResponse.ok) {
                    throw new Error(`HTTP error! Status: ${verifyResponse.status}`);
                }
                if (!verifyResponse.headers.get('content-type').includes('application/json')) {
                    throw new Error('Unexpected response format');
                }
                const verifyData = await verifyResponse.json();
                if (verifyData.verified === "true") {
                    toastMessage.firstElementChild.textContent = 'Credential Verified!';
                    toastMessage.classList.remove('hidden');
                    setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                    return;
                } else if (verifyData.verified === "false" || verifyData.state === "abandoned" || verifyData.state === "deleted") {
                    toastMessage.classList.add('hidden');
                    const errorMsg = verifyData.error || 'Verification failed: Credential is revoked or invalid';
                    throw new Error(errorMsg);
                }
            } catch (verifyError) {
                toastMessage.classList.add('hidden');
                errorMessage.textContent = verifyError.message;
                errorMessage.classList.remove('hidden');
                return;
            }
            attempts++;
            await new Promise(resolve => setTimeout(resolve, delay));
            delay *= 1.5; // Exponential backoff
        }

        toastMessage.classList.add('hidden');
        errorMessage.textContent = 'Verification timed out. Please try again.';
        errorMessage.classList.remove('hidden');
    } catch (error) {
        toastMessage.classList.add('hidden');
        errorMessage.textContent = `Error sending presentation: ${error.message}`;
        errorMessage.classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchSchemas();
    fetchHolderConnections();
    document.getElementById('schemaSelect')?.addEventListener('change', () => {
        document.getElementById('credentialSelect').innerHTML = '<option value="">Select a credential</option>';
        document.getElementById('credentialDetails').innerHTML = '';
        document.getElementById('credentialDetails').classList.add('hidden');
        document.getElementById('credentialSelectContainer').classList.add('hidden');
        document.getElementById('sendPresentation').classList.add('hidden');
        document.getElementById('sendPresentation').disabled = true;
    });
    document.getElementById('credentialSelect')?.addEventListener('change', () => {
        displayCredentialDetails(document.getElementById('credentialSelect').value);
    });
    document.getElementById('sendProofRequest')?.addEventListener('click', sendProofRequest);
    document.getElementById('sendPresentation')?.addEventListener('click', sendPresentation);
    document.getElementById('toast-close')?.addEventListener('click', () => {
        document.getElementById('toast-message').classList.add('hidden');
    });
});