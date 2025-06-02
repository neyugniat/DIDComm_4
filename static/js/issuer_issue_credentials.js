document.addEventListener("DOMContentLoaded", () => {
  const issueButton = document.getElementById("issue-credential");
  const connectionSelect = document.getElementById("connection-select");
  const successDiv = document.getElementById("success-message");
  const errorDiv = document.getElementById("generic-error");

  const requestData = {
    auto_remove: false,
    comment: "Cấp bằng đại học cho Nguyễn Văn A",
    connection_id: "",
    credential_preview: {
      "@type": "issue-credential/2.0/credential-preview",
      attributes: [
        { name: "ho_ten", value: "Nguyễn Văn A" },
        { name: "ngay_sinh", value: "2003-07-16" },
        { name: "ngay_tot_nghiep", value: "2025-05-31" },
        { name: "loai_bang", value: "Bằng cử nhân" },
        { name: "unixdob", value: "12243" },
        { name: "mssv", value: "AT18N0127" },
        { name: "truong", value: "HVKTMM" },
        { name: "chuyen_nganh", value: "ATTT" },
        { name: "gpa", value: "360" },
        { name: "trang_thai_tot_nghiep", value: "1" }
      ],
    },
    filter: {
      indy: {
        cred_def_id: "DSs1t1E3pizf86GqTXonU5:3:CL:91:support_revocation",
        issuer_did: "DSs1t1E3pizf86GqTXonU5",
        schema_id: "DSs1t1E3pizf86GqTXonU5:2:Bang_tot_nghiep:1.0",
        schema_issuer_did: "DSs1t1E3pizf86GqTXonU5",
        schema_name: "Bang_tot_nghiep",
        schema_version: "1.0"
      }
    },
    trace: false
  };


  function createToast(content, type = "error") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `p-4 rounded-lg shadow-lg max-w-lg transition-opacity duration-300 ${
      type === "error" ? "bg-red-100 text-red-500" : "bg-green-600 text-white"
    }`;
    toast.textContent = content;
    toast.style.opacity = "0";
    container.appendChild(toast);
    setTimeout(() => (toast.style.opacity = "1"), 100);
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.parentNode?.removeChild(toast), 300);
    }, 3000);
  }

  function showSuccess(message) {
    if (successDiv) {
      successDiv.textContent = message;
      successDiv.classList.remove("hidden");
    }
    if (errorDiv) errorDiv.classList.add("hidden");
    createToast(message, "success");
  }

  function showError(message) {
    if (errorDiv) {
      errorDiv.textContent = message;
      errorDiv.classList.remove("hidden");
    }
    if (successDiv) successDiv.classList.add("hidden");
    createToast(message, "error");
  }

  function populateCredentialPreview() {
    const previewTable = document.getElementById("credential-attributes");
    if (!previewTable) return;
    previewTable.innerHTML = "";

    requestData.credential_preview.attributes.forEach((attr) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td class="px-4 py-2 border-b font-medium">${attr.name}</td>
        <td class="px-4 py-2 border-b">${attr.value}</td>
      `;
      previewTable.appendChild(row);
    });
  }

  async function loadConnections() {
    try {
      const res = await fetch("/connections/issuer");
      const data = await res.json();
      const options = data.results || [];

      connectionSelect.innerHTML = "";
      if (options.length === 0) {
        connectionSelect.innerHTML = '<option disabled selected>Không có connection nào.</option>';
        return;
      }

      options.forEach((conn) => {
        const option = document.createElement("option");
        option.value = conn.connection_id;
        option.textContent = `${conn.their_label || "Unknown"} (${conn.connection_id.slice(0, 6)}...)`;
        connectionSelect.appendChild(option);
      });
    } catch (err) {
      showError("Không thể tải danh sách connections.");
      console.error(err);
    }
  }

  async function pollCredentialStatus(credExId, maxRetries = 10, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      const res = await fetch(`/issue-credentials/fetch_record/ISSUER/${credExId}`);
      if (!res.ok) throw new Error("Failed to fetch credential record");
      const data = await res.json();

      if (data.cred_ex_record?.state === "done") return true;

      await new Promise((resolve) => setTimeout(resolve, delay));
    }
    return false;
  }

  issueButton.addEventListener("click", async () => {
    const selectedConnId = connectionSelect.value;
    if (!selectedConnId) {
      showError("Vui lòng chọn một connection để cấp bằng.");
      return;
    }

    requestData.connection_id = selectedConnId;

    try {
      const res = await fetch("/issue-credentials/send_credential", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });

      if (!res.ok) throw new Error(`Failed to issue credential: ${res.status}`);
      const result = await res.json();
      const credExId = result.cred_ex_id;

      const isDone = await pollCredentialStatus(credExId);
      if (isDone) {
        showSuccess(`Cấp bằng thành công! Exchange ID: ${credExId}`);
      } else {
        throw new Error("Quá thời gian chờ xác nhận cấp bằng.");
      }
    } catch (err) {
      showError(`Lỗi: ${err.message}`);
    }
  });

  populateCredentialPreview();
  loadConnections();
});
