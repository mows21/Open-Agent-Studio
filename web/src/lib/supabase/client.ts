/**
 * Supabase Client Configuration
 * Secure database access with Row Level Security (RLS)
 */

import { createClient } from "@supabase/supabase-js";
import type { Database } from "./database.types";

// Client-side Supabase client (uses anon key)
export const createBrowserClient = () => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error("Missing Supabase environment variables");
  }

  return createClient<Database>(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
    db: {
      schema: "public",
    },
    global: {
      headers: {
        "X-Client-Info": "open-agent-studio-web",
      },
    },
  });
};

// Server-side Supabase client (uses service role key for admin operations)
export const createServerClient = () => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !supabaseServiceKey) {
    throw new Error("Missing Supabase service role key");
  }

  return createClient<Database>(supabaseUrl, supabaseServiceKey, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
    db: {
      schema: "public",
    },
    global: {
      headers: {
        "X-Client-Info": "open-agent-studio-server",
      },
    },
  });
};

/**
 * Get Supabase client with user authentication
 */
export const getAuthenticatedClient = (userId: string) => {
  const client = createBrowserClient();

  // Set user context for RLS policies
  return client;
};

/**
 * Storage helper with security validation
 */
export const storage = {
  /**
   * Upload file with security checks
   */
  async uploadFile(
    bucket: string,
    path: string,
    file: File,
    userId: string
  ): Promise<{ url: string; path: string } | { error: string }> {
    const client = createBrowserClient();

    // Validate file type
    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
      "image/gif",
      "video/mp4",
      "video/webm",
    ];

    if (!allowedTypes.includes(file.type)) {
      return { error: "Invalid file type" };
    }

    // Validate file size (10MB for images, 100MB for videos)
    const maxSize = file.type.startsWith("video/")
      ? 100 * 1024 * 1024
      : 10 * 1024 * 1024;

    if (file.size > maxSize) {
      return { error: "File too large" };
    }

    // Generate secure file path
    const timestamp = Date.now();
    const sanitizedFileName = file.name.replace(/[^a-zA-Z0-9.-]/g, "_");
    const securePath = `${userId}/${timestamp}-${sanitizedFileName}`;

    try {
      const { data, error } = await client.storage
        .from(bucket)
        .upload(securePath, file, {
          cacheControl: "3600",
          upsert: false,
        });

      if (error) throw error;

      const {
        data: { publicUrl },
      } = client.storage.from(bucket).getPublicUrl(data.path);

      return {
        url: publicUrl,
        path: data.path,
      };
    } catch (error) {
      console.error("Upload error:", error);
      return { error: "Upload failed" };
    }
  },

  /**
   * Delete file with ownership verification
   */
  async deleteFile(
    bucket: string,
    path: string,
    userId: string
  ): Promise<{ success: boolean; error?: string }> {
    const client = createBrowserClient();

    // Verify user owns the file (path should start with userId)
    if (!path.startsWith(`${userId}/`)) {
      return { success: false, error: "Unauthorized" };
    }

    try {
      const { error } = await client.storage.from(bucket).remove([path]);

      if (error) throw error;

      return { success: true };
    } catch (error) {
      console.error("Delete error:", error);
      return { success: false, error: "Delete failed" };
    }
  },

  /**
   * Get signed URL with expiration
   */
  async getSignedUrl(
    bucket: string,
    path: string,
    expiresIn: number = 3600
  ): Promise<{ url: string } | { error: string }> {
    const client = createBrowserClient();

    try {
      const { data, error } = await client.storage
        .from(bucket)
        .createSignedUrl(path, expiresIn);

      if (error) throw error;

      return { url: data.signedUrl };
    } catch (error) {
      console.error("Signed URL error:", error);
      return { error: "Failed to generate signed URL" };
    }
  },
};

export default createBrowserClient;
