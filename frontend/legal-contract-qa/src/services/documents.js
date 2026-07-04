const STORAGE_KEY = 'contractai_documents';

let idCounter = parseInt(localStorage.getItem('contractai_doc_counter') || '0', 10);

function nextId() {
  idCounter += 1;
  localStorage.setItem('contractai_doc_counter', idCounter.toString());
  return `doc_${idCounter}`;
}

export function getDocuments() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveDocuments(docs) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(docs));
}

export function addDocument(name) {
  const docs = getDocuments();
  const doc = {
    id: nextId(),
    name,
    status: 'indexed',
    uploadedAt: new Date().toISOString().slice(0, 10),
    createdAt: Date.now(),
  };
  docs.unshift(doc);
  saveDocuments(docs);
  return doc;
}

export function removeDocument(id) {
  let docs = getDocuments();
  docs = docs.filter((d) => d.id !== id);
  saveDocuments(docs);
  return docs;
}

export function updateDocumentStatus(id, status) {
  const docs = getDocuments();
  const doc = docs.find((d) => d.id === id);
  if (doc) {
    doc.status = status;
    saveDocuments(docs);
  }
  return docs;
}

export async function fetchDocuments() {
  return getDocuments();
}
