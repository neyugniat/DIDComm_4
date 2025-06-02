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

        // Step 2: Sign VC-JWT
        // const payload = {
        //     iss: `did:sov:${issuerDid}`,
        //     sub: did,
        //     vc: {
        //         '@context': ['https://www.w3.org/2018/credentials/v1'],
        //         type: ['VerifiableCredential', 'UniversityDegreeCredential'],
        //         credentialSubject: {
        //             id: did,
        //             name: 'Nguyễn Tài Nguyên',
        //             degree: 'Bachelor of Information Security',
        //             status: 'graduated',
        //             graduationDate: '2025-07-16'
        //         }
        //     },
        //     exp: Math.floor(Date.now() / 1000) + 3600,
        //     iat: Math.floor(Date.now() / 1000)
        // };

        const payload = {
            iss: `did:sov:${issuerDid}`,
            sub: did,
            vc: {
                '@context': ['https://www.w3.org/2018/credentials/v1'],
                type: ['VerifiableCredential', 'DoctorCredential'],
                credentialSubject: {
                    id: did,
                    ho_ten: 'Trần Thị B',
                    chuc_vu: "Bác sĩ",
                    chuyen_khoa: 'Tim mạch',
                    benh_vien: 'Bệnh viện A',
                    licenseNumber: 'VN-MOH-2025-123456'
                }
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

document.getElementById('issue-credential').addEventListener('click', issueCredential);