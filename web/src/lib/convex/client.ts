/**
 * Convex Client Configuration
 * Real-time database client setup
 */

"use client";

import { ConvexProvider, ConvexReactClient } from "convex/react";
import { ReactNode } from "react";

// Initialize Convex client
export const convexClient = new ConvexReactClient(
  process.env.NEXT_PUBLIC_CONVEX_URL || ""
);

/**
 * Convex Provider Component
 * Wrap your app with this to enable real-time features
 */
export function ConvexClientProvider({ children }: { children: ReactNode }) {
  return <ConvexProvider client={convexClient}>{children}</ConvexProvider>;
}

/**
 * Hook for authenticated Convex operations
 * Integrates with Clerk for user context
 */
export function useConvexAuth() {
  // This would integrate with Clerk to get the current user ID
  // and pass it to Convex mutations/queries
  return {
    userId: null, // Get from Clerk
    isAuthenticated: false, // Get from Clerk
  };
}
