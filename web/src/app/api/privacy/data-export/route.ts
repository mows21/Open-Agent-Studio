/**
 * GDPR Data Export API
 * Allows users to export all their data
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { exportAllUserData } from "@/lib/privacy/gdpr";

export async function POST(request: NextRequest) {
  try {
    // Authentication
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Get export options from request
    const body = await request.json();
    const {
      includeProfiles = true,
      includeAutomations = true,
      includeMLInferences = true,
      includeFiles = true,
      includeAuditLogs = true,
    } = body;

    // Export user data
    const exportData = await exportAllUserData({
      userId,
      includeProfiles,
      includeAutomations,
      includeMLInferences,
      includeFiles,
      includeAuditLogs,
    });

    // Return as downloadable JSON
    return new NextResponse(JSON.stringify(exportData, null, 2), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Content-Disposition": `attachment; filename="user-data-${userId}-${Date.now()}.json"`,
      },
    });
  } catch (error) {
    console.error("Data export error:", error);
    return NextResponse.json(
      {
        error: "Export failed",
        message:
          error instanceof Error ? error.message : "Failed to export data",
      },
      { status: 500 }
    );
  }
}
