async function issueCredential() {
    try {
        // Step 1: Create new DID
        const didResponse = await fetch('/jwt-credentials/create-did', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: 'key',
                options: { key_type: 'ed25519' }
            })
        });
        if (!didResponse.ok) throw new Error(`Failed to create DID: ${await didResponse.text()}`);
        const didData = await didResponse.json();
        const did = didData.result.did;
        const verkey = didData.result.verkey;
        console.log('Created DID:', didData);
        createToast('DID created successfully', 'success');

        const issuerResponse = await fetch('/did/issuer', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        const issuerData = await issuerResponse.json();
        const issuerDid = issuerData.did;
        console.log("Issuer DID: ", issuerDid)

        // Credential type configurations
        const credentialConfigs = {
            UniversityDegreeCredential: {
                type: ['VerifiableCredential', 'UniversityDegreeCredential'],
                credentialSubject: {
                    id: did,
                    name: 'Nguyễn Tài Nguyên',
                    degree: 'Bachelor of Information Security',
                    status: 'graduated',
                    graduationDate: '2025-07-16'
                }
            },
            DoctorCredential: {
                type: ['VerifiableCredential', 'DoctorCredential'],
                credentialSubject: {
                    id: did,
                    ho_ten: 'Trần Thị B',
                    chuc_vu: "Bác sĩ",
                    chuyen_khoa: 'Tim mạch',
                    benh_vien: 'Bệnh viện A',
                    licenseNumber: 'VN-MOH-2025-123456'
                }
            }
        };

        // Get selected credential type
        const credentialType = document.getElementById('credential-type').value;
        if (!credentialType) throw new Error('Please select a credential type');

        const payload = {
            iss: `did:sov:${issuerDid}`,
            sub: did,
            vc: {
                '@context': ['https://www.w3.org/2018/credentials/v1'],
                ...credentialConfigs[credentialType]
            },
            exp: Math.floor(Date.now() / 1000) + 3600,
            iat: Math.floor(Date.now() / 1000)
        };

        const vcResponse = await fetch('/jwt-credentials/sign-vc-jwt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ did: `did:sov:${issuerDid}`, payload })
        });
        if (!vcResponse.ok) throw new Error(`Failed to sign VC-JWT: ${await vcResponse.text()}`);
        const vcData = await vcResponse.json();
        console.log('Signed VC-JWT:', vcData);
        createToast('VC-JWT signed successfully', 'success');

        // Step 3: Store in server-side wallet
        const storeResponse = await fetch('/jwt-wallet/store', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                did: did,
                jwt: vcData.jwt,
                verkey: verkey
            })
        });
        if (!storeResponse.ok) throw new Error(`Failed to store credential: ${await storeResponse.text()}`);
        const storeData = await storeResponse.json();
        console.log('Stored credential:', storeData);
        createToast('Credential stored successfully', 'success');

        // Display result
        const result = { did: didData.result, vcJwt: vcData, stored: storeData };
        const didResult = document.getElementById('did-result');
        didResult.querySelector('pre').textContent = JSON.stringify(result, null, 2);
        didResult.classList.remove('hidden');

        // Reset form and preview
        document.getElementById('credential-type').value = '';
        document.getElementById('issue-credential').disabled = true;
        renderCredentialPreview('');
    } catch (error) {
        console.error('Error issuing credential:', error);
        createToast(error.message, 'error');
        showError(error.message);
    }
}

function showError(message) {
    const errorDiv = document.getElementById('generic-error');
    errorDiv.textContent = `Error: ${message}`;
    errorDiv.classList.remove('hidden');
}

function createToast(message, type) {
    console.log(`Toast: ${message} (${type})`);
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 p-4 rounded text-white ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function renderCredentialPreview(credentialType) {
    const previewContainer = document.getElementById('credential-preview');
    const previewContent = document.getElementById('preview-content');
    
    if (!credentialType) {
        previewContainer.classList.add('hidden');
        previewContent.innerHTML = '';
        return;
    }

    const credentialConfigs = {
        UniversityDegreeCredential: {
            type: ['VerifiableCredential', 'UniversityDegreeCredential'],
            credentialSubject: {
                name: 'Nguyễn Tài Nguyên',
                degree: 'Bachelor of Information Security',
                status: 'graduated',
                graduationDate: '2025-07-16'
            }
        },
        DoctorCredential: {
            type: ['VerifiableCredential', 'DoctorCredential'],
            credentialSubject: {
                ho_ten: 'Trần Thị B',
                chuc_vu: 'Bác sĩ',
                chuyen_khoa: 'Tim mạch',
                benh_vien: 'Bệnh viện A',
                licenseNumber: 'VN-MOH-2025-123456'
            }
        }
    };

    const config = credentialConfigs[credentialType];
    if (!config) {
        previewContainer.classList.add('hidden');
        return;
    }

    const attributes = Object.entries(config.credentialSubject)
        .map(([key, value]) => `<p><strong>${key}:</strong> ${value}</p>`)
        .join('');

    previewContent.innerHTML = attributes;
    previewContainer.classList.remove('hidden');
}

document.getElementById('issue-credential').addEventListener('click', issueCredential);

// Enable/disable issue button and show preview based on dropdown selection
document.getElementById('credential-type').addEventListener('change', () => {
    const credentialType = document.getElementById('credential-type').value;
    const issueButton = document.getElementById('issue-credential');
    issueButton.disabled = !credentialType;
    renderCredentialPreview(credentialType);
});