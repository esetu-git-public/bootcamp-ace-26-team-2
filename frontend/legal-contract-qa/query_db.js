import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://iqvspttbvqfueyqdseok.supabase.co';
const supabaseAnonKey = 'sb_publishable_qOKnfRRVmKxWlTX9M1PVBA_BxfBiB56';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function inspect() {
  console.log("Checking profiles table...");
  const { data, error } = await supabase.from('profiles').select('*').limit(5);
  if (error) {
    console.error("Error fetching profiles:", error);
  } else {
    console.log("Profiles data:", data);
  }

  const tables = ['users', 'profiles', 'user_profiles', 'personal_info', 'additional_info'];
  for (const table of tables) {
    const { data, error } = await supabase.from(table).select('*').limit(1);
    if (error) {
      console.log(`Table '${table}' query failed:`, error.message);
    } else {
      console.log(`Table '${table}' exists! Sample data:`, data);
    }
  }
}

inspect();
