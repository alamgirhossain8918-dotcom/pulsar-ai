/**
 * Supabase client configuration
 * In cloud deployment, this connects to Supabase auth & PostgreSQL tables
 */

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

export const supabaseConfig = {
  url: supabaseUrl,
  anonKey: supabaseAnonKey,
};
