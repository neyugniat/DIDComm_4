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
        const schemaId = `${issuerDid}:2:Can_Cuoc_Cong_Dan:1.0`;
        const targetAge = 18;
        const unixDobValue = calculateUnixDobInDays(targetAge);

        const response = await fetch('/age_presentation/verifier/send-request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                connection_id: connectionId,
                auto_verify: true,
                presentation_request: {
                    indy: {
                        name: "CCCD Verification",
                        version: "1.0",
                        requested_attributes: {
                            "0_ho_ten_uuid": { "name": "ho_ten", "restrictions": [{ "schema_id": schemaId }] },
                            "0_gioi_tinh_uuid": { "name": "gioi_tinh", "restrictions": [{ "schema_id": schemaId }] },
                            "0_noi_cap_uuid": { "name": "noi_cap", "restrictions": [{ "schema_id": schemaId }] },
                            "0_noi_thuong_tru_uuid": { "name": "noi_thuong_tru", "restrictions": [{ "schema_id": schemaId }] },
                            "0_so_cccd_uuid": { "name": "so_cccd", "restrictions": [{ "schema_id": schemaId }] },
                            "0_que_quan_uuid": { "name": "que_quan", "restrictions": [{ "schema_id": schemaId }] },
                            "0_ngay_cap_uuid": { "name": "ngay_cap", "restrictions": [{ "schema_id": schemaId }] },
                            "0_ngay_sinh_uuid": { "name": "ngay_sinh", "restrictions": [{ "schema_id": schemaId }] },
                            "0_quoc_tich_uuid": { "name": "quoc_tich", "restrictions": [{ "schema_id": schemaId }] }
                        },
                        requested_predicates: {
                            "0_age_GT_uuid": {
                                "name": "unixdob",
                                "p_type": "<",
                                "p_value": unixDobValue,
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
            credentials.forEach(cred => {
                const option = document.createElement('option');
                option.value = cred.cred_info.referent;
                option.textContent = `${cred.cred_info.attrs.ho_ten || 'Unknown'} - CCCD (${cred.cred_info.attrs.so_cccd || 'Unknown'})`;
                credentialSelect.appendChild(option);
            });
        }
        toastMessage.classList.add('toast-success'); // Green for success
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
            <h3 class="text-lg font-bold mb-2">CCCD Credential Details</h3>
            <div class="attribute mb-2">
                <span>Họ tên: ${attrs.ho_ten || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ho_ten">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Giới tính: ${attrs.gioi_tinh || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="gioi_tinh">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Nơi cấp: ${attrs.noi_cap || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="noi_cap">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Nơi thường trú: ${attrs.noi_thuong_tru || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="noi_thuong_tru">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Số CCCD: ${attrs.so_cccd || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="so_cccd">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Quê quán: ${attrs.que_quan || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="que_quan">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Ngày cấp: ${attrs.ngay_cap || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ngay_cap">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Ngày sinh: ${attrs.ngay_sinh || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ngay_sinh">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Quốc tịch: ${attrs.quoc_tich || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="quoc_tich">Reveal</button>
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
        'gioi_tinh',
        'noi_cap',
        'noi_thuong_tru',
        'so_cccd',
        'que_quan',
        'ngay_cap',
        'ngay_sinh',
        'quoc_tich'
    ];
    const requestedAttributes = {};
    allAttributes.forEach(attr => {
        requestedAttributes[`0_${attr}_uuid`] = {
            cred_id: referent,
            revealed: !!selectedAttrs[attr]
        };
    });

    try {
        const response = await fetch('/age_presentation/holder/send-presentation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pres_ex_id: holderPresExId,
                presentation: {
                    indy: {
                        requested_attributes: requestedAttributes,
                        requested_predicates: {
                            "0_age_GT_uuid": { "cred_id": referent }
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
        toastMessage.classList.add('toast-success'); // Green for success
        toastMessage.classList.remove('toast-error');
        toastMessage.textContent = 'Presentation sent successfully! Awaiting verification...';
        toastMessage.classList.remove('hidden');

        // Poll for verification status
        let attempts = 0;
        const maxAttempts = 10;
        const pollInterval = 1000;

        while (attempts < maxAttempts) {
            try {
                const verifyResponse = await fetch(`/presentations/get-presentation-status/${threadId}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                if (!verifyResponse.ok) {
                    throw new Error(`HTTP error! Status: ${verifyResponse.status}`);
                }
                const verifyData = await verifyResponse.json();
                if (verifyData.verified === "true") {
                    toastMessage.classList.add('toast-success');
                    toastMessage.classList.remove('toast-error');
                    toastMessage.textContent = 'Credential Verified!';
                    toastMessage.classList.remove('hidden');
                    setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                    return;
                } else if (verifyData.verified === "false" || verifyData.state === "abandoned" || verifyData.state === "deleted") {
                    toastMessage.classList.add('toast-error'); // Red for failure
                    toastMessage.classList.remove('toast-success');
                    toastMessage.textContent = 'Verification failed: ' + (verifyData.error || 'Credential is revoked or invalid');
                    toastMessage.classList.remove('hidden');
                    setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                    return;
                }
            } catch (verifyError) {
                toastMessage.classList.add('toast-error'); // Red for error
                toastMessage.classList.remove('toast-success');
                toastMessage.textContent = 'Verification error: ' + verifyError.message;
                toastMessage.classList.remove('hidden');
                setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                return;
            }
            attempts++;
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }

        toastMessage.classList.add('toast-error'); // Red for timeout
        toastMessage.classList.remove('toast-success');
        toastMessage.textContent = 'Verification timed out. Please try again.';
        toastMessage.classList.remove('hidden');
        setTimeout(() => toastMessage.classList.add('hidden'), 5000);
    } catch (error) {
        toastMessage.classList.add('toast-error'); // Red for error
        toastMessage.classList.remove('toast-success');
        toastMessage.textContent = `Error sending presentation: ${error.message}`;
        toastMessage.classList.remove('hidden');
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