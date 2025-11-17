/**
 * Supabase Database Type Definitions
 * Auto-generated types for type-safe database access
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      // User Profiles (synced with Clerk)
      profiles: {
        Row: {
          id: string;
          clerk_user_id: string;
          email: string;
          full_name: string | null;
          avatar_url: string | null;
          role: "admin" | "developer" | "user";
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          clerk_user_id: string;
          email: string;
          full_name?: string | null;
          avatar_url?: string | null;
          role?: "admin" | "developer" | "user";
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          clerk_user_id?: string;
          email?: string;
          full_name?: string | null;
          avatar_url?: string | null;
          role?: "admin" | "developer" | "user";
          created_at?: string;
          updated_at?: string;
        };
      };

      // ML Inference History
      ml_inferences: {
        Row: {
          id: string;
          user_id: string;
          model_name: string;
          input_data: Json;
          output_data: Json;
          confidence_score: number | null;
          processing_time_ms: number;
          status: "success" | "failed" | "pending";
          error_message: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          model_name: string;
          input_data: Json;
          output_data?: Json;
          confidence_score?: number | null;
          processing_time_ms?: number;
          status?: "success" | "failed" | "pending";
          error_message?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          model_name?: string;
          input_data?: Json;
          output_data?: Json;
          confidence_score?: number | null;
          processing_time_ms?: number;
          status?: "success" | "failed" | "pending";
          error_message?: string | null;
          created_at?: string;
        };
      };

      // Automation Workflows
      automation_workflows: {
        Row: {
          id: string;
          user_id: string;
          name: string;
          description: string | null;
          workflow_data: Json;
          is_active: boolean;
          last_run_at: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          name: string;
          description?: string | null;
          workflow_data: Json;
          is_active?: boolean;
          last_run_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          name?: string;
          description?: string | null;
          workflow_data?: Json;
          is_active?: boolean;
          last_run_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };

      // API Keys (encrypted)
      api_keys: {
        Row: {
          id: string;
          user_id: string;
          name: string;
          key_hash: string;
          key_preview: string;
          permissions: string[];
          expires_at: string | null;
          last_used_at: string | null;
          is_active: boolean;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          name: string;
          key_hash: string;
          key_preview: string;
          permissions?: string[];
          expires_at?: string | null;
          last_used_at?: string | null;
          is_active?: boolean;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          name?: string;
          key_hash?: string;
          key_preview?: string;
          permissions?: string[];
          expires_at?: string | null;
          last_used_at?: string | null;
          is_active?: boolean;
          created_at?: string;
        };
      };

      // Audit Logs
      audit_logs: {
        Row: {
          id: string;
          user_id: string | null;
          action: string;
          resource_type: string;
          resource_id: string | null;
          metadata: Json | null;
          ip_address: string | null;
          user_agent: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          action: string;
          resource_type: string;
          resource_id?: string | null;
          metadata?: Json | null;
          ip_address?: string | null;
          user_agent?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string | null;
          action?: string;
          resource_type?: string;
          resource_id?: string | null;
          metadata?: Json | null;
          ip_address?: string | null;
          user_agent?: string | null;
          created_at?: string;
        };
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      user_role: "admin" | "developer" | "user";
      inference_status: "success" | "failed" | "pending";
    };
  };
}
