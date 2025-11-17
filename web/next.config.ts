import type { NextConfig } from "next";
import { securityConfig, generateCSPHeader } from "./src/config/security.config";

const nextConfig: NextConfig = {
  /* Security Headers */
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Content-Security-Policy",
            value: generateCSPHeader(),
          },
          ...Object.entries(securityConfig.headers).map(([key, value]) => ({
            key,
            value,
          })),
        ],
      },
    ];
  },

  /* Image Optimization */
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**.supabase.co",
      },
      {
        protocol: "https",
        hostname: "img.clerk.com",
      },
    ],
    formats: ["image/webp", "image/avif"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  /* Compiler Options */
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },

  /* Experimental Features */
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
      allowedOrigins: securityConfig.cors.allowedOrigins,
    },
  },

  /* Environment Variables Validation */
  env: {
    CUSTOM_ENV_VALIDATION: "enabled",
  },

  /* Disable telemetry */
  telemetry: false,
};

export default nextConfig;
