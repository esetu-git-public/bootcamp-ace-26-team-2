import { supabase } from '../utils/supabase';
import { getDocuments } from './documents';
import { getConversations } from './chatHistory';

const STORAGE_KEY = 'contractai_profile';

function getStoredProfile() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveStoredProfile(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export async function fetchProfile() {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      const stored = getStoredProfile() || {};
      return {
        id: user.id,
        name: user.user_metadata?.full_name || stored.name || null,
        email: user.email || null,
        role: stored.role || 'User',
        memberSince: user.created_at || stored.memberSince || null,
        lastLogin: stored.lastLogin || null,
        emailVerified: user.email_confirmed_at ? true : false,
        accountStatus: stored.accountStatus || 'active',
        passwordLastChanged: stored.passwordLastChanged || null,
        twoFactorEnabled: stored.twoFactorEnabled || false,
      };
    }
  } catch {
    // fall through to localStorage
  }

  const stored = getStoredProfile();
  if (stored) {
    return stored;
  }

  return {
    id: null, name: null, email: null, role: null,
    memberSince: null, lastLogin: null, emailVerified: null,
    accountStatus: null, passwordLastChanged: null, twoFactorEnabled: null,
  };
}

export async function fetchProfileStats() {
  const docs = getDocuments();
  const conversations = getConversations();
  return {
    contractsUploaded: docs.length || null,
    conversations: conversations.length || null,
    lastContractUploaded: docs.length > 0 ? docs[0].name : null,
  };
}

export async function changePassword(currentPassword, newPassword) {
  const { error } = await supabase.auth.updateUser({ password: newPassword });
  if (error) throw error;
  return { success: true };
}

export async function deleteAccount() {
  return null;
}

export async function updateProfile(data) {
  const current = await fetchProfile();
  const merged = { ...current, ...data };
  saveStoredProfile(merged);
  return merged;
}
