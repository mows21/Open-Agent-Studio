/**
 * Credential Vault
 * Secure storage and retrieval of API keys and credentials
 */

import { createServerClient } from "@/lib/supabase/client";
import { encrypt, decrypt, hash, generateAPIKey } from "./encryption";
import { nanoid } from "nanoid";

export interface Credential {
  id: string;
  userId: string;
  name: string;
  type: "api_key" | "oauth_token" | "password" | "certificate";
  value: string; // Decrypted value
  metadata?: Record<string, any>;
  expiresAt?: Date;
  createdAt: Date;
}

export interface StoredCredential {
  id: string;
  userId: string;
  name: string;
  type: string;
  encryptedValue: string;
  iv: string;
  tag: string;
  keyPreview: string; // Last 4 characters for identification
  metadata?: any;
  expiresAt?: string;
  createdAt: string;
  lastUsedAt?: string;
}

/**
 * Credential Vault Manager
 */
export class CredentialVault {
  private userId: string;

  constructor(userId: string) {
    this.userId = userId;
  }

  /**
   * Store a new credential
   */
  async storeCredential(
    name: string,
    type: Credential["type"],
    value: string,
    metadata?: Record<string, any>,
    expiresAt?: Date
  ): Promise<{ id: string; success: boolean }> {
    try {
      const supabase = createServerClient();

      // Encrypt the credential value
      const { encrypted, iv, tag } = encrypt(value);

      // Get last 4 characters for preview
      const keyPreview = value.slice(-4);

      // Store in database
      const { data, error } = await supabase
        .from("credentials")
        .insert({
          id: nanoid(),
          user_id: this.userId,
          name,
          type,
          encrypted_value: encrypted,
          iv,
          tag,
          key_preview: keyPreview,
          metadata: metadata || {},
          expires_at: expiresAt?.toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      return { id: data.id, success: true };
    } catch (error) {
      console.error("Error storing credential:", error);
      throw new Error("Failed to store credential");
    }
  }

  /**
   * Retrieve and decrypt a credential
   */
  async getCredential(credentialId: string): Promise<Credential | null> {
    try {
      const supabase = createServerClient();

      const { data, error } = await supabase
        .from("credentials")
        .select("*")
        .eq("id", credentialId)
        .eq("user_id", this.userId)
        .single();

      if (error || !data) {
        return null;
      }

      // Check if expired
      if (data.expires_at && new Date(data.expires_at) < new Date()) {
        throw new Error("Credential has expired");
      }

      // Decrypt the value
      const decryptedValue = decrypt(
        data.encrypted_value,
        data.iv,
        data.tag
      );

      // Update last used timestamp
      await supabase
        .from("credentials")
        .update({ last_used_at: new Date().toISOString() })
        .eq("id", credentialId);

      return {
        id: data.id,
        userId: data.user_id,
        name: data.name,
        type: data.type as Credential["type"],
        value: decryptedValue,
        metadata: data.metadata,
        expiresAt: data.expires_at ? new Date(data.expires_at) : undefined,
        createdAt: new Date(data.created_at),
      };
    } catch (error) {
      console.error("Error retrieving credential:", error);
      throw new Error("Failed to retrieve credential");
    }
  }

  /**
   * List all credentials (without decrypted values)
   */
  async listCredentials(): Promise<
    Omit<StoredCredential, "encryptedValue" | "iv" | "tag">[]
  > {
    try {
      const supabase = createServerClient();

      const { data, error } = await supabase
        .from("credentials")
        .select("id, user_id, name, type, key_preview, metadata, expires_at, created_at, last_used_at")
        .eq("user_id", this.userId)
        .order("created_at", { ascending: false });

      if (error) throw error;

      return data || [];
    } catch (error) {
      console.error("Error listing credentials:", error);
      return [];
    }
  }

  /**
   * Update credential metadata (not the value)
   */
  async updateMetadata(
    credentialId: string,
    metadata: Record<string, any>
  ): Promise<boolean> {
    try {
      const supabase = createServerClient();

      const { error } = await supabase
        .from("credentials")
        .update({ metadata })
        .eq("id", credentialId)
        .eq("user_id", this.userId);

      if (error) throw error;

      return true;
    } catch (error) {
      console.error("Error updating credential metadata:", error);
      return false;
    }
  }

  /**
   * Rotate a credential (update value)
   */
  async rotateCredential(
    credentialId: string,
    newValue: string
  ): Promise<boolean> {
    try {
      const supabase = createServerClient();

      // Encrypt new value
      const { encrypted, iv, tag } = encrypt(newValue);
      const keyPreview = newValue.slice(-4);

      const { error } = await supabase
        .from("credentials")
        .update({
          encrypted_value: encrypted,
          iv,
          tag,
          key_preview: keyPreview,
          updated_at: new Date().toISOString(),
        })
        .eq("id", credentialId)
        .eq("user_id", this.userId);

      if (error) throw error;

      return true;
    } catch (error) {
      console.error("Error rotating credential:", error);
      return false;
    }
  }

  /**
   * Delete a credential
   */
  async deleteCredential(credentialId: string): Promise<boolean> {
    try {
      const supabase = createServerClient();

      const { error } = await supabase
        .from("credentials")
        .delete()
        .eq("id", credentialId)
        .eq("user_id", this.userId);

      if (error) throw error;

      return true;
    } catch (error) {
      console.error("Error deleting credential:", error);
      return false;
    }
  }

  /**
   * Generate and store a new API key
   */
  async generateAPIKey(
    name: string,
    permissions: string[] = ["api:read"],
    expiresAt?: Date
  ): Promise<{ apiKey: string; id: string }> {
    try {
      const supabase = createServerClient();

      // Generate API key
      const apiKey = generateAPIKey("oas");

      // Hash the key for storage
      const keyHash = await hash(apiKey);
      const keyPreview = apiKey.slice(-4);

      // Store in database
      const { data, error } = await supabase
        .from("api_keys")
        .insert({
          user_id: this.userId,
          name,
          key_hash: keyHash,
          key_preview: keyPreview,
          permissions,
          expires_at: expiresAt?.toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      // Return the plain API key (only shown once!)
      return {
        apiKey,
        id: data.id,
      };
    } catch (error) {
      console.error("Error generating API key:", error);
      throw new Error("Failed to generate API key");
    }
  }

  /**
   * Validate API key
   */
  static async validateAPIKey(
    apiKey: string
  ): Promise<{ valid: boolean; userId?: string; permissions?: string[] }> {
    try {
      const supabase = createServerClient();

      // Get all API keys and check hash
      const { data: apiKeys, error } = await supabase
        .from("api_keys")
        .select("*")
        .eq("is_active", true);

      if (error) throw error;

      // Find matching key by hash comparison
      for (const storedKey of apiKeys || []) {
        const { verifyHash } = await import("./encryption");
        const isValid = await verifyHash(apiKey, storedKey.key_hash);

        if (isValid) {
          // Check expiration
          if (
            storedKey.expires_at &&
            new Date(storedKey.expires_at) < new Date()
          ) {
            return { valid: false };
          }

          // Update last used
          await supabase
            .from("api_keys")
            .update({ last_used_at: new Date().toISOString() })
            .eq("id", storedKey.id);

          return {
            valid: true,
            userId: storedKey.user_id,
            permissions: storedKey.permissions,
          };
        }
      }

      return { valid: false };
    } catch (error) {
      console.error("Error validating API key:", error);
      return { valid: false };
    }
  }
}

/**
 * Helper function to get credential vault for a user
 */
export function getCredentialVault(userId: string): CredentialVault {
  return new CredentialVault(userId);
}
