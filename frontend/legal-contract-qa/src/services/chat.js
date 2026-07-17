import { supabase } from '../utils/supabase';

export async function sendMessage(question, documentId = null) {
  const body = { query: question };
  if (documentId) {
    body.document_id = documentId;
  }

  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token;
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch('/chat/ask', {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error('Failed to get response from the server');
  }
  return response.json();
}
