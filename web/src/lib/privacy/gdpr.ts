/**
 * GDPR Compliance Utilities
 * Data privacy and compliance helpers
 */

import { createServerClient } from "@/lib/supabase/client";
import { exportUserData, deleteUserData } from "@/lib/clerk";
import { storage } from "@/lib/supabase/client";

export interface DataExportRequest {
  userId: string;
  includeProfiles?: boolean;
  includeAutomations?: boolean;
  includeMLInferences?: boolean;
  includeFiles?: boolean;
  includeAuditLogs?: boolean;
}

export interface DataDeletionRequest {
  userId: string;
  deleteProfiles?: boolean;
  deleteAutomations?: boolean;
  deleteMLInferences?: boolean;
  deleteFiles?: boolean;
  deleteAuditLogs?: boolean;
  keepAuditTrail?: boolean; // For compliance, retain anonymized audit logs
}

/**
 * Export all user data (GDPR Article 20 - Right to Data Portability)
 */
export async function exportAllUserData(
  request: DataExportRequest
): Promise<any> {
  const supabase = createServerClient();
  const exportData: any = {
    exportedAt: new Date().toISOString(),
    userId: request.userId,
    data: {},
  };

  try {
    // 1. User profile from Clerk
    if (request.includeProfiles !== false) {
      const clerkData = await exportUserData(request.userId);
      exportData.data.profile = clerkData;
    }

    // 2. Automation workflows
    if (request.includeAutomations !== false) {
      const { data: workflows } = await supabase
        .from("automation_workflows")
        .select("*")
        .eq("user_id", request.userId);

      const { data: executions } = await supabase
        .from("automation_executions")
        .select("*")
        .eq("user_id", request.userId);

      exportData.data.automations = {
        workflows: workflows || [],
        executions: executions || [],
      };
    }

    // 3. ML inferences
    if (request.includeMLInferences !== false) {
      const { data: inferences } = await supabase
        .from("ml_inferences")
        .select("*")
        .eq("user_id", request.userId);

      exportData.data.mlInferences = inferences || [];
    }

    // 4. Files from storage
    if (request.includeFiles !== false) {
      // Get list of user's files from storage buckets
      const buckets = ["ml-uploads", "user-files", "automation-outputs"];
      const files: any = {};

      for (const bucket of buckets) {
        const { data } = await supabase.storage
          .from(bucket)
          .list(`${request.userId}/`);

        if (data) {
          files[bucket] = data.map((file) => ({
            name: file.name,
            size: file.metadata?.size,
            createdAt: file.created_at,
            // Include download URL
            url: `${bucket}/${request.userId}/${file.name}`,
          }));
        }
      }

      exportData.data.files = files;
    }

    // 5. Audit logs
    if (request.includeAuditLogs !== false) {
      const { data: auditLogs } = await supabase
        .from("audit_logs")
        .select("*")
        .eq("user_id", request.userId);

      exportData.data.auditLogs = auditLogs || [];
    }

    // 6. API keys (metadata only, not the actual keys)
    const { data: apiKeys } = await supabase
      .from("api_keys")
      .select("id, name, key_preview, permissions, created_at, last_used_at")
      .eq("user_id", request.userId);

    exportData.data.apiKeys = apiKeys || [];

    return exportData;
  } catch (error) {
    console.error("Error exporting user data:", error);
    throw new Error("Failed to export user data");
  }
}

/**
 * Delete all user data (GDPR Article 17 - Right to Erasure / Right to be Forgotten)
 */
export async function deleteAllUserData(
  request: DataDeletionRequest
): Promise<{ success: boolean; deletedItems: string[] }> {
  const supabase = createServerClient();
  const deletedItems: string[] = [];

  try {
    // 1. Delete automation executions
    if (request.deleteAutomations !== false) {
      await supabase
        .from("automation_executions")
        .delete()
        .eq("user_id", request.userId);
      deletedItems.push("automation_executions");

      // Delete workflows
      await supabase
        .from("automation_workflows")
        .delete()
        .eq("user_id", request.userId);
      deletedItems.push("automation_workflows");
    }

    // 2. Delete ML inferences
    if (request.deleteMLInferences !== false) {
      await supabase
        .from("ml_inferences")
        .delete()
        .eq("user_id", request.userId);
      deletedItems.push("ml_inferences");
    }

    // 3. Delete files from storage
    if (request.deleteFiles !== false) {
      const buckets = ["ml-uploads", "user-files", "automation-outputs"];

      for (const bucket of buckets) {
        const { data: files } = await supabase.storage
          .from(bucket)
          .list(`${request.userId}/`);

        if (files && files.length > 0) {
          const filePaths = files.map(
            (file) => `${request.userId}/${file.name}`
          );
          await supabase.storage.from(bucket).remove(filePaths);
          deletedItems.push(`storage:${bucket}`);
        }
      }
    }

    // 4. Delete or anonymize audit logs
    if (request.deleteAuditLogs !== false) {
      if (request.keepAuditTrail) {
        // Anonymize instead of delete (for compliance)
        await supabase
          .from("audit_logs")
          .update({
            user_id: null,
            metadata: { anonymized: true, original_user_deleted: true },
          })
          .eq("user_id", request.userId);
        deletedItems.push("audit_logs (anonymized)");
      } else {
        await supabase
          .from("audit_logs")
          .delete()
          .eq("user_id", request.userId);
        deletedItems.push("audit_logs");
      }
    }

    // 5. Delete API keys
    await supabase.from("api_keys").delete().eq("user_id", request.userId);
    deletedItems.push("api_keys");

    // 6. Delete credentials
    await supabase.from("credentials").delete().eq("user_id", request.userId);
    deletedItems.push("credentials");

    // 7. Delete user profile from Supabase
    if (request.deleteProfiles !== false) {
      await supabase
        .from("profiles")
        .delete()
        .eq("clerk_user_id", request.userId);
      deletedItems.push("profile");
    }

    // 8. Delete user from Clerk (authentication)
    if (request.deleteProfiles !== false) {
      await deleteUserData(request.userId);
      deletedItems.push("clerk_account");
    }

    return {
      success: true,
      deletedItems,
    };
  } catch (error) {
    console.error("Error deleting user data:", error);
    throw new Error("Failed to delete user data");
  }
}

/**
 * Create anonymized copy of user data before deletion (for analytics/compliance)
 */
export async function anonymizeUserData(userId: string): Promise<void> {
  const supabase = createServerClient();

  try {
    // Anonymize ML inferences (keep for model improvement)
    await supabase
      .from("ml_inferences")
      .update({
        user_id: "ANONYMIZED",
        // Remove any PII from input/output data
      })
      .eq("user_id", userId);

    // Anonymize audit logs
    await supabase
      .from("audit_logs")
      .update({
        user_id: null,
        ip_address: null,
        user_agent: null,
        metadata: { anonymized: true },
      })
      .eq("user_id", userId);
  } catch (error) {
    console.error("Error anonymizing user data:", error);
    throw new Error("Failed to anonymize user data");
  }
}

/**
 * Check data retention compliance
 */
export async function checkDataRetention(): Promise<{
  itemsToDelete: number;
  oldestData: Date | null;
}> {
  const supabase = createServerClient();
  const retentionDays = parseInt(process.env.DATA_RETENTION_DAYS || "90");
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

  try {
    // Check old ML inferences
    const { count } = await supabase
      .from("ml_inferences")
      .select("*", { count: "exact", head: true })
      .lt("created_at", cutoffDate.toISOString());

    // Check old audit logs
    const logRetentionDays = parseInt(process.env.LOG_RETENTION_DAYS || "30");
    const logCutoffDate = new Date();
    logCutoffDate.setDate(logCutoffDate.getDate() - logRetentionDays);

    const { count: logCount } = await supabase
      .from("audit_logs")
      .select("*", { count: "exact", head: true })
      .lt("created_at", logCutoffDate.toISOString());

    return {
      itemsToDelete: (count || 0) + (logCount || 0),
      oldestData: cutoffDate,
    };
  } catch (error) {
    console.error("Error checking data retention:", error);
    return { itemsToDelete: 0, oldestData: null };
  }
}

/**
 * Audit logging helper (GDPR Article 30 - Records of Processing Activities)
 */
export async function logDataAccess(
  userId: string,
  action: string,
  resourceType: string,
  resourceId: string | null,
  request: Request
): Promise<void> {
  const supabase = createServerClient();

  try {
    await supabase.from("audit_logs").insert({
      user_id: userId,
      action,
      resource_type: resourceType,
      resource_id: resourceId,
      ip_address: request.headers.get("x-forwarded-for") || null,
      user_agent: request.headers.get("user-agent") || null,
      metadata: {
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    console.error("Error logging data access:", error);
    // Don't throw - logging should not break the main flow
  }
}

/**
 * Consent management helper
 */
export interface UserConsent {
  userId: string;
  dataProcessing: boolean;
  analytics: boolean;
  marketing: boolean;
  thirdPartySharing: boolean;
  consentedAt: Date;
  version: string;
}

export async function recordConsent(consent: UserConsent): Promise<void> {
  const supabase = createServerClient();

  try {
    await supabase.from("user_consents").upsert({
      user_id: consent.userId,
      data_processing: consent.dataProcessing,
      analytics: consent.analytics,
      marketing: consent.marketing,
      third_party_sharing: consent.thirdPartySharing,
      consented_at: consent.consentedAt.toISOString(),
      version: consent.version,
      updated_at: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Error recording consent:", error);
    throw new Error("Failed to record consent");
  }
}

export async function getUserConsent(
  userId: string
): Promise<UserConsent | null> {
  const supabase = createServerClient();

  try {
    const { data, error } = await supabase
      .from("user_consents")
      .select("*")
      .eq("user_id", userId)
      .single();

    if (error || !data) return null;

    return {
      userId: data.user_id,
      dataProcessing: data.data_processing,
      analytics: data.analytics,
      marketing: data.marketing,
      thirdPartySharing: data.third_party_sharing,
      consentedAt: new Date(data.consented_at),
      version: data.version,
    };
  } catch (error) {
    console.error("Error getting user consent:", error);
    return null;
  }
}
