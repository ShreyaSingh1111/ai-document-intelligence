const API_BASE = "http://127.0.0.1:8000";

async function uploadDocument() {
  const fileInput = document.getElementById("fileInput");
  const docType = document.getElementById("documentType").value;
  const msgEl = document.getElementById("uploadMsg");

  if (!fileInput.files.length) {
    msgEl.textContent = "Please choose a file first.";
    msgEl.className = "msg error";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  msgEl.textContent = "Processing... this can take a few seconds (OCR + AI extraction).";
  msgEl.className = "msg";

  try {
    const res = await fetch(`${API_BASE}/documents/upload?document_type=${encodeURIComponent(docType)}`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (!res.ok) {
      msgEl.textContent = "Error: " + (data.detail || "Upload failed.");
      msgEl.className = "msg error";
      return;
    }

    msgEl.textContent = `Uploaded "${data.document_name}" - status: ${data.processing_status}`;
    msgEl.className = "msg ok";
    fileInput.value = "";
    loadDocuments();
  } catch (err) {
    msgEl.textContent = "Network error: " + err.message;
    msgEl.className = "msg error";
  }
}

async function loadDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  const docs = await res.json();

  const tbody = document.getElementById("docTableBody");
  tbody.innerHTML = "";

  docs.forEach(doc => {
    const tr = document.createElement("tr");
    tr.onclick = () => openDetail(doc.document_name);
    tr.innerHTML = `
      <td>${doc.document_name}</td>
      <td>${doc.document_type}</td>
      <td><span class="status status-${doc.processing_status}">${doc.processing_status}</span></td>
      <td>${new Date(doc.created_at).toLocaleString()}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function openDetail(name) {
  const res = await fetch(`${API_BASE}/documents/by-name/${encodeURIComponent(name)}`);
  const doc = await res.json();

  document.getElementById("detailPanel").style.display = "block";
  document.getElementById("detailTitle").textContent = `${doc.document_name} (${doc.document_type}) - ${doc.processing_status}`;

  const fieldsGrid = document.getElementById("fieldsGrid");
  fieldsGrid.innerHTML = "";
  const data = doc.extracted_data || {};

  Object.keys(data).forEach(key => {
    if (key === "line_items") return;
    const value = data[key];
    const displayValue = (value === null || value === undefined || value === "")
      ? '<span class="missing">missing</span>'
      : value;
    fieldsGrid.innerHTML += `<div><strong>${key}</strong>: ${displayValue}</div>`;
  });

  const lineItemsBody = document.getElementById("lineItemsBody");
  lineItemsBody.innerHTML = "";
  (data.line_items || []).forEach(item => {
    lineItemsBody.innerHTML += `
      <tr>
        <td>${item.description ?? ""}</td>
        <td>${item.quantity ?? ""}</td>
        <td>${item.unit_price ?? ""}</td>
        <td>${item.amount ?? ""}</td>
      </tr>
    `;
  });

  const validationChecks = document.getElementById("validationChecks");
  validationChecks.innerHTML = "";
  const validation = doc.validation || {};
  const checks = validation.checks || [];

  if (checks.length === 0) {
    validationChecks.innerHTML = `<div class="check-row check-SKIPPED">No validation checks were applicable for this document.</div>`;
  }

  checks.forEach(check => {
    const status = check.status || "SKIPPED";
    validationChecks.innerHTML += `
      <div class="check-row check-${status}">
        <strong>${check.name}</strong> - ${status}<br/>
        Formula: ${check.formula}<br/>
        Calculated: ${check.calculated_value} | Reported: ${check.reported_value} | Variance: ${check.variance}
      </div>
    `;
  });

  if (validation.issues && validation.issues.length) {
    validationChecks.innerHTML += `<div class="check-row check-FAIL"><strong>Issues:</strong> ${validation.issues.join("; ")}</div>`;
  }

  document.getElementById("rawJson").textContent = JSON.stringify(doc, null, 2);
}

function closeDetail() {
  document.getElementById("detailPanel").style.display = "none";
}

loadDocuments();
