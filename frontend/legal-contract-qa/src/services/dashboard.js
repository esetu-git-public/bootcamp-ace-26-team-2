import { getDocuments } from '../services/documents';

// TODO: Replace with actual API integration

export async function fetchDashboardStats() {
  const docs = getDocuments();
  return {
    contractsUploaded: docs.length,
    questionsAsked: null,
    recentUploads: docs.filter((d) => {
      const daysAgo = (Date.now() - d.createdAt) / 86400000;
      return daysAgo < 7;
    }).length,
  };
}

export async function fetchRecentDocuments() {
  return getDocuments().slice(0, 5);
}

export async function fetchRecentActivity() {
  // TODO: Connect to backend API endpoint for recent activity
  // const response = await fetch('/api/dashboard/activity');
  // return response.json();
  return [];
}
