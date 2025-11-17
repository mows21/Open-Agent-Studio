/**
 * Convex Database Schema
 * Real-time ML inference and automation data
 */

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Real-time ML Inference Sessions
  mlInferences: defineTable({
    userId: v.string(),
    modelName: v.string(),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    ),
    inputData: v.any(),
    outputData: v.optional(v.any()),
    confidenceScore: v.optional(v.number()),
    processingTimeMs: v.optional(v.number()),
    errorMessage: v.optional(v.string()),
    createdAt: v.number(),
    completedAt: v.optional(v.number()),
  })
    .index("by_user", ["userId"])
    .index("by_status", ["status"])
    .index("by_created_at", ["createdAt"]),

  // Live Computer Vision Streams
  visionStreams: defineTable({
    userId: v.string(),
    sessionId: v.string(),
    streamType: v.union(
      v.literal("screen_capture"),
      v.literal("webcam"),
      v.literal("image_analysis")
    ),
    isActive: v.boolean(),
    frameCount: v.number(),
    fps: v.optional(v.number()),
    lastFrameAt: v.optional(v.number()),
    detections: v.optional(
      v.array(
        v.object({
          label: v.string(),
          confidence: v.number(),
          boundingBox: v.optional(
            v.object({
              x: v.number(),
              y: v.number(),
              width: v.number(),
              height: v.number(),
            })
          ),
        })
      )
    ),
    metadata: v.optional(v.any()),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_session", ["sessionId"])
    .index("by_active", ["isActive"]),

  // Automation Execution Logs (Real-time)
  automationExecutions: defineTable({
    userId: v.string(),
    workflowId: v.string(),
    workflowName: v.string(),
    status: v.union(
      v.literal("queued"),
      v.literal("running"),
      v.literal("completed"),
      v.literal("failed")
    ),
    currentStep: v.optional(v.string()),
    totalSteps: v.number(),
    completedSteps: v.number(),
    logs: v.array(
      v.object({
        timestamp: v.number(),
        level: v.union(
          v.literal("info"),
          v.literal("warning"),
          v.literal("error")
        ),
        message: v.string(),
      })
    ),
    result: v.optional(v.any()),
    errorMessage: v.optional(v.string()),
    startedAt: v.number(),
    completedAt: v.optional(v.number()),
  })
    .index("by_user", ["userId"])
    .index("by_workflow", ["workflowId"])
    .index("by_status", ["status"]),

  // User Presence (for collaborative features)
  userPresence: defineTable({
    userId: v.string(),
    userName: v.string(),
    avatarUrl: v.optional(v.string()),
    currentPage: v.string(),
    isOnline: v.boolean(),
    lastSeenAt: v.number(),
    metadata: v.optional(v.any()),
  })
    .index("by_user", ["userId"])
    .index("by_online", ["isOnline"]),

  // Real-time Notifications
  notifications: defineTable({
    userId: v.string(),
    type: v.string(),
    title: v.string(),
    message: v.string(),
    isRead: v.boolean(),
    priority: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high"),
      v.literal("urgent")
    ),
    actionUrl: v.optional(v.string()),
    metadata: v.optional(v.any()),
    createdAt: v.number(),
    readAt: v.optional(v.number()),
  })
    .index("by_user", ["userId"])
    .index("by_unread", ["userId", "isRead"])
    .index("by_priority", ["priority"]),

  // Shared ML Models Registry
  mlModels: defineTable({
    name: v.string(),
    version: v.string(),
    description: v.optional(v.string()),
    type: v.string(), // "vision", "nlp", "custom"
    isPublic: v.boolean(),
    ownerId: v.string(),
    endpoint: v.optional(v.string()),
    parameters: v.optional(v.any()),
    performance: v.optional(
      v.object({
        accuracy: v.optional(v.number()),
        latencyMs: v.optional(v.number()),
        throughput: v.optional(v.number()),
      })
    ),
    tags: v.array(v.string()),
    usageCount: v.number(),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_owner", ["ownerId"])
    .index("by_type", ["type"])
    .index("by_public", ["isPublic"]),
});
