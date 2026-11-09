const $ = (id) => document.getElementById(id);
const api = async (path, options = {}) => {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || data.error || `Request failed (${response.status})`);
  return data;
};
function message(id, text = "", type = "") { const el = $(id); el.textContent = text; el.className = `message ${type}`; }
function escapeHtml(value = "") { return String(value).replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch])); }

async function checkHealth() {
  try { await api("/health"); $("apiStatus").textContent = "API connected"; $("statusDot").classList.add("online"); }
  catch { $("apiStatus").textContent = "API unavailable"; $("statusDot").classList.remove("online"); }
}

$("fileInput").addEventListener("change", () => {
  const file = $("fileInput").files[0];
  $("fileLabel").textContent = file ? file.name : "Choose a document to upload";
});

$("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("fileInput").files[0];
  if (!file) return message("uploadMessage", "Choose a PDF, DOCX or TXT file.", "error");
  if (file.size > 20 * 1024 * 1024) return message("uploadMessage", "File exceeds the 20 MB limit.", "error");
  const button = $("uploadButton"); button.disabled = true; button.textContent = "Indexing…";
  message("uploadMessage", "Extracting text, creating chunks and embeddings. Large files may take a moment.");
  try {
    const form = new FormData(); form.append("file", file);
    const result = await api("/documents/upload", { method: "POST", body: form });
    message("uploadMessage", `Indexed ${result.filename}: ${result.chunks} chunks created.`, "success");
    $("uploadForm").reset(); $("fileLabel").textContent = "Choose a document to upload";
    await loadDocuments();
  } catch (error) { message("uploadMessage", error.message, "error"); }
  finally { button.disabled = false; button.textContent = "Upload document"; }
});

$("searchForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = $("queryInput").value.trim(); if (!query) return;
  const button = $("searchButton"); button.disabled = true; button.textContent = "Searching…";
  message("searchMessage", "Embedding your query and searching the vector index…");
  $("results").innerHTML = "";
  try {
    const data = await api("/search", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query, top_k: Number($("topK").value) }) });
    message("searchMessage", `${data.results.length} relevant passage(s) found. Retrieval only — no LLM-generated answer.`, "success");
    if (!data.results.length) { $("results").innerHTML = '<div class="empty-state">No matching passages found. Upload a document first.</div>'; return; }
    $("results").innerHTML = data.results.map((item, index) => `
      <article class="result-card">
        <div class="result-top"><span>MATCH ${String(index + 1).padStart(2, "0")} · ${escapeHtml(item.source || "Unknown source")}</span><span class="score">${(item.similarity_score * 100).toFixed(1)}% similarity</span></div>
        <p>${escapeHtml(item.content)}</p>
        <div class="result-meta">Page ${item.page ?? "—"} · Chunk ${item.chunk_index} · ID ${escapeHtml(item.document_id)}</div>
      </article>`).join("");
  } catch (error) { message("searchMessage", error.message, "error"); $("results").innerHTML = '<div class="empty-state">Search could not be completed.</div>'; }
  finally { button.disabled = false; button.textContent = "Search"; }
});

async function loadDocuments() {
  const container = $("documents"); container.innerHTML = '<div class="empty-state">Loading documents…</div>';
  try {
    const data = await api("/documents");
    if (!data.documents.length) { container.innerHTML = '<div class="empty-state">No documents indexed yet. Upload your first document above.</div>'; return; }
    container.innerHTML = data.documents.map(doc => `
      <div class="document-row">
        <div class="document-info"><div class="document-name">${escapeHtml(doc.filename)}</div><div class="document-details">${doc.chunks} chunks · ${doc.pages_with_text} pages with text · ${escapeHtml(doc.document_id)}</div></div>
        <button class="delete-button" data-delete="${escapeHtml(doc.document_id)}" type="button">Delete</button>
      </div>`).join("");
    container.querySelectorAll("[data-delete]").forEach(button => button.addEventListener("click", async () => {
      if (!confirm("Delete this document and its indexed chunks?")) return;
      button.disabled = true;
      try { await api(`/documents/${encodeURIComponent(button.dataset.delete)}`, { method: "DELETE" }); await loadDocuments(); }
      catch (error) { alert(error.message); button.disabled = false; }
    }));
  } catch (error) { container.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`; }
}

$("refreshButton").addEventListener("click", loadDocuments);
checkHealth(); loadDocuments();
