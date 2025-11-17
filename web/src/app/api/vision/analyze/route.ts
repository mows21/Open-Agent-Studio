/**
 * Computer Vision Analysis API Route
 * Handles image/video analysis with security validation
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { z } from "zod";
import { storage } from "@/lib/supabase/client";
import { securityConfig } from "@/config/security.config";
import sharp from "sharp";

// Input validation
const visionRequestSchema = z.object({
  imageUrl: z.string().url().optional(),
  imageBase64: z.string().optional(),
  analysisType: z.enum([
    "ocr",
    "object_detection",
    "face_detection",
    "scene_classification",
    "semantic_segmentation",
  ]),
  options: z
    .object({
      language: z.string().optional(),
      minConfidence: z.number().min(0).max(1).optional(),
      maxResults: z.number().min(1).max(100).optional(),
    })
    .optional(),
});

export async function POST(request: NextRequest) {
  try {
    // 1. Authentication
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // 2. Parse request
    const contentType = request.headers.get("content-type");

    let body;
    let imageBuffer: Buffer | null = null;

    if (contentType?.includes("multipart/form-data")) {
      // Handle file upload
      const formData = await request.formData();
      const file = formData.get("image") as File;
      const analysisType = formData.get("analysisType") as string;

      if (!file) {
        return NextResponse.json(
          { error: "No image file provided" },
          { status: 400 }
        );
      }

      // Validate file type
      if (!securityConfig.upload.allowedImageFormats.includes(file.type)) {
        return NextResponse.json(
          { error: "Invalid file type", allowedTypes: securityConfig.upload.allowedImageFormats },
          { status: 400 }
        );
      }

      // Validate file size
      if (file.size > securityConfig.upload.maxImageSize) {
        return NextResponse.json(
          {
            error: "File too large",
            maxSize: securityConfig.upload.maxImageSize,
          },
          { status: 400 }
        );
      }

      imageBuffer = Buffer.from(await file.arrayBuffer());
      body = { analysisType };
    } else {
      // Handle JSON request
      body = await request.json();
    }

    // 3. Validate request
    const validationResult = visionRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return NextResponse.json(
        {
          error: "Validation failed",
          details: validationResult.error.issues,
        },
        { status: 400 }
      );
    }

    const { imageUrl, imageBase64, analysisType, options } =
      validationResult.data;

    // 4. Get image data
    if (!imageBuffer) {
      if (imageBase64) {
        imageBuffer = Buffer.from(imageBase64, "base64");
      } else if (imageUrl) {
        // Fetch image from URL
        const imageResponse = await fetch(imageUrl);
        imageBuffer = Buffer.from(await imageResponse.arrayBuffer());
      } else {
        return NextResponse.json(
          { error: "No image provided" },
          { status: 400 }
        );
      }
    }

    // 5. Validate and process image
    let processedImage: Buffer;
    let imageMetadata;

    try {
      const image = sharp(imageBuffer);
      imageMetadata = await image.metadata();

      // Resize if too large (max 4K resolution)
      const maxWidth = 3840;
      const maxHeight = 2160;

      if (
        imageMetadata.width! > maxWidth ||
        imageMetadata.height! > maxHeight
      ) {
        processedImage = await image
          .resize(maxWidth, maxHeight, { fit: "inside" })
          .toBuffer();
      } else {
        processedImage = imageBuffer;
      }
    } catch (error) {
      return NextResponse.json(
        { error: "Invalid image format" },
        { status: 400 }
      );
    }

    // 6. Call Python backend for vision analysis
    const startTime = Date.now();
    let analysisResult;

    try {
      const pythonBackendUrl = process.env.PYTHON_BACKEND_URL;
      const apiKey = process.env.PYTHON_BACKEND_API_KEY;

      if (!pythonBackendUrl) {
        throw new Error("Python backend not configured");
      }

      // Create FormData for image upload to Python backend
      const formData = new FormData();
      formData.append(
        "image",
        new Blob([processedImage]),
        "image.jpg"
      );
      formData.append("analysis_type", analysisType);
      if (options) {
        formData.append("options", JSON.stringify(options));
      }

      const visionResponse = await fetch(
        `${pythonBackendUrl}/api/vision/analyze`,
        {
          method: "POST",
          headers: {
            "X-API-Key": apiKey || "",
          },
          body: formData,
        }
      );

      if (!visionResponse.ok) {
        throw new Error(`Vision service error: ${visionResponse.statusText}`);
      }

      analysisResult = await visionResponse.json();
    } catch (visionError) {
      console.error("Vision analysis error:", visionError);

      // Fallback: Use Claude for image analysis
      const { Anthropic } = await import("@anthropic-ai/sdk");
      const anthropic = new Anthropic({
        apiKey: process.env.ANTHROPIC_API_KEY,
      });

      const base64Image = processedImage.toString("base64");

      const message = await anthropic.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1024,
        messages: [
          {
            role: "user",
            content: [
              {
                type: "image",
                source: {
                  type: "base64",
                  media_type: "image/jpeg",
                  data: base64Image,
                },
              },
              {
                type: "text",
                text: `Analyze this image for ${analysisType}. Provide detailed results.`,
              },
            ],
          },
        ],
      });

      analysisResult = {
        type: analysisType,
        results: message.content,
        confidence: 0.9,
        source: "claude",
      };
    }

    const processingTime = Date.now() - startTime;

    // 7. Store results in Supabase
    const { createServerClient } = await import("@/lib/supabase/client");
    const supabase = createServerClient();

    await supabase.from("ml_inferences").insert({
      user_id: userId,
      model_name: `vision:${analysisType}`,
      input_data: {
        imageMetadata: {
          width: imageMetadata.width,
          height: imageMetadata.height,
          format: imageMetadata.format,
        },
      },
      output_data: analysisResult,
      confidence_score: analysisResult.confidence,
      processing_time_ms: processingTime,
      status: "success",
    });

    // 8. Return response
    return NextResponse.json({
      success: true,
      analysisType,
      results: analysisResult,
      processingTimeMs: processingTime,
      imageMetadata: {
        width: imageMetadata.width,
        height: imageMetadata.height,
        format: imageMetadata.format,
      },
    });
  } catch (error) {
    console.error("Vision analysis error:", error);

    return NextResponse.json(
      {
        error: "Analysis failed",
        message:
          error instanceof Error ? error.message : "Unknown error occurred",
      },
      { status: 500 }
    );
  }
}

export const config = {
  api: {
    bodyParser: {
      sizeLimit: "10mb",
    },
  },
};
