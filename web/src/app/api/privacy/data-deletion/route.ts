/**
 * GDPR Data Deletion API
 * Allows users to request deletion of all their data
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { deleteAllUserData } from "@/lib/privacy/gdpr";
import { z } from "zod";

const deletionRequestSchema = z.object({
  confirmEmail: z.string().email(),
  confirmPhrase: z.literal("DELETE MY DATA"),
  keepAuditTrail: z.boolean().optional(),
});

export async function POST(request: NextRequest) {
  try {
    // Authentication
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Validate request
    const body = await request.json();
    const validationResult = deletionRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return NextResponse.json(
        {
          error: "Validation failed",
          message:
            "Please confirm your email and type 'DELETE MY DATA' to proceed",
          details: validationResult.error.issues,
        },
        { status: 400 }
      );
    }

    const { confirmEmail, keepAuditTrail } = validationResult.data;

    // Verify email matches user's email
    const { getUser } = await import("@clerk/nextjs/server");
    const user = await getUser(userId);

    if (
      !user?.emailAddresses.find((email) => email.emailAddress === confirmEmail)
    ) {
      return NextResponse.json(
        {
          error: "Email mismatch",
          message: "The provided email does not match your account",
        },
        { status: 400 }
      );
    }

    // Delete all user data
    const result = await deleteAllUserData({
      userId,
      deleteProfiles: true,
      deleteAutomations: true,
      deleteMLInferences: true,
      deleteFiles: true,
      deleteAuditLogs: true,
      keepAuditTrail: keepAuditTrail !== false, // Default to keeping anonymized audit trail
    });

    return NextResponse.json({
      success: true,
      message: "All your data has been deleted",
      deletedItems: result.deletedItems,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Data deletion error:", error);
    return NextResponse.json(
      {
        error: "Deletion failed",
        message:
          error instanceof Error ? error.message : "Failed to delete data",
      },
      { status: 500 }
    );
  }
}
