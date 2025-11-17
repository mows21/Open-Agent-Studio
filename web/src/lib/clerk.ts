/**
 * Clerk Authentication Configuration
 * Secure authentication setup with best practices
 */

import { clerkClient } from "@clerk/nextjs/server";

export const clerkConfig = {
  // Appearance customization
  appearance: {
    variables: {
      colorPrimary: "#0F172A",
      colorBackground: "#ffffff",
      colorText: "#1e293b",
    },
    elements: {
      formButtonPrimary: "bg-slate-900 hover:bg-slate-800",
      card: "shadow-xl",
      headerTitle: "text-2xl font-bold",
      headerSubtitle: "text-slate-600",
    },
  },

  // Sign in/up configuration
  signIn: {
    elements: {
      formFieldInput: "rounded-md border-slate-300",
      footerActionLink: "text-blue-600 hover:text-blue-700",
    },
  },

  signUp: {
    elements: {
      formFieldInput: "rounded-md border-slate-300",
      footerActionLink: "text-blue-600 hover:text-blue-700",
    },
  },
} as const;

/**
 * Security: Enhanced user metadata with privacy controls
 */
export interface UserMetadata {
  // Privacy settings
  dataRetention: boolean;
  analyticsEnabled: boolean;
  marketingEmails: boolean;

  // Security settings
  twoFactorEnabled: boolean;
  lastPasswordChange?: string;
  sessionTimeout: number;

  // Compliance
  gdprConsent: boolean;
  termsAcceptedVersion: string;
  privacyPolicyAcceptedVersion: string;

  // Audit trail
  accountCreatedAt: string;
  lastLoginAt?: string;
  lastLoginIP?: string;
}

/**
 * Get user with enhanced security context
 */
export async function getUserWithSecurityContext(userId: string) {
  try {
    const client = await clerkClient();
    const user = await client.users.getUser(userId);

    return {
      id: user.id,
      email: user.emailAddresses[0]?.emailAddress,
      firstName: user.firstName,
      lastName: user.lastName,
      imageUrl: user.imageUrl,
      metadata: user.publicMetadata as UserMetadata,
      // Security context
      security: {
        twoFactorEnabled: user.twoFactorEnabled,
        hasPassword: user.passwordEnabled,
        lastSignInAt: user.lastSignInAt,
        createdAt: user.createdAt,
      },
    };
  } catch (error) {
    console.error("Error fetching user:", error);
    throw new Error("Failed to fetch user data");
  }
}

/**
 * Update user metadata with privacy controls
 */
export async function updateUserPrivacySettings(
  userId: string,
  settings: Partial<UserMetadata>
) {
  try {
    const client = await clerkClient();
    await client.users.updateUserMetadata(userId, {
      publicMetadata: settings,
    });

    return { success: true };
  } catch (error) {
    console.error("Error updating user metadata:", error);
    throw new Error("Failed to update privacy settings");
  }
}

/**
 * Security: Audit user login
 */
export async function auditUserLogin(userId: string, ipAddress?: string) {
  try {
    const client = await clerkClient();
    const currentMetadata = (await client.users.getUser(userId))
      .publicMetadata as UserMetadata;

    await client.users.updateUserMetadata(userId, {
      publicMetadata: {
        ...currentMetadata,
        lastLoginAt: new Date().toISOString(),
        lastLoginIP: ipAddress,
      },
    });
  } catch (error) {
    console.error("Error auditing login:", error);
    // Don't throw - this is non-critical
  }
}

/**
 * Check if user has required permissions
 */
export async function checkUserPermissions(
  userId: string,
  requiredPermissions: string[]
) {
  try {
    const client = await clerkClient();
    const user = await client.users.getUser(userId);

    // Get user's role from metadata
    const userRole = (user.publicMetadata as any)?.role || "user";

    // Define role permissions
    const rolePermissions: Record<string, string[]> = {
      admin: ["*"], // All permissions
      developer: [
        "ml:inference",
        "automation:execute",
        "api:read",
        "api:write",
      ],
      user: ["ml:inference", "automation:execute", "api:read"],
    };

    const userPermissions = rolePermissions[userRole] || [];

    // Check if user has all required permissions
    const hasPermissions =
      userPermissions.includes("*") ||
      requiredPermissions.every((perm) => userPermissions.includes(perm));

    return {
      hasPermissions,
      userRole,
      userPermissions,
    };
  } catch (error) {
    console.error("Error checking permissions:", error);
    return {
      hasPermissions: false,
      userRole: "user",
      userPermissions: [],
    };
  }
}

/**
 * Security: Delete all user data (GDPR right to be forgotten)
 */
export async function deleteUserData(userId: string) {
  try {
    const client = await clerkClient();

    // 1. Delete user from Clerk
    await client.users.deleteUser(userId);

    // 2. TODO: Delete user data from Supabase
    // 3. TODO: Delete user data from Convex
    // 4. TODO: Revoke all API keys
    // 5. TODO: Delete all user files/uploads

    return { success: true };
  } catch (error) {
    console.error("Error deleting user data:", error);
    throw new Error("Failed to delete user data");
  }
}

/**
 * Security: Export all user data (GDPR data portability)
 */
export async function exportUserData(userId: string) {
  try {
    const client = await clerkClient();
    const user = await client.users.getUser(userId);

    const userData = {
      profile: {
        id: user.id,
        email: user.emailAddresses[0]?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        createdAt: user.createdAt,
      },
      metadata: user.publicMetadata,
      // TODO: Add data from Supabase
      // TODO: Add data from Convex
      // TODO: Add automation history
      // TODO: Add ML inference history
    };

    return userData;
  } catch (error) {
    console.error("Error exporting user data:", error);
    throw new Error("Failed to export user data");
  }
}
