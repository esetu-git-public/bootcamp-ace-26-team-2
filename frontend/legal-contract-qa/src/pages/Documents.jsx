import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Upload, Trash2, Download } from 'lucide-react';
import Button from '../components/ui/Button';
import DashboardSection from '../components/dashboard/DashboardSection';
import EmptyState from '../components/dashboard/EmptyState';
import { getDocuments, addDocument, removeDocument } from '../services/documents';

export default function Documents() {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    setDocuments(getDocuments());
  }, []);

  function refresh() {
    setDocuments(getDocuments());
  }

  function handleUpload() {
    const name = `Contract - ${new Date().toLocaleDateString()}`;
    addDocument(name);
    refresh();
  }

  function handleDelete(id) {
    removeDocument(id);
    refresh();
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-text mb-1">Documents</h1>
          <p className="text-muted">Manage your uploaded legal contracts.</p>
        </div>
        <Button icon={Upload} onClick={handleUpload}>Upload Contract</Button>
      </div>

      <DashboardSection title={`All Documents (${documents.length})`}>
        {documents.length > 0 ? (
          <div className="divide-y divide-border">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="py-3 flex items-center justify-between"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-xl bg-card flex items-center justify-center shrink-0">
                    <FileText className="w-5 h-5 text-muted" />
                  </div>
                  <div className="min-w-0">
                    <span className="text-sm font-medium truncate block">
                      {doc.name}
                    </span>
                    <span className="text-xs text-muted">{doc.uploadedAt}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      doc.status === 'indexed'
                        ? 'text-success bg-success/10'
                        : doc.status === 'processing'
                        ? 'text-warning bg-warning/10'
                        : doc.status === 'failed'
                        ? 'text-error bg-error/10'
                        : 'text-muted bg-card-hover'
                    }`}
                  >
                    {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                  </span>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-2 text-muted-dark hover:text-error rounded-lg hover:bg-error/5 transition-all"
                    aria-label="Delete document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={FileText}
            title="No contracts uploaded yet"
            description="Upload your first legal contract to begin asking AI-powered questions."
            action={
              <Button variant="outline" icon={Upload} onClick={handleUpload}>
                Upload Your First Contract
              </Button>
            }
          />
        )}
      </DashboardSection>
    </motion.div>
  );
}
