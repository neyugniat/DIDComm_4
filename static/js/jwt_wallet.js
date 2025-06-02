let credentials = [];

async function updateCredentialList() {
    try {
        const response = await fetch('/jwt-wallet/credentials', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) throw new Error(`Failed to fetch credentials: ${await response.text()}`);
        credentials = await response.json();
        console.log('Fetched credentials:', credentials);

        const listDiv = document.getElementById('credential-list');
        const select = document.getElementById('wallet-credential');
        listDiv.innerHTML = '';
        select.innerHTML = '<option value="">Select a credential</option>';

        credentials.forEach(cred => {
            // Parse VC-JWT to extract human-readable info
            let displayName = 'Unknown';
            let displayField = 'Unknown';
            let credentialType = 'Unknown';
            try {
                const payload = JSON.parse(atob(cred.jwt.split('.')[1]));
                if (payload.vc && payload.vc.credentialSubject) {
                    const subject = payload.vc.credentialSubject;
                    credentialType = payload.vc.type.includes('UniversityDegreeCredential') 
                        ? 'University Degree' 
                        : payload.vc.type.includes('DoctorCredential') 
                            ? 'Doctor Credential' 
                            : 'Unknown Credential';
                    
                    if (credentialType === 'University Degree') {
                        displayName = subject.name || displayName;
                        displayField = subject.degree || displayField;
                    } else if (credentialType === 'Doctor Credential') {
                        displayName = subject.ho_ten || displayName;
                        displayField = subject.chuyen_khoa || displayField;
                    }
                }
            } catch (e) {
                console.error('Error parsing VC-JWT:', e);
            }

            // Display in list
            const div = document.createElement('div');
            div.className = 'border p-4 mb-2 rounded bg-gray-50';
            div.innerHTML = `
                <strong>Type:</strong> ${credentialType}<br>
                <strong>Name:</strong> ${displayName}<br>
                <strong>${credentialType === 'University Degree' ? 'Degree' : 'Specialty'}:</strong> ${displayField}<br>
                <strong>DID:</strong> ${cred.did}<br>
            `;
            listDiv.appendChild(div);

            // Add to dropdown
            const option = document.createElement('option');
            option.value = cred.did;
            option.textContent = `${displayName} - ${credentialType} (${displayField})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching credentials:', error);
        createToast(error.message, 'error');
        showError(error.message);
    }
}

async function generateVpJwt() {
    try {
        const did = document.getElementById('wallet-credential').value;
        const credential = credentials.find(c => c.did === did);
        if (!did || !credential) {
            throw new Error('Please select a valid credential');
        }

        // Validate verkey (ensure it's a valid base64 string)
        if (!credential.verkey || typeof credential.verkey !== 'string') {
            throw new Error('Invalid verification key for selected credential');
        }
        // Normalize verkey (add padding if missing)
        let normalizedVerkey = credential.verkey;
        try {
            // Ensure verkey is properly padded
            while (normalizedVerkey.length % 4 !== 0) {
                normalizedVerkey += '=';
            }
            // Test base64 decoding
            atob(normalizedVerkey);
        } catch (e) {
            throw new Error(`Invalid base64 verkey: ${e.message}`);
        }

        // Fetch verifier DID
        const verifierResponse = await fetch('/did/verifier', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!verifierResponse.ok) {
            throw new Error(`Failed to fetch verifier DID: ${await verifierResponse.text()}`);
        }
        const verifierData = await verifierResponse.json();
        const verifierDid = verifierData.did;
        console.log('Verifier DID:', verifierDid);

        // Construct VP payload
        const payload = {
            iss: did,
            aud: `did:sov:${verifierDid}`,
            vp: {
                '@context': ['https://www.w3.org/2018/credentials/v1'],
                type: ['VerifiablePresentation'],
                verifiableCredential: [credential.jwt]
            },
            exp: Math.floor(Date.now() / 1000) + 3600,
            iat: Math.floor(Date.now() / 1000),
            cnf: {}
        };

        // Log payload for debugging
        console.log('VP-JWT Payload:', JSON.stringify(payload, null, 2));

        // Sign VP-JWT
        const response = await fetch('/jwt-credentials/sign-vp-jwt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ did, payload, verkey: normalizedVerkey })
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to sign VP-JWT: ${errorText}`);
        }
        const data = await response.json();
        console.log('Signed VP-JWT:', data);
        createToast('VP-JWT generated successfully', 'success');

        // Display VP-JWT
        document.getElementById('vp-jwt').value = data.jwt;
    } catch (error) {
        console.error('Error generating VP-JWT:', error);
        createToast(error.message, 'error');
        showError(error.message);
    }
}

function copyVpJwt() {
    const vpJwtText = document.getElementById('vp-jwt');
    if (!vpJwtText.value) {
        createToast('No VP-JWT to copy!', 'error');
        return;
    }
    vpJwtText.select();
    document.execCommand('copy');
    createToast('VP-JWT copied to clipboard!', 'success');
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

document.getElementById('generate-vp').addEventListener('click', generateVpJwt);
document.getElementById('copy-vp').addEventListener('click', copyVpJwt);

// Initialize credential list
updateCredentialList();