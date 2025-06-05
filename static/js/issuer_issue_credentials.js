// DOM elements
const toastMessage = document.getElementById('toast-message');
const toastClose = document.getElementById('toast-close');
const errorMessage = document.getElementById('error-message');
const credDefIdSelect = document.getElementById('cred-def-id');
const connectionIdSelect = document.getElementById('connection-id');
const commentInput = document.getElementById('comment');
const attributesContainer = document.getElementById('attributes-container');
const attributesList = document.getElementById('attributes-list');
const issueCredentialBtn = document.getElementById('issueCredential');

// Pre-defined values keyed by schemaName instead of cred_def_id
const defaultValues = {
  "Bang_tot_nghiep": {
    attributes: {
      ngay_tot_nghiep: "2025-05-31",
      trang_thai_tot_nghiep: "1",
      mssv: "AT18N0127",
      gpa: "360",
      chuyen_nganh: "ATTT",
      ngay_sinh: "2003-07-16",
      truong: "HVKTMM",
      unixdob: "12243",
      ho_ten: "Nguyễn Văn A",
      loai_bang: "Bằng cử nhân"
    }
  },
  "Can_Cuoc_Cong_Dan": {
    attributes: {
      so_cccd: "123456789",
      ho_ten: "Trần Thị B",
      ngay_sinh: "1995-04-20",
      gioi_tinh: "Nữ",
      quoc_tich: "Việt Nam",
      que_quan: "TP. Hồ Chí Minh",
      noi_thuong_tru: "123 Cộng Hoà, Tân Bình",
      ngay_cap: "2025-06-02",
      noi_cap: "Cục Cảnh sát DKQL Cư trú",
      unixdob: "11000"
    }
  }
};

// Handle toast close
toastClose.addEventListener('click', () => {
  toastMessage.classList.add('hidden');
});

// Fetch Credential Definitions and populate the dropdown
async function populateCredDefDropdown() {
  try {
    const response = await fetch('/credential-definitions/issuer');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const credDefs = await response.json();
    for (const credDef of credDefs) {
      console.log("Cred: ", credDef);
      const credDefId = credDef.credential_definition_id;
      const option = document.createElement('option');
      option.value = credDefId;

      // Fetch schemaId from /credential-definitions/issuer/{cred_def_id}
      const detailsResponse = await fetch(`/credential-definitions/issuer/${encodeURIComponent(credDefId)}`);
      if (!detailsResponse.ok) {
        throw new Error(`HTTP error fetching cred def details! status: ${detailsResponse.status}`);
      }
      const details = await detailsResponse.json();
      const schemaId = details.credential_definition.schemaId;

      // Fetch schema details from /schemas/issuer/{schemaId}
      const schemaResponse = await fetch(`/schemas/issuer/${schemaId}`);
      if (!schemaResponse.ok) {
        throw new Error(`HTTP error fetching schema! status: ${schemaResponse.status}`);
      }
      const schemaData = await schemaResponse.json();
      const schema = schemaData.schema;

      // console.log("schema.id: ", schema.id)
      option.textContent = schema.id;

      option.dataset.schemaId = schema.id;
      option.dataset.schemaName = schema.name;
      option.dataset.schemaVersion = schema.version;
      option.dataset.attributes = JSON.stringify(schema.attrNames);
      credDefIdSelect.appendChild(option);
    }
  } catch (error) {
    errorMessage.textContent = `Error fetching credential definitions: ${error.message}`;
    errorMessage.classList.remove('hidden');
    showToast(`Error fetching credential definitions: ${error.message}`, true);
  }
}

// Fetch Connections and populate the dropdown
async function populateConnectionDropdown() {
  try {
    const response = await fetch('/connections/issuer');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const connections = data.results;

    connections.forEach(conn => {
      const option = document.createElement('option');
      option.value = conn.connection_id;
      option.textContent = `${conn.their_label} (${conn.connection_id})`;
      connectionIdSelect.appendChild(option);
    });
  } catch (error) {
    errorMessage.textContent = `Error fetching connections: ${error.message}`;
    errorMessage.classList.remove('hidden');
    showToast(`Error fetching connections: ${error.message}`, true);
  }
}

// Fetch Issuer DID
async function fetchIssuerDid() {
  try {
    const response = await fetch('/did/issuer');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    // console.log("data: ", data);
    return data.did;
  } catch (error) {
    throw new Error(`Failed to fetch Issuer DID: ${error.message}`);
  }
}

// Populate attributes form based on schema with pre-defined values
function populateAttributesForm(attributes, schemaName) {
  attributesList.innerHTML = ''; // Clear previous attributes
  const defaults = defaultValues[schemaName]?.attributes || {};
  
  attributes.forEach(attr => {
    const div = document.createElement('div');
    div.className = 'mb-2';
    const defaultValue = defaults[attr] || '';
    div.innerHTML = `
      <label class="block text-sm font-medium text-gray-700 mb-1">${attr}</label>
      <input
        type="text"
        data-attribute="${attr}"
        value="${defaultValue}"
        placeholder="Enter value for ${attr}"
        class="p-2 border rounded-lg w-full"
      />
    `;
    attributesList.appendChild(div);
  });
  attributesContainer.classList.remove('hidden');
}

// Handle credential definition selection
credDefIdSelect.addEventListener('change', () => {
  const selectedOption = credDefIdSelect.options[credDefIdSelect.selectedIndex];
  const schemaName = selectedOption.dataset.schemaName;
  const attributes = selectedOption.dataset.attributes ? JSON.parse(selectedOption.dataset.attributes) : [];
  if (attributes.length > 0) {
    populateAttributesForm(attributes, schemaName);
  } else {
    attributesContainer.classList.add('hidden');
  }
});

// Issue Credential
issueCredentialBtn.addEventListener('click', async () => {
  try {
    const credDefId = credDefIdSelect.value;
    const connectionId = connectionIdSelect.value;
    const comment = commentInput.value.trim();
    const selectedOption = credDefIdSelect.options[credDefIdSelect.selectedIndex];
    const schemaId = selectedOption.dataset.schemaId;
    const schemaName = selectedOption.dataset.schemaName;
    const schemaVersion = selectedOption.dataset.schemaVersion;

    if (!credDefId || !connectionId || !schemaId) {
      throw new Error('Please select a credential definition and a connection');
    }

    const issuerDid = await fetchIssuerDid();

    // Collect attribute values
    const attributeInputs = attributesList.querySelectorAll('input');
    const attributes = Array.from(attributeInputs).map(input => ({
      name: input.dataset.attribute,
      value: input.value.trim()
    }));

    if (attributes.some(attr => !attr.value)) {
      throw new Error('Please fill in all attribute values');
    }

    const requestData = {
      auto_remove: false,
      comment: comment || `Cấp chứng chỉ cho schema ${schemaName}`,
      connection_id: connectionId,
      credential_preview: {
        "@type": "issue-credential/2.0/credential-preview",
        attributes: attributes
      },
      filter: {
        indy: {
          cred_def_id: credDefId,
          issuer_did: issuerDid,
          schema_id: schemaId,
          schema_issuer_did: issuerDid,
          schema_name: schemaName,
          schema_version: schemaVersion
        }
      },
      trace: false
    };

    const response = await fetch('/issue-credentials/send_credential', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    showToast(`Credential offer sent successfully!`);
    errorMessage.classList.add('hidden');

    // Reset form
    credDefIdSelect.value = '';
    connectionIdSelect.value = '';
    commentInput.value = '';
    attributesContainer.classList.add('hidden');
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

// Populate dropdowns on page load
document.addEventListener('DOMContentLoaded', () => {
  populateCredDefDropdown();
  populateConnectionDropdown();
});