import { supabase } from '../utils/supabase';

function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return null;
  if (bytes > 1024 * 1024 * 1024) {
    return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB';
  }
  if (bytes > 1024 * 1024) {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  }
  return (bytes / 1024).toFixed(1) + ' KB';
}

async function getAuthHeaders() {
  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchDashboardStats() {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch('/documents', { headers });

    if (!response.ok) {
      return emptyDashboardResponse();
    }

    const data = await response.json();
    const count = data.length;
    const totalBytes = data.reduce((sum, d) => sum + (d.file_size || 0), 0);

    const mapped = data.map((doc) => ({
      id: doc.id,
      documentId: doc.document_id,
      name: doc.filename,
      uploadedAt: new Date(doc.uploaded_at).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
      }),
      createdAt: new Date(doc.uploaded_at).getTime(),
      status: doc.indexed ? 'indexed' : 'processing',
      rawSize: doc.file_size,
      size: doc.file_size > 1024 * 1024
        ? (doc.file_size / 1024 / 1024).toFixed(2) + ' MB'
        : (doc.file_size / 1024).toFixed(1) + ' KB',
    }));

    const activityItems = mapped.slice(0, 10).map((doc) => ({
      id: `activity-${doc.id}`,
      action: `Uploaded ${doc.name}`,
      timestamp: doc.uploadedAt,
    }));

    return {
      contractsUploaded: count || null,
      documentsIndexed: count || null,
      storageUsed: formatBytes(totalBytes),
      documents: mapped,
      activity: activityItems,
      appStatus: {
        authentication: 'connected',
        documents: mapped.length > 0 ? 'ready' : 'connected',
        aiAssistant: 'available',
        database: 'checking',
      },
    };
  } catch {
    return emptyDashboardResponse();
  }
}

function emptyDashboardResponse() {
  return {
    contractsUploaded: null,
    documentsIndexed: null,
    storageUsed: null,
    documents: [],
    activity: [],
    appStatus: null,
  };
}

export async function fetchRecentDocuments() {
  const stats = await fetchDashboardStats();
  return stats.documents.slice(0, 5);
}

export async function fetchRecentActivity() {
  const stats = await fetchDashboardStats();
  return stats.activity;
}

export async function fetchApplicationStatus() {
  const stats = await fetchDashboardStats();
  return stats.appStatus;
}
