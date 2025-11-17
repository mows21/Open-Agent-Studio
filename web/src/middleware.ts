import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

// Initialize rate limiter (only if Upstash is configured)
let rateLimiter: Ratelimit | null = null;

if (
  process.env.UPSTASH_REDIS_REST_URL &&
  process.env.UPSTASH_REDIS_REST_TOKEN
) {
  const redis = new Redis({
    url: process.env.UPSTASH_REDIS_REST_URL,
    token: process.env.UPSTASH_REDIS_REST_TOKEN,
  });

  rateLimiter = new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(100, "15 m"), // 100 requests per 15 minutes
    analytics: true,
    prefix: "@upstash/ratelimit",
  });
}

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  "/",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/health",
  "/api/public(.*)",
]);

// Define API routes that need stricter rate limiting
const isAPIRoute = createRouteMatcher(["/api(.*)"]);
const isMLRoute = createRouteMatcher(["/api/ml(.*)", "/api/vision(.*)"]);

export default clerkMiddleware(async (auth, req: NextRequest) => {
  const { userId } = await auth();

  // Security: Add security headers
  const response = NextResponse.next();

  // CORS handling for API routes
  if (isAPIRoute(req)) {
    const origin = req.headers.get("origin");
    const allowedOrigins =
      process.env.ALLOWED_ORIGINS?.split(",") || ["http://localhost:3000"];

    if (origin && allowedOrigins.includes(origin)) {
      response.headers.set("Access-Control-Allow-Origin", origin);
      response.headers.set("Access-Control-Allow-Credentials", "true");
      response.headers.set(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, DELETE, OPTIONS"
      );
      response.headers.set(
        "Access-Control-Allow-Headers",
        "Content-Type, Authorization, X-Requested-With, X-API-Key"
      );
    }

    // Handle preflight requests
    if (req.method === "OPTIONS") {
      return new NextResponse(null, { status: 200, headers: response.headers });
    }
  }

  // Rate Limiting
  if (rateLimiter && isAPIRoute(req)) {
    const identifier = userId || req.ip || "anonymous";

    try {
      const { success, limit, remaining, reset } = await rateLimiter.limit(
        identifier
      );

      // Add rate limit headers
      response.headers.set("X-RateLimit-Limit", limit.toString());
      response.headers.set("X-RateLimit-Remaining", remaining.toString());
      response.headers.set("X-RateLimit-Reset", new Date(reset).toISOString());

      if (!success) {
        return new NextResponse(
          JSON.stringify({
            error: "Rate limit exceeded",
            message: "Too many requests. Please try again later.",
            retryAfter: new Date(reset).toISOString(),
          }),
          {
            status: 429,
            headers: {
              "Content-Type": "application/json",
              "Retry-After": Math.ceil((reset - Date.now()) / 1000).toString(),
              ...Object.fromEntries(response.headers),
            },
          }
        );
      }

      // Extra strict rate limiting for ML routes
      if (isMLRoute(req)) {
        const mlIdentifier = `ml:${identifier}`;
        const mlLimit = await rateLimiter.limit(mlIdentifier);

        if (!mlLimit.success) {
          return new NextResponse(
            JSON.stringify({
              error: "ML API rate limit exceeded",
              message:
                "You've exceeded the rate limit for ML operations. Please wait before trying again.",
              retryAfter: new Date(mlLimit.reset).toISOString(),
            }),
            {
              status: 429,
              headers: {
                "Content-Type": "application/json",
                "Retry-After": Math.ceil(
                  (mlLimit.reset - Date.now()) / 1000
                ).toString(),
              },
            }
          );
        }
      }
    } catch (error) {
      console.error("Rate limiting error:", error);
      // Continue without rate limiting if there's an error
    }
  }

  // Protect non-public routes
  if (!isPublicRoute(req)) {
    await auth.protect();
  }

  return response;
});

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
