document.getElementById('verifierFetchBtn')?.addEventListener('click', async () => {
  const urlDisplay = document.getElementById('verifierInvitationUrl');
  const qrDisplay = document.getElementById('verifierQRCode');
  const jsonDisplay = document.getElementById('verifierInvitationJson');
  const copyBtn = document.getElementById('verifierCopyBtn');
  const successMsg = document.getElementById('success-message');
  const errorMsg = document.getElementById('error-message');

  if (!urlDisplay || !qrDisplay || !jsonDisplay || !copyBtn || !successMsg || !errorMsg) {
    console.error('Missing one or more DOM elements.');
    return;
  }

  // Reset UI
  urlDisplay.textContent = '';
  urlDisplay.href = '#';
  qrDisplay.innerHTML = '';
  jsonDisplay.textContent = '';
  copyBtn.classList.add('hidden');
  successMsg.classList.add('hidden');
  errorMsg.classList.add('hidden');

  try {
    const response = await fetch('/connections/verifier/create-invitation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        accept: ['didcomm/aip1', 'didcomm/aip2;env=rfc19'],
        handshake_protocols: ['https://didcomm.org/didexchange/1.1'],
        my_label: 'B_BANK',
        use_public_did: false
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}: ${await response.text()}`);

    const data = await response.json();
    const invitationUrl = data.invitation_url;
    const invitation = data.invitation;

    if (!invitationUrl || !invitation) {
      throw new Error('Invalid response: missing invitation_url or invitation.');
    }

    // Display invitation URL
    urlDisplay.textContent = invitationUrl;
    urlDisplay.href = invitationUrl;

    const connectionDetails = document.getElementById('connection-details');
    if (connectionDetails) connectionDetails.classList.remove('hidden');

    // Show QR code
    new QRCode(qrDisplay, {
      text: invitationUrl,
      width: 200,
      height: 200,
      colorDark: '#000000',
      colorLight: '#ffffff',
      correctLevel: QRCode.CorrectLevel.H
    });

    // Show JSON
    const formattedJson = JSON.stringify(invitation, null, 2);
    jsonDisplay.textContent = formattedJson;

    // Enable copy
    copyBtn.classList.remove('hidden');
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(formattedJson)
        .then(() => {
          successMsg.textContent = 'Invitation copied!';
          successMsg.classList.remove('hidden');
          setTimeout(() => successMsg.classList.add('hidden'), 3000);
        })
        .catch(err => {
          errorMsg.textContent = `Copy error: ${err.message}`;
          errorMsg.classList.remove('hidden');
        });
    };

    successMsg.textContent = 'Invitation created successfully!';
    successMsg.classList.remove('hidden');

  } catch (err) {
    errorMsg.textContent = `Fetch failed: ${err.message}`;
    errorMsg.classList.remove('hidden');
  }
});


// HOLDER: Receive Invitation
document.getElementById('holderReceiveBtn')?.addEventListener('click', async () => {
  const input = document.getElementById('holderInvitationInput');
  const successMsg = document.getElementById('success-message');
  const errorMsg = document.getElementById('error-message');

  if (!input || !successMsg || !errorMsg) {
    console.error('Missing DOM elements for holder input.');
    return;
  }

  successMsg.classList.add('hidden');
  errorMsg.classList.add('hidden');

  const rawText = input.value.trim();
  if (!rawText) {
    errorMsg.textContent = 'Paste a valid invitation JSON.';
    errorMsg.classList.remove('hidden');
    return;
  }

  try {
    const invitation = JSON.parse(rawText);

    const res = await fetch('/connections/holder/receive-invitation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ invitation })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);

    const result = await res.json();
    successMsg.textContent = `Invitation received! Connection ID: ${result.connection_id || 'unknown'}`;
    successMsg.classList.remove('hidden');
    setTimeout(() => successMsg.classList.add('hidden'), 5000);

    input.value = '';

  } catch (err) {
    errorMsg.textContent = `Receive failed: ${err.message}`;
    errorMsg.classList.remove('hidden');
  }
});
