export async function sendMessage(question) {
  const response = await fetch('/chat/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error('Failed to get response from the server');
  }
  return response.json();
}
