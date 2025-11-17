/**
 * Automation Execution API Route
 * Bridge between Next.js frontend and Python automation backend
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { z } from "zod";
import { createServerClient } from "@/lib/supabase/client";
import crypto from "crypto";

// Input validation
const automationRequestSchema = z.object({
  workflowId: z.string().uuid(),
  action: z.enum(["start", "stop", "pause", "resume"]),
  parameters: z.record(z.any()).optional(),
});

/**
 * Generate HMAC signature for webhook verification
 */
function generateSignature(payload: string, secret: string): string {
  return crypto.createHmac("sha256", secret).update(payload).digest("hex");
}

/**
 * POST - Execute automation workflow
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Authentication
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // 2. Validate request
    const body = await request.json();
    const validationResult = automationRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return NextResponse.json(
        {
          error: "Validation failed",
          details: validationResult.error.issues,
        },
        { status: 400 }
      );
    }

    const { workflowId, action, parameters } = validationResult.data;

    // 3. Verify user owns the workflow
    const supabase = createServerClient();
    const { data: workflow, error: workflowError } = await supabase
      .from("automation_workflows")
      .select("*")
      .eq("id", workflowId)
      .eq("user_id", userId)
      .single();

    if (workflowError || !workflow) {
      return NextResponse.json(
        { error: "Workflow not found or access denied" },
        { status: 404 }
      );
    }

    // 4. Prepare request to Python backend
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL;
    const apiKey = process.env.PYTHON_BACKEND_API_KEY;
    const webhookSecret = process.env.PYTHON_BACKEND_WEBHOOK_SECRET;

    if (!pythonBackendUrl || !apiKey) {
      return NextResponse.json(
        { error: "Automation backend not configured" },
        { status: 503 }
      );
    }

    // 5. Create execution record
    const { data: execution, error: executionError } = await supabase
      .from("automation_executions")
      .insert({
        user_id: userId,
        workflow_id: workflowId,
        workflow_name: workflow.name,
        status: "queued",
        current_step: null,
        total_steps: 0,
        completed_steps: 0,
        logs: [],
        started_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (executionError) {
      console.error("Failed to create execution record:", executionError);
    }

    // 6. Prepare payload for Python backend
    const payload = {
      executionId: execution?.id,
      workflowId,
      userId,
      action,
      workflow: workflow.workflow_data,
      parameters: parameters || {},
      timestamp: Date.now(),
    };

    const payloadString = JSON.stringify(payload);

    // 7. Generate signature for security
    const signature = webhookSecret
      ? generateSignature(payloadString, webhookSecret)
      : "";

    // 8. Call Python backend
    try {
      const backendResponse = await fetch(
        `${pythonBackendUrl}/api/automation/execute`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
            "X-Signature": signature,
            "X-User-Id": userId,
          },
          body: payloadString,
        }
      );

      if (!backendResponse.ok) {
        const errorData = await backendResponse.json().catch(() => ({}));
        throw new Error(
          errorData.message || `Backend error: ${backendResponse.statusText}`
        );
      }

      const result = await backendResponse.json();

      // 9. Update execution record
      if (execution) {
        await supabase
          .from("automation_executions")
          .update({
            status: "running",
            current_step: result.currentStep,
            total_steps: result.totalSteps,
          })
          .eq("id", execution.id);
      }

      // 10. Update workflow last_run_at
      await supabase
        .from("automation_workflows")
        .update({
          last_run_at: new Date().toISOString(),
        })
        .eq("id", workflowId);

      return NextResponse.json({
        success: true,
        executionId: execution?.id,
        workflowId,
        status: "running",
        message: "Automation started successfully",
        result,
      });
    } catch (backendError) {
      console.error("Backend communication error:", backendError);

      // Update execution status to failed
      if (execution) {
        await supabase
          .from("automation_executions")
          .update({
            status: "failed",
            error_message:
              backendError instanceof Error
                ? backendError.message
                : "Unknown error",
            completed_at: new Date().toISOString(),
          })
          .eq("id", execution.id);
      }

      return NextResponse.json(
        {
          error: "Backend execution failed",
          message:
            backendError instanceof Error
              ? backendError.message
              : "Failed to communicate with automation backend",
        },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error("Automation execution error:", error);

    return NextResponse.json(
      {
        error: "Execution failed",
        message:
          error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 }
    );
  }
}

/**
 * GET - Get automation execution status
 */
export async function GET(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const executionId = searchParams.get("executionId");
    const workflowId = searchParams.get("workflowId");

    const supabase = createServerClient();

    if (executionId) {
      // Get specific execution
      const { data, error } = await supabase
        .from("automation_executions")
        .select("*")
        .eq("id", executionId)
        .eq("user_id", userId)
        .single();

      if (error || !data) {
        return NextResponse.json(
          { error: "Execution not found" },
          { status: 404 }
        );
      }

      return NextResponse.json(data);
    } else if (workflowId) {
      // Get all executions for a workflow
      const { data, error } = await supabase
        .from("automation_executions")
        .select("*")
        .eq("workflow_id", workflowId)
        .eq("user_id", userId)
        .order("started_at", { ascending: false })
        .limit(50);

      if (error) throw error;

      return NextResponse.json({ executions: data || [] });
    } else {
      // Get all user's executions
      const { data, error } = await supabase
        .from("automation_executions")
        .select("*")
        .eq("user_id", userId)
        .order("started_at", { ascending: false })
        .limit(100);

      if (error) throw error;

      return NextResponse.json({ executions: data || [] });
    }
  } catch (error) {
    console.error("Error fetching execution status:", error);
    return NextResponse.json(
      { error: "Failed to fetch execution status" },
      { status: 500 }
    );
  }
}
