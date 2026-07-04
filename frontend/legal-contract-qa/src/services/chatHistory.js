const STORAGE_KEY = 'contractai_conversations';
const ACTIVE_KEY = 'contractai_active_conversation';

export function getConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveConversations(conversations) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

export function getActiveConversationId() {
  return localStorage.getItem(ACTIVE_KEY);
}

export function setActiveConversationId(id) {
  if (id) {
    localStorage.setItem(ACTIVE_KEY, id);
  } else {
    localStorage.removeItem(ACTIVE_KEY);
  }
}

export function createConversation() {
  const conversations = getConversations();
  const id = `conv_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
  const conversation = {
    id,
    title: 'New Chat',
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  conversations.unshift(conversation);
  saveConversations(conversations);
  setActiveConversationId(id);
  return conversation;
}

export function addMessage(conversationId, message) {
  const conversations = getConversations();
  const conv = conversations.find((c) => c.id === conversationId);
  if (!conv) return null;

  conv.messages.push(message);
  conv.updatedAt = Date.now();

  if (message.role === 'user' && conv.title === 'New Chat') {
    conv.title = message.content.slice(0, 60) + (message.content.length > 60 ? '...' : '');
  }

  saveConversations(conversations);
  return conv;
}

export function deleteConversation(id) {
  let conversations = getConversations();
  conversations = conversations.filter((c) => c.id !== id);
  saveConversations(conversations);

  const activeId = getActiveConversationId();
  if (activeId === id) {
    const nextId = conversations[0]?.id || null;
    setActiveConversationId(nextId);
  }
  return conversations;
}

export function getConversation(id) {
  const conversations = getConversations();
  return conversations.find((c) => c.id === id) || null;
}
