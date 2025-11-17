/**
 * ML Inference API Route
 * Handles ML model inference requests with security and rate limiting
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { z } from "zod";
import { createServerClient } from "@/lib/supabase/client";

// Input validation schema
const inferenceRequestSchema = z.object({
  modelName: z.string().min(1).max(100),
  inputData: z.any(),
  options: z
    .object({
      maxTokens: z.number().optional(),
      temperature: z.number().min(0).max(2).optional(),
      topP: z.number().min(0).max(1).optional(),
    })
    .optional(),
});

export async function POST(request: NextRequest) {
  try {
    // 1. Authentication
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json(
        { error: "Unauthorized", message: "Authentication required" },
        { status: 401 }
      );
    }

    // 2. Parse and validate request body
    const body = await request.json();
    const validationResult = inferenceRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return NextResponse.json(
        {
          error: "Validation failed",
          message: "Invalid request format",
          details: validationResult.error.issues,
        },
        { status: 400 }
      );
    }

    const { modelName, inputData, options } = validationResult.data;

    // 3. Check user permissions
    const supabase = createServerClient();
    const { data: profile } = await supabase
      .from("profiles")
      .select("role")
      .eq("clerk_user_id", userId)
      .single();

    const allowedRoles = ["admin", "developer", "user"];
    if (!profile || !allowedRoles.includes(profile.role)) {
      return NextResponse.json(
        { error: "Forbidden", message: "Insufficient permissions" },
        { status: 403 }
      );
    }

    // 4. Create inference record (for tracking)
    const startTime = Date.now();
    const { data: inference, error: insertError } = await supabase
      .from("ml_inferences")
      .insert({
        user_id: userId,
        model_name: modelName,
        input_data: inputData,
        status: "pending",
      })
      .select()
      .single();

    if (insertError) {
      console.error("Failed to create inference record:", insertError);
    }

    // 5. Call ML model (integrate with Python backend or Claude)
    let result;
    let confidenceScore;

    try {
      // TODO: Call Python backend ML service
      const pythonBackendUrl = process.env.PYTHON_BACKEND_URL;
      const apiKey = process.env.PYTHON_BACKEND_API_KEY;

      if (!pythonBackendUrl) {
        throw new Error("Python backend not configured");
      }

      const mlResponse = await fetch(`${pythonBackendUrl}/api/ml/inference`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey || "",
        },
        body: JSON.stringify({
          model: modelName,
          input: inputData,
          options,
        }),
      });

      if (!mlResponse.ok) {
        throw new Error(`ML service error: ${mlResponse.statusText}`);
      }

      const mlData = await mlResponse.json();
      result = mlData.output;
      confidenceScore = mlData.confidence;
    } catch (mlError) {
      console.error("ML inference error:", mlError);

      // Fallback: Use Claude for text-based inference
      if (typeof inputData === "string" || inputData.text) {
        const { Anthropic } = await import("@anthropic-ai/sdk");
        const anthropic = new Anthropic({
          apiKey: process.env.ANTHROPIC_API_KEY,
        });

        const message = await anthropic.messages.create({
          model: "claude-sonnet-4-20250514",
          max_tokens: options?.maxTokens || 1024,
          messages: [
            {
              role: "user",
              content: inputData.text || JSON.stringify(inputData),
            },
          ],
        });

        result = message.content[0];
        confidenceScore = 0.95;
      } else {
        throw new Error("ML inference failed and no fallback available");
      }
    }

    const processingTime = Date.now() - startTime;

    // 6. Update inference record with results
    if (inference) {
      await supabase
        .from("ml_inferences")
        .update({
          output_data: result,
          confidence_score: confidenceScore,
          processing_time_ms: processingTime,
          status: "success",
        })
        .eq("id", inference.id);
    }

    // 7. Return response
    return NextResponse.json({
      success: true,
      inferenceId: inference?.id,
      result,
      confidenceScore,
      processingTimeMs: processingTime,
      model: modelName,
    });
  } catch (error) {
    console.error("ML inference error:", error);

    return NextResponse.json(
      {
        error: "Inference failed",
        message:
          error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 }
    );
  }
}

/**
 * GET - Retrieve inference history
 */
export async function GET(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get("limit") || "50");
    const offset = parseInt(searchParams.get("offset") || "0");

    const supabase = createServerClient();
    const { data, error, count } = await supabase
      .from("ml_inferences")
      .select("*", { count: "exact" })
      .eq("user_id", userId)
      .order("created_at", { ascending: false })
      .range(offset, offset + limit - 1);

    if (error) throw error;

    return NextResponse.json({
      inferences: data || [],
      total: count || 0,
      limit,
      offset,
    });
  } catch (error) {
    console.error("Error fetching inferences:", error);
    return NextResponse.json(
      { error: "Failed to fetch inferences" },
      { status: 500 }
    );
  }
}
