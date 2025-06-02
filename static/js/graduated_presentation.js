let holderPresExId = null;
let credentials = [];
let threadId = null;

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
                            "0_ho_ten_uuid": { "name": "ho_ten", },
                            "0_chuyen_nganh_uuid": { "name": "chuyen_nganh" },
                            "0_mssv_uuid": { "name": "mssv" },
                            "0_loai_bang_uuid": { "name": "loai_bang" },
                            "0_truong_uuid": { "name": "truong" },
                            "0_gpa_uuid": { "name": "gpa" },
                            "0_ngay_tot_nghiep_uuid": { "name": "ngay_tot_nghiep" },
                            "0_ngay_sinh_uuid": { "name": "ngay_sinh" },
                            "0_unixdob_uuid": { "name": "unixdob" }
                        },
                        requested_predicates: {
                            "0_trang_thai_tot_nghiep_uuid": {
                                "name": "trang_thai_tot_nghiep",
                                "p_type": ">=",
                                "p_value": 1
                            }
                        },
                        non_revoked: {
                            from: 0,
                            to: Math.floor(Date.now() / 1000)
                        }
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
                option.textContent = `${cred.cred_info.attrs.ho_ten || 'Unknown'} - ${cred.cred_info.attrs.loai_bang || 'Unknown'} (${cred.cred_info.attrs.truong || 'Unknown'})`;
                credentialSelect.appendChild(option);
            });
        }
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
            <h3 class="text-lg font-bold mb-2">Credential Details</h3>
            <div class="attribute mb-2">
                <span>Họ tên: ${attrs.ho_ten || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ho_ten">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Chuyên ngành: ${attrs.chuyen_nganh || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="chuyen_nganh">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>MSSV: ${attrs.mssv || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="mssv">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Loại bằng: ${attrs.loai_bang || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="loai_bang">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Trường: ${attrs.truong || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="truong">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>GPA: ${attrs.gpa || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="gpa">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Ngày tốt nghiệp: ${attrs.ngay_tot_nghiep || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ngay_tot_nghiep">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Ngày sinh: ${attrs.ngay_sinh || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="ngay_sinh">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Unix DOB: ${attrs.unixdob || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="unixdob">Reveal</button>
            </div>
            <div class="attribute mb-2">
                <span>Trạng thái tốt nghiệp: ${attrs.trang_thai_tot_nghiep || 'N/A'}</span>
                <button class="reveal-btn ml-2 px-2 py-1 bg-blue-500 text-white rounded" data-attr="trang_thai_tot_nghiep">Reveal</button>
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
        'ngay_sinh',
        'unixdob'
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
        toastMessage.textContent = 'Presentation sent successfully! Awaiting verification...';
        toastMessage.classList.remove('hidden');

        // Poll for verification status
        let attempts = 0;
        const maxAttempts = 10;
        const pollInterval = 1000; // 1 second

        while (attempts < maxAttempts) {
            try {
                const verifyResponse = await fetch(`/presentations/verify/${threadId}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                if (!verifyResponse.ok) {
                    throw new Error(`HTTP error! Status: ${verifyResponse.status}`);
                }
                const verifyData = await verifyResponse.json();
                if (verifyData.status === 'verified') {
                    toastMessage.textContent = 'Credential Verified!';
                    toastMessage.classList.remove('hidden');
                    setTimeout(() => toastMessage.classList.add('hidden'), 5000);
                    return;
                }
            } catch (verifyError) {
                console.error('Verification check error:', verifyError.message);
            }
            attempts++;
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }

        errorMessage.textContent = 'Verification timed out. Please try again.';
        errorMessage.classList.remove('hidden');
    } catch (error) {
        errorMessage.textContent = `Error sending presentation: ${error.message}`;
        errorMessage.classList.remove('hidden');
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