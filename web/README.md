# Open Agent Studio - Web Interface

**Secure, ML-Powered Next.js Application with Real-time Automation**

A modern web interface for Open Agent Studio featuring:
- 🔐 **Enterprise-grade security** with Clerk authentication
- 🤖 **ML & Computer Vision** APIs with Claude AI integration
- 🚀 **Real-time data sync** via Convex
- 📊 **Secure data storage** with Supabase & Row Level Security
- 🔒 **GDPR compliance** with data export/deletion
- 🛡️ **Advanced rate limiting** and DDoS protection
- 🔑 **Credential vault** for secure API key management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js Frontend                        │
│  • TypeScript + React                                       │
│  • Tailwind CSS + Shadcn UI                                 │
│  • Clerk Authentication                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (Next.js)                     │
│  • ML Inference (/api/ml)                                   │
│  • Computer Vision (/api/vision)                            │
│  • Automation Bridge (/api/automation)                      │
│  • Privacy APIs (/api/privacy)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────┬──────────────────┬─────────────────────┐
│   Supabase       │     Convex       │  Python Backend     │
│  (Postgres)      │  (Real-time DB)  │  (Desktop Agent)    │
│  • User data     │  • Live streams  │  • Automation       │
│  • ML history    │  • Notifications │  • OCR/Vision       │
│  • Audit logs    │  • Presence      │  • Browser control  │
└──────────────────┴──────────────────┴─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+ (for backend integration)
- **Accounts**: Clerk, Supabase, Convex, Upstash (free tiers available)

### Installation

1. **Install dependencies**

```bash
npm install
```

2. **Set up environment variables**

```bash
cp .env.example .env.local
```

Edit `.env.local` and add your API keys (see [Configuration](#configuration) section).

3. **Initialize Convex** (optional, for real-time features)

```bash
npx convex dev
```

4. **Run development server**

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

---

## ⚙️ Configuration

### 1. Clerk Authentication

Create a Clerk account at [https://clerk.com](https://clerk.com)

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

### 2. Supabase Database

Create a Supabase project at [https://supabase.com](https://supabase.com)

1. Run SQL schema from `src/lib/supabase/schema.sql`
2. Create storage buckets:
   - `ml-uploads`
   - `user-files`
   - `automation-outputs`

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### 3. Convex Real-time Database

Create a Convex account at [https://convex.dev](https://convex.dev)

```bash
npx convex login
npx convex dev
```

```env
NEXT_PUBLIC_CONVEX_URL=https://xxx.convex.cloud
```

### 4. Upstash Redis (Rate Limiting)

Create an Upstash account at [https://upstash.com](https://upstash.com)

```env
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
```

### 5. Anthropic Claude AI

Get API key from [https://console.anthropic.com](https://console.anthropic.com)

```env
ANTHROPIC_API_KEY=sk-ant-...
```

### 6. Generate Security Secrets

```bash
# Generate secrets
node -e "console.log('JWT_SECRET=' + require('crypto').randomBytes(32).toString('base64'))"
node -e "console.log('ENCRYPTION_KEY=' + require('crypto').randomBytes(32).toString('base64'))"
node -e "console.log('PYTHON_BACKEND_WEBHOOK_SECRET=' + require('crypto').randomBytes(32).toString('base64'))"
```

Add to `.env.local`:

```env
JWT_SECRET=<generated-secret>
ENCRYPTION_KEY=<generated-secret>
PYTHON_BACKEND_WEBHOOK_SECRET=<generated-secret>
```

---

## 📁 Project Structure

```
web/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/               # API Routes
│   │   │   ├── ml/           # ML Inference APIs
│   │   │   ├── vision/       # Computer Vision APIs
│   │   │   ├── automation/   # Automation Bridge
│   │   │   └── privacy/      # GDPR APIs
│   │   ├── dashboard/         # Protected dashboard
│   │   └── page.tsx           # Home page
│   │
│   ├── lib/                   # Libraries & utilities
│   │   ├── clerk.ts          # Auth helpers
│   │   ├── supabase/         # Database client & schema
│   │   ├── convex/           # Real-time client
│   │   ├── security/         # Encryption & vault
│   │   └── privacy/          # GDPR utilities
│   │
│   ├── config/               # Configuration
│   │   └── security.config.ts # Security settings
│   │
│   └── middleware.ts         # Edge middleware (auth, rate limiting)
│
├── convex/                   # Convex backend
│   ├── schema.ts            # Database schema
│   └── mlInferences.ts      # ML functions
│
├── .env.example             # Environment template
├── SECURITY.md              # Security documentation
└── README.md                # This file
```

---

## 🔐 Security Features

### Authentication & Authorization

- **Clerk**: OAuth, SSO, 2FA
- **RBAC**: Admin, Developer, User roles
- **JWT**: Secure session management
- **API Keys**: Hashed with PBKDF2

### Data Protection

- **Encryption**: AES-256-GCM at rest
- **TLS 1.3**: All data in transit
- **RLS**: Supabase Row Level Security
- **CSP**: Strict Content Security Policy

### Rate Limiting

| Endpoint      | Limit                  |
|---------------|------------------------|
| API           | 100 req / 15 min       |
| ML Inference  | 10 req / 1 min         |
| Auth          | 5 req / 15 min         |

### Input Validation

All endpoints use **Zod schemas** for type-safe validation.

### Audit Logging

All sensitive operations logged:
- Authentication events
- Data access
- ML inferences
- Automation execution

See [SECURITY.md](./SECURITY.md) for complete security documentation.

---

## 🤖 API Endpoints

### ML Inference

**POST** `/api/ml/inference`

```typescript
// Request
{
  "modelName": "claude-sonnet-4",
  "inputData": { "text": "Analyze this..." },
  "options": {
    "maxTokens": 1024,
    "temperature": 0.7
  }
}

// Response
{
  "success": true,
  "inferenceId": "uuid",
  "result": { ... },
  "confidenceScore": 0.95,
  "processingTimeMs": 1234
}
```

### Computer Vision

**POST** `/api/vision/analyze`

```typescript
// Request (multipart/form-data)
FormData {
  image: File,
  analysisType: "ocr" | "object_detection" | "face_detection",
  options: { minConfidence: 0.8 }
}

// Response
{
  "success": true,
  "analysisType": "ocr",
  "results": { ... },
  "processingTimeMs": 2345
}
```

### Automation

**POST** `/api/automation/execute`

```typescript
// Request
{
  "workflowId": "uuid",
  "action": "start" | "stop" | "pause",
  "parameters": { ... }
}

// Response
{
  "success": true,
  "executionId": "uuid",
  "status": "running"
}
```

### Privacy (GDPR)

**POST** `/api/privacy/data-export`

Downloads all user data as JSON.

**POST** `/api/privacy/data-deletion`

```typescript
// Request
{
  "confirmEmail": "user@example.com",
  "confirmPhrase": "DELETE MY DATA",
  "keepAuditTrail": true
}
```

---

## 🛠️ Development

### Commands

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type check
npx tsc --noEmit

# Convex development
npx convex dev

# Deploy Convex
npx convex deploy
```

---

## 📚 Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Clerk Docs](https://clerk.com/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Convex Docs](https://docs.convex.dev/)
- [Security Guide](./SECURITY.md)

---

**Built with ❤️ using Next.js, TypeScript, and Claude AI**
