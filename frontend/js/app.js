const API = '/api/v1';
let activeDocumentId = null;
let activeDocumentName = '';

// ── Upload ────────────────────────────────────────────────────────────────────

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('drop-zone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
}

document.getElementById('drop-zone').addEventListener('dragover', (e) => {
  e.preventDefault();
  e.currentTarget.classList.add('drag-over');
});
document.getElementById('drop-zone').addEventListener('dragleave', (e) => {
  e.currentTarget.classList.remove('drag-over');
});

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) uploadFile(file);
}

async function uploadFile(file) {
  showUploadProgress(file.name);

  const formData = new FormData();
  formData.append('file', file);

  try {
    setProgress(30, 'Uploading...');
    const res = await fetch(`${API}/upload`, { method: 'POST', body: formData });
    setProgress(70, 'Processing...');

    const json = await res.json();
    if (!res.ok || json.status === 'error') {
      showUploadError(json.error?.message || 'Upload failed.');
      return;
    }

    setProgress(100, 'Ready!');
    const doc = json.data;
    activeDocumentId = doc.document_id;
    activeDocumentName = doc.filename;

    setTimeout(() => {
      hideUploadProgress();
      addDocToList(doc);
      showChatScreen(doc);
    }, 400);

  } catch (err) {
    showUploadError('Network error: ' + err.message);
  }
}

function setProgress(pct, text) {
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('upload-pct').textContent = pct + '%';
  document.getElementById('upload-status-text').textContent = text;
}

function showUploadProgress(name) {
  document.getElementById('upload-error').classList.add('hidden');
  document.getElementById('upload-filename').textContent = name;
  document.getElementById('upload-progress').classList.remove('hidden');
  setProgress(10, 'Uploading...');
}

function hideUploadProgress() {
  document.getElementById('upload-progress').classList.add('hidden');
  document.getElementById('upload-error').classList.add('hidden');
}

function showUploadError(msg) {
  document.getElementById('upload-progress').classList.add('hidden');
  const el = document.getElementById('upload-error');
  el.textContent = '⚠ ' + msg;
  el.classList.remove('hidden');
}

function addDocToList(doc) {
  document.getElementById('doc-list-section').classList.remove('hidden');
  const list = document.getElementById('doc-list');
  const div = document.createElement('div');
  div.id = `doc-${doc.document_id}`;
  div.className = 'flex items-center justify-between bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm';
  div.innerHTML = `
    <button onclick="switchDocument('${doc.document_id}','${escHtml(doc.filename)}')"
      class="flex items-center gap-3 text-left min-w-0 flex-1">
      <span class="text-brand text-lg">📄</span>
      <div class="min-w-0">
        <p class="font-medium text-gray-800 truncate">${escHtml(doc.filename)}</p>
        <p class="text-gray-400 text-xs">${doc.chunk_count} chunks · ${doc.page_count} pages</p>
      </div>
    </button>
    <button onclick="deleteDocument('${doc.document_id}')"
      class="ml-3 text-gray-300 hover:text-red-400 transition-colors shrink-0" title="Delete">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
      </svg>
    </button>
  `;
  list.prepend(div);
}

async function deleteDocument(docId) {
  if (!confirm('Delete this document and its vectors?')) return;
  try {
    const res = await fetch(`${API}/documents/${docId}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      document.getElementById(`doc-${docId}`)?.remove();
      if (activeDocumentId === docId) showUploadScreen();
      const list = document.getElementById('doc-list');
      if (!list.children.length) document.getElementById('doc-list-section').classList.add('hidden');
    }
  } catch (err) {
    alert('Delete failed: ' + err.message);
  }
}

function switchDocument(docId, filename) {
  activeDocumentId = docId;
  activeDocumentName = filename;
  showChatScreen({ document_id: docId, filename, chunk_count: '', page_count: '' });
  clearMessages();
}

// ── Screens ───────────────────────────────────────────────────────────────────

function showChatScreen(doc) {
  document.getElementById('upload-screen').classList.add('hidden');
  const chat = document.getElementById('chat-screen');
  chat.classList.remove('hidden');
  document.getElementById('chat-doc-name').textContent = doc.filename;
  document.getElementById('chat-doc-info').textContent =
    doc.chunk_count ? `${doc.chunk_count} chunks indexed · ${doc.page_count} pages` : '';
  document.getElementById('question-input').focus();
}

function showUploadScreen() {
  document.getElementById('chat-screen').classList.add('hidden');
  document.getElementById('upload-screen').classList.remove('hidden');
  hideUploadProgress();
  document.getElementById('file-input').value = '';
}

function clearMessages() {
  document.getElementById('messages').innerHTML = '';
}

// ── Q&A ───────────────────────────────────────────────────────────────────────

function handleEnter(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    askQuestion();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}

async function askQuestion() {
  const input = document.getElementById('question-input');
  const question = input.value.trim();
  if (!question || !activeDocumentId) return;

  input.value = '';
  input.style.height = 'auto';

  appendUserMessage(question);
  const answerId = appendSkeletonAnswer();

  try {
    const res = await fetch(`${API}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: activeDocumentId, question }),
    });
    const json = await res.json();

    if (!res.ok || json.status === 'error') {
      replaceSkeletonWithError(answerId, json.error?.message || 'Query failed.');
      return;
    }

    replaceSkeletonWithAnswer(answerId, json.data);
  } catch (err) {
    replaceSkeletonWithError(answerId, 'Network error: ' + err.message);
  }
}

function appendUserMessage(text) {
  const msgs = document.getElementById('messages');
  const div = document.createElement('div');
  div.className = 'flex justify-end fade-in';
  div.innerHTML = `
    <div class="max-w-[78%] bg-brand text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed">
      ${escHtml(text)}
    </div>`;
  msgs.appendChild(div);
  div.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function appendSkeletonAnswer() {
  const id = 'ans-' + Date.now();
  const msgs = document.getElementById('messages');
  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex gap-3 fade-in';
  div.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-brand-light flex items-center justify-center shrink-0 mt-1">
      <svg class="w-4 h-4 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586..."/>
      </svg>
    </div>
    <div class="flex-1">
      <div class="skeleton h-4 w-3/4 mb-2"></div>
      <div class="skeleton h-4 w-full mb-2"></div>
      <div class="skeleton h-4 w-2/3"></div>
    </div>`;
  msgs.appendChild(div);
  div.scrollIntoView({ behavior: 'smooth', block: 'end' });
  return id;
}

function replaceSkeletonWithAnswer(id, data) {
  const el = document.getElementById(id);
  if (!el) return;

  const answerHtml = renderMarkdown(data.answer);
  const citationsHtml = renderCitations(data.citations);
  const meta = `
    <p class="text-xs text-gray-400 mt-3">
      ${data.model_used} · ${data.chunks_retrieved} chunks · ${data.latency_ms}ms
    </p>`;

  el.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-brand-light flex items-center justify-center shrink-0 mt-1">
      <svg class="w-4 h-4 text-brand" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
    </div>
    <div class="flex-1 min-w-0">
      <div class="answer-content text-sm text-gray-800 leading-relaxed">${answerHtml}</div>
      ${meta}
      ${citationsHtml}
    </div>`;
  el.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

function replaceSkeletonWithError(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `<div class="text-red-500 text-sm bg-red-50 rounded-xl px-4 py-3">⚠ ${escHtml(msg)}</div>`;
}

// ── Render helpers ────────────────────────────────────────────────────────────

function renderMarkdown(text) {
  // Replace [SOURCE N] with clickable badges
  let html = escHtml(text)
    .replace(/\[SOURCE (\d+)\]/g, (_, n) =>
      `<span class="source-badge" onclick="scrollToCitation(${n})" title="Source ${n}">${n}</span>`
    );

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Code blocks
  html = html.replace(/```[\s\S]*?```/g, m => {
    const inner = m.slice(3, -3).replace(/^[a-z]+\n/, '');
    return `<pre><code>${inner}</code></pre>`;
  });
  // Bullet lists
  html = html.replace(/((?:^- .+$\n?)+)/gm, match => {
    const items = match.trim().split('\n').map(l => `<li>${l.replace(/^- /, '')}</li>`).join('');
    return `<ul>${items}</ul>`;
  });
  // Numbered lists
  html = html.replace(/((?:^\d+\. .+$\n?)+)/gm, match => {
    const items = match.trim().split('\n').map(l => `<li>${l.replace(/^\d+\. /, '')}</li>`).join('');
    return `<ol>${items}</ol>`;
  });
  // Paragraphs
  html = html.split('\n\n').map(p => p.trim() ? `<p>${p}</p>` : '').join('');

  return html;
}

function renderCitations(citations) {
  if (!citations || !citations.length) return '';

  const cards = citations.map((c, i) => `
    <div id="citation-${i+1}" class="citation-card">
      <div class="flex items-start gap-2">
        <span class="source-badge shrink-0">${i+1}</span>
        <div class="min-w-0">
          <p class="font-medium text-gray-700 truncate">${escHtml(c.source_filename)}</p>
          <p class="text-gray-400 text-xs">Page ${c.page_number} · score ${c.similarity_score.toFixed(2)}</p>
          <p class="text-gray-600 mt-1 line-clamp-3">${escHtml(c.excerpt)}</p>
        </div>
      </div>
    </div>`).join('');

  return `
    <details class="mt-3" open>
      <summary class="cursor-pointer text-xs font-semibold text-gray-500 uppercase tracking-wide hover:text-brand transition-colors">
        Sources (${citations.length})
      </summary>
      <div class="mt-2 space-y-2">${cards}</div>
    </details>`;
}

function scrollToCitation(n) {
  const el = document.getElementById(`citation-${n}`);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Load existing docs on startup
(async () => {
  try {
    const res = await fetch(`${API}/documents`);
    const json = await res.json();
    if (json.status === 'success' && json.data.documents.length > 0) {
      json.data.documents.forEach(addDocToList);
    }
  } catch (_) {}
})();
