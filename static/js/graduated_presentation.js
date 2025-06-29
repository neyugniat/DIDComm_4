let holderPresExId = null;
let credentials = [];
let threadId = null;

async function fetchIssuerDid() {
    try {
        const response = await fetch('/did/issuer', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        return data.did;
    } catch (error) {
        throw new Error(`Failed to fetch issuer DID: ${error.message}`);
    }
}

async function fetchHolderConnections() {
    try {
        const response = await fetch('/connections/verifier', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
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

async function sendProofRequest() {
    const connectionId = document.getElementById('connectionSelect').value;
    const errorMessage = document.getElementById('error-message');
    const credentialSelect = document.getElementById('credentialSelect');
    const credentialDetails = document.getElementById('credentialDetails');
    const toastMessage = document.getElementById('toast-message');

    toastMessage.classList.add('hidden');
    errorMessage.classList.add('hidden');
    credentialSelect.innerHTML = '<option value="">Select a credential</option>';
    credentialDetails.innerHTML = '';
    holderPresExId = null;
    credentials = [];
    threadId = null;

    if (!connectionId) {
        errorMessage.textContent = 'Please select a connection';
        errorMessage.classList.remove('hidden');
        return;
    }

    try {
        const issuerDid = await fetchIssuerDid();
        const schemaId = `${issuerDid}:2:Bang_tot_nghiep:1.0`;

        const response = await fetch('/graduated_presentation/verifier/send-request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                connection_id: connectionId,
                auto_verify: true,
                presentation_request: {
                    indy: {
                        name: "Graduation Verification",
                        version: "1.0",
                        requested_attributes: {
                            "0_ho_ten_uuid": { "name": "ho_ten", "restrictions": [{ "schema_id": schemaId }] },
                            "0_chuyen_nganh_uuid": { "name": "chuyen_nganh", "restrictions": [{ "schema_id": schemaId }] },
                            "0_mssv_uuid": { "name": "mssv", "restrictions": [{ "schema_id": schemaId }] },
                            "0_loai_bang_uuid": { "name": "loai_bang", "restrictions": [{ "schema_id": schemaId }] },
                            "0_truong_uuid": { "name": "truong", "restrictions": [{ "schema_id": schemaId }] },
                            "0_gpa_uuid": { "name": "gpa", "restrictions": [{ "schema_id": schemaId }] },
                            "0_ngay_tot_nghiep_uuid": { "name": "ngay_tot_nghiep", "restrictions": [{ "schema_id": schemaId }] },
                            "0_ngay_sinh_uuid": { "name": "ngay_sinh", "restrictions": [{ "schema_id": schemaId }] },
                        },
                        requested_predicates: {
                            "0_trang_thai_tot_nghiep_uuid": {
                                "name": "trang_thai_tot_nghiep",
                                "p_type": ">=",
                                "p_value": 1,
                                "restrictions": [{ "schema_id": schemaId }]
                            }
                        },
                        non_revoked: { from: 0, to: Math.floor(Date.now() / 1000) }
                    }
                },
                auto_remove: false
            })
        });

        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        holderPresExId = data.holder_pres_ex_id;
        credentials = data.credentials || [];
        threadId = data.thread_id;

        if (credentials.length > 0) {
            credentials.forEach(credential => {
                const option = document.createElement('option');
                option.value = credential.cred_info.referent;
                option.textContent = `${credential.cred_info.attrs.ho_ten || 'Unknown'} - ${credential.cred_info.attrs.loai_bang || 'Unknown'} (${credential.cred_info.attrs.truong || 'Unknown'})`;
                credentialSelect.appendChild(option);
            });
        }
        toastMessage.classList.add('toast-success');
        toastMessage.classList.remove('toast-error');
        toastMessage.textContent = 'Proof request sent successfully!';
        toastMessage.classList.remove('hidden');
        setTimeout(() => toastMessage.classList.add('hidden'), 5000);
    } catch (error) {
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.classList.remove('hidden');
    }
}

function displayCredentialDetails(referent) {
    const credentialDetails = document.getElementById('credentialDetails');
    credentialDetails.innerHTML = '';

    if (!referent) return;

    const cred = credentials.find(c => c.cred_info.referent === referent);
    if (!cred) {
        credentialDetails.innerHTML = '<p class="text-gray-600">Credential not found.</p>';
        return;
    }

    const attrs = cred.cred_info.attrs;
    credentialDetails.innerHTML = `
        <div class="border p-4 rounded shadow">
            <div class="border-b mb-4">
                <h3 class="text-lg font-bold">Credential Details</h3>
            </div>
            <div class="attribute mb-2">
                <span>Name: ${attrs.ho_ten || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ho_ten">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Chuyen Nghanh: ${attrs.chuyen_nganh || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="chuyen_nganh">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>MSSV: ${attrs.mssv || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="mssv">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Loai Bang: ${attrs.loai_bang || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-2 bg-blue-500 text-white rounded" data-attr="loai_bang">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Truong: ${attrs.truong || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="truong">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>GPA: ${attrs.gpa || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="gpa">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Graduation Date: ${attrs.ngay_tot_nghiep || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ngay_tot_nghiep">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Birth Date: ${attrs.ngay_sinh || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ngay_sinh">Reveal</button>
            </div>
        </div>
    `;

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

    const selectedAttrs = {};
    document.querySelectorAll('.reveal-btn.bg-blue-500').forEach(btn => {
        selectedAttrs[btn.dataset.attr] = true;
    });

    const allAttributes = [
        'ho_ten',
        'chuyen_nganh',
        'mssv',
        'loai_bang',
        'truong',
        'gpa',
        'ngay_tot_nghiep',
        'ngay_sinh'
    ];
    const requestedAttributes = {};
    allAttributes.forEach(attr => {
        requestedAttributes[`0_${attr}_uuid`] = {
            cred_id: referent,
            revealed: !!selectedAttrs[attr]
        };
    });

    try {
        const response = await fetch('/graduated_presentation/holder/send-presentation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pres_ex_id: holderPresExId,
                presentation: {
                    indy: {
                        requested_attributes: requestedAttributes,
                        requested_predicates: {
                            "0_trang_thai_tot_nghiep_uuid": { "cred_id": referent }
                        },
                        self_attested_attributes: {}
                    }
                }
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! Status: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        toastMessage.classList.add('toast-success');
        toastMessage.classList.remove('toast-error');
        toastMessage.textContent = 'Presentation sent successfully! Awaiting verification...';
        toastMessage.classList.remove('hidden');

        // Poll for verification status
        let attempts = 0;
        const maxAttempts = 10;
        const pollInterval = 1000;

        while (attempts < maxAttempts) {
            try {
                const verifyResponse = await fetch(`/presentations/verify/${threadId}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                if (verifyResponse.status === 425) {
                    attempts++;
                    await new Promise(resolve => setTimeout(resolve, pollInterval));
                    continue;
                }
                if (!verifyResponse.ok) {
                    throw new Error(`HTTP error! Status: ${verifyResponse.status}`);
                }
                const verifyData = await verifyResponse.json();
                if (verifyData.status === 'verified') {
                    toastMessage.classList.add('toast-success');
                    toastMessage.classList.remove('toast-error');
                    toastMessage.textContent = 'Credential Verified!';
                    toastMessage.classList.remove('hidden');
                    setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                    return;
                } else if (verifyData.status === 'failed' || verifyData.state === 'abandoned' || verifyData.state === 'deleted') {
                    toastMessage.classList.add('toast-error');
                    toastMessage.classList.remove('toast-success');
                    toastMessage.textContent = 'Verification failed: ' + (verifyData.error || 'Credential is revoked or invalid');
                    toastMessage.classList.remove('hidden');
                    setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                    return;
                }
            } catch (verifyError) {
                toastMessage.classList.add('toast-error');
                toastMessage.classList.remove('toast-success');
                toastMessage.textContent = 'Verification error: ' + verifyError.message;
                toastMessage.classList.remove('hidden');
                setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                return;
            }
            attempts++;
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }

        toastMessage.classList.add('toast-error');
        toastMessage.classList.remove('toast-success');
        toastMessage.textContent = 'Verification timed out. Please try again.';
        toastMessage.classList.remove('hidden');
        setTimeout(() => toastMessage.classList.add('hidden'), 5000);
    } catch (error) {
        toastMessage.classList.add('toast-error');
        toastMessage.classList.remove('toast-success');
        toastMessage.textContent = `Error sending presentation: ${error.message}`;
        toastMessage.classList.remove('hidden');
        document.getElementById('error-message').classList.remove('hidden');
        setTimeout(() => toastMessage.classList.add('hidden'), 5000);
    }
}

document.getElementById('sendProofRequest')?.addEventListener('click', sendProofRequest);
document.getElementById('sendPresentation')?.addEventListener('click', sendPresentation);
document.addEventListener('DOMContentLoaded', () => {
    fetchHolderConnections();
    document.getElementById('credentialSelect')?.addEventListener('change', () => {
        displayCredentialDetails(document.getElementById('credentialSelect').value);
    });
    document.getElementById('toast-close')?.addEventListener('click', () => {
        document.getElementById('toast-message').classList.add('hidden');
    });
});