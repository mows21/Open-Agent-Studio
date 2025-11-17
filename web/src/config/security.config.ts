/**
 * Security Configuration for Open Agent Studio
 * Centralizes all security-related settings and constants
 */

export const securityConfig = {
  /**
   * Content Security Policy
   * Protects against XSS, clickjacking, and other code injection attacks
   */
  csp: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: [
        "'self'",
        "'unsafe-inline'", // Required for Next.js in dev mode
        "'unsafe-eval'", // Required for Next.js in dev mode
        "https://clerk.com",
        "https://*.clerk.accounts.dev",
        "https://*.convex.cloud",
      ],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: [
        "'self'",
        "data:",
        "blob:",
        "https://*.supabase.co",
        "https://img.clerk.com",
      ],
      connectSrc: [
        "'self'",
        "https://*.clerk.accounts.dev",
        "https://*.supabase.co",
        "https://*.convex.cloud",
        "wss://*.convex.cloud",
        "https://api.anthropic.com",
        process.env.PYTHON_BACKEND_URL || "http://localhost:8080",
      ],
      frameSrc: ["'self'", "https://clerk.com", "https://*.clerk.accounts.dev"],
      objectSrc: ["'none'"],
      baseUri: ["'self'"],
      formAction: ["'self'"],
      frameAncestors: ["'none'"],
      upgradeInsecureRequests: process.env.NODE_ENV === "production" ? [] : null,
    },
  },

  /**
   * CORS Configuration
   */
  cors: {
    allowedOrigins:
      process.env.ALLOWED_ORIGINS?.split(",") || ["http://localhost:3000"],
    allowedMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: [
      "Content-Type",
      "Authorization",
      "X-Requested-With",
      "X-API-Key",
    ],
    exposedHeaders: ["X-Total-Count", "X-Rate-Limit-Remaining"],
    credentials: true,
    maxAge: 86400, // 24 hours
  },

  /**
   * Rate Limiting Configuration
   */
  rateLimit: {
    // Standard API endpoints
    api: {
      windowMs: parseInt(process.env.RATE_LIMIT_API_WINDOW_MS || "900000"), // 15 minutes
      max: parseInt(process.env.RATE_LIMIT_API_REQUESTS || "100"),
      message: "Too many requests from this IP, please try again later.",
    },
    // ML/Computer Vision endpoints (more restrictive)
    ml: {
      windowMs: parseInt(process.env.RATE_LIMIT_ML_WINDOW_MS || "60000"), // 1 minute
      max: parseInt(process.env.RATE_LIMIT_ML_REQUESTS || "10"),
      message: "ML API rate limit exceeded. Please wait before trying again.",
    },
    // Authentication endpoints
    auth: {
      windowMs: 900000, // 15 minutes
      max: 5,
      message: "Too many authentication attempts. Please try again later.",
    },
  },

  /**
   * Session Configuration
   */
  session: {
    timeoutMinutes: parseInt(process.env.SESSION_TIMEOUT_MINUTES || "30"),
    maxFailedAttempts: parseInt(process.env.MAX_FAILED_LOGIN_ATTEMPTS || "5"),
    lockoutDurationMinutes: parseInt(
      process.env.LOCKOUT_DURATION_MINUTES || "15"
    ),
  },

  /**
   * File Upload Security
   */
  upload: {
    maxImageSize: parseInt(
      process.env.MAX_IMAGE_UPLOAD_SIZE || "10485760" // 10MB
    ),
    maxVideoSize: parseInt(
      process.env.MAX_VIDEO_UPLOAD_SIZE || "104857600" // 100MB
    ),
    allowedImageFormats:
      process.env.ALLOWED_IMAGE_FORMATS?.split(",") || [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
      ],
    allowedVideoFormats: [
      "video/mp4",
      "video/webm",
      "video/quicktime",
    ],
    // Dangerous file extensions to block
    blockedExtensions: [
      ".exe",
      ".dll",
      ".bat",
      ".cmd",
      ".sh",
      ".bash",
      ".ps1",
      ".vbs",
      ".scr",
      ".msi",
    ],
  },

  /**
   * Input Validation
   */
  validation: {
    // Minimum password requirements
    password: {
      minLength: 12,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
    },
    // API key format
    apiKey: {
      minLength: 32,
      pattern: /^[A-Za-z0-9_-]+$/,
    },
    // Username validation
    username: {
      minLength: 3,
      maxLength: 30,
      pattern: /^[a-zA-Z0-9_-]+$/,
    },
  },

  /**
   * Privacy & Data Protection
   */
  privacy: {
    dataRetentionDays: parseInt(process.env.DATA_RETENTION_DAYS || "90"),
    logRetentionDays: parseInt(process.env.LOG_RETENTION_DAYS || "30"),
    enableAnalytics: process.env.ENABLE_ANALYTICS === "true",
    enableErrorReporting: process.env.ENABLE_ERROR_REPORTING === "true",
    enableDataExport: process.env.ENABLE_DATA_EXPORT !== "false", // Default true
    enableDataDeletion: process.env.ENABLE_DATA_DELETION !== "false", // Default true
  },

  /**
   * Security Headers
   */
  headers: {
    "X-DNS-Prefetch-Control": "off",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-XSS-Protection": "1; mode=block",
    "Permissions-Policy":
      "camera=(), microphone=(), geolocation=(), interest-cohort=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  },

  /**
   * Encryption Configuration
   */
  encryption: {
    algorithm: "aes-256-gcm",
    keyLength: 32,
    ivLength: 16,
    saltLength: 64,
    tagLength: 16,
  },

  /**
   * WebSocket Security
   */
  websocket: {
    port: parseInt(process.env.WEBSOCKET_PORT || "3001"),
    secure: process.env.WEBSOCKET_SECURE === "true",
    maxConnections: parseInt(process.env.WEBSOCKET_MAX_CONNECTIONS || "100"),
    heartbeatInterval: 30000, // 30 seconds
    connectionTimeout: 60000, // 1 minute
  },

  /**
   * Audit Logging
   */
  audit: {
    enabled: process.env.NODE_ENV === "production",
    logSensitiveOperations: true,
    sensitiveOperations: [
      "user.login",
      "user.logout",
      "user.password.change",
      "user.delete",
      "api.key.create",
      "api.key.delete",
      "credential.access",
      "ml.inference",
      "automation.execute",
    ],
  },
} as const;

/**
 * Helper function to generate CSP header string
 */
export function generateCSPHeader(): string {
  const directives = securityConfig.csp.directives;
  return Object.entries(directives)
    .filter(([, value]) => value !== null)
    .map(([key, value]) => {
      const directiveName = key.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`);
      if (Array.isArray(value)) {
        return `${directiveName} ${value.join(" ")}`;
      }
      return directiveName;
    })
    .join("; ");
}

/**
 * Validate environment variables for security requirements
 */
export function validateSecurityConfig(): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // Check required environment variables
  const requiredVars = [
    "CLERK_SECRET_KEY",
    "JWT_SECRET",
    "ENCRYPTION_KEY",
  ];

  for (const varName of requiredVars) {
    if (!process.env[varName]) {
      errors.push(`Missing required environment variable: ${varName}`);
    } else if (process.env[varName]!.length < 32) {
      errors.push(`${varName} must be at least 32 characters long`);
    }
  }

  // Check production-specific requirements
  if (process.env.NODE_ENV === "production") {
    if (process.env.ALLOWED_ORIGINS?.includes("localhost")) {
      errors.push("Production environment should not allow localhost origins");
    }

    if (process.env.DEBUG === "true") {
      errors.push("Debug mode should be disabled in production");
    }

    if (!process.env.UPSTASH_REDIS_REST_URL) {
      errors.push("Rate limiting requires Upstash Redis in production");
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
