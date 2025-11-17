/**
 * Automation Webhook Handler
 * Receives status updates from Python automation backend
 */

import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@/lib/supabase/client";
import crypto from "crypto";
import { z } from "zod";

// Webhook payload validation
const webhookPayloadSchema = z.object({
  executionId: z.string().uuid(),
  status: z.enum(["queued", "running", "completed", "failed", "paused"]),
  currentStep: z.string().optional(),
  completedSteps: z.number().optional(),
  totalSteps: z.number().optional(),
  logs: z
    .array(
      z.object({
        timestamp: z.number(),
        level: z.enum(["info", "warning", "error"]),
        message: z.string(),
      })
    )
    .optional(),
  result: z.any().optional(),
  errorMessage: z.string().optional(),
  timestamp: z.number(),
});

/**
 * Verify webhook signature
 */
function verifySignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const expectedSignature = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("hex");

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

/**
 * POST - Handle webhook from Python backend
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Get raw body for signature verification
    const rawBody = await request.text();

    // 2. Verify signature
    const signature = request.headers.get("X-Signature");
    const webhookSecret = process.env.PYTHON_BACKEND_WEBHOOK_SECRET;

    if (!signature || !webhookSecret) {
      console.error("Missing signature or webhook secret");
      return NextResponse.json(
        { error: "Unauthorized - Invalid signature" },
        { status: 401 }
      );
    }

    if (!verifySignature(rawBody, signature, webhookSecret)) {
      console.error("Invalid webhook signature");
      return NextResponse.json(
        { error: "Unauthorized - Signature verification failed" },
        { status: 401 }
      );
    }

    // 3. Parse and validate payload
    const body = JSON.parse(rawBody);
    const validationResult = webhookPayloadSchema.safeParse(body);

    if (!validationResult.success) {
      console.error("Webhook validation failed:", validationResult.error);
      return NextResponse.json(
        {
          error: "Validation failed",
          details: validationResult.error.issues,
        },
        { status: 400 }
      );
    }

    const {
      executionId,
      status,
      currentStep,
      completedSteps,
      totalSteps,
      logs,
      result,
      errorMessage,
    } = validationResult.data;

    // 4. Update execution in database
    const supabase = createServerClient();

    const updateData: any = {
      status,
      current_step: currentStep,
      completed_steps: completedSteps,
      total_steps: totalSteps,
      updated_at: new Date().toISOString(),
    };

    // Add logs if provided
    if (logs && logs.length > 0) {
      const { data: existingExecution } = await supabase
        .from("automation_executions")
        .select("logs")
        .eq("id", executionId)
        .single();

      const existingLogs = existingExecution?.logs || [];
      updateData.logs = [...existingLogs, ...logs];
    }

    // Add result if completed
    if (status === "completed" && result) {
      updateData.result = result;
      updateData.completed_at = new Date().toISOString();
    }

    // Add error if failed
    if (status === "failed" && errorMessage) {
      updateData.error_message = errorMessage;
      updateData.completed_at = new Date().toISOString();
    }

    const { error: updateError } = await supabase
      .from("automation_executions")
      .update(updateData)
      .eq("id", executionId);

    if (updateError) {
      console.error("Failed to update execution:", updateError);
      return NextResponse.json(
        { error: "Failed to update execution" },
        { status: 500 }
      );
    }

    // 5. Create notification for user (if significant event)
    if (status === "completed" || status === "failed") {
      const { data: execution } = await supabase
        .from("automation_executions")
        .select("user_id, workflow_name")
        .eq("id", executionId)
        .single();

      if (execution) {
        // TODO: Create notification in Convex or send via WebSocket
        console.log(
          `Automation ${status}: ${execution.workflow_name} for user ${execution.user_id}`
        );
      }
    }

    // 6. Return success
    return NextResponse.json({
      success: true,
      executionId,
      status,
      message: "Webhook processed successfully",
    });
  } catch (error) {
    console.error("Webhook processing error:", error);

    return NextResponse.json(
      {
        error: "Webhook processing failed",
        message:
          error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 }
    );
  }
}

/**
 * GET - Health check for webhook endpoint
 */
export async function GET() {
  return NextResponse.json({
    status: "healthy",
    endpoint: "automation-webhook",
    timestamp: Date.now(),
  });
}
