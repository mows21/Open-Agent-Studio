/**
 * Convex ML Inference Functions
 * Real-time ML inference tracking and updates
 */

import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

/**
 * Create a new ML inference request
 */
export const create = mutation({
  args: {
    userId: v.string(),
    modelName: v.string(),
    inputData: v.any(),
  },
  handler: async (ctx, args) => {
    const inferenceId = await ctx.db.insert("mlInferences", {
      userId: args.userId,
      modelName: args.modelName,
      status: "pending",
      inputData: args.inputData,
      createdAt: Date.now(),
    });

    return inferenceId;
  },
});

/**
 * Update inference status with results
 */
export const update = mutation({
  args: {
    inferenceId: v.id("mlInferences"),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    ),
    outputData: v.optional(v.any()),
    confidenceScore: v.optional(v.number()),
    processingTimeMs: v.optional(v.number()),
    errorMessage: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { inferenceId, ...updateData } = args;

    await ctx.db.patch(inferenceId, {
      ...updateData,
      completedAt:
        args.status === "completed" || args.status === "failed"
          ? Date.now()
          : undefined,
    });

    return { success: true };
  },
});

/**
 * Get user's recent inferences (real-time)
 */
export const listByUser = query({
  args: {
    userId: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const inferences = await ctx.db
      .query("mlInferences")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(args.limit || 50);

    return inferences;
  },
});

/**
 * Get active (pending/processing) inferences
 */
export const listActive = query({
  args: {
    userId: v.string(),
  },
  handler: async (ctx, args) => {
    const pending = await ctx.db
      .query("mlInferences")
      .withIndex("by_status", (q) => q.eq("status", "pending"))
      .filter((q) => q.eq(q.field("userId"), args.userId))
      .collect();

    const processing = await ctx.db
      .query("mlInferences")
      .withIndex("by_status", (q) => q.eq("status", "processing"))
      .filter((q) => q.eq(q.field("userId"), args.userId))
      .collect();

    return [...pending, ...processing].sort(
      (a, b) => b.createdAt - a.createdAt
    );
  },
});

/**
 * Get inference statistics
 */
export const getStats = query({
  args: {
    userId: v.string(),
  },
  handler: async (ctx, args) => {
    const inferences = await ctx.db
      .query("mlInferences")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();

    const total = inferences.length;
    const completed = inferences.filter((i) => i.status === "completed").length;
    const failed = inferences.filter((i) => i.status === "failed").length;
    const avgProcessingTime =
      inferences
        .filter((i) => i.processingTimeMs)
        .reduce((sum, i) => sum + (i.processingTimeMs || 0), 0) /
      (completed || 1);

    return {
      total,
      completed,
      failed,
      pending: total - completed - failed,
      avgProcessingTime: Math.round(avgProcessingTime),
      successRate: total > 0 ? (completed / total) * 100 : 0,
    };
  },
});

/**
 * Delete old inferences (cleanup)
 */
export const cleanup = mutation({
  args: {
    userId: v.string(),
    olderThanDays: v.number(),
  },
  handler: async (ctx, args) => {
    const cutoffTime = Date.now() - args.olderThanDays * 24 * 60 * 60 * 1000;

    const oldInferences = await ctx.db
      .query("mlInferences")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .filter((q) => q.lt(q.field("createdAt"), cutoffTime))
      .collect();

    for (const inference of oldInferences) {
      await ctx.db.delete(inference._id);
    }

    return { deleted: oldInferences.length };
  },
});
