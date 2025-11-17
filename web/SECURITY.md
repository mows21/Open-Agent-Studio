# Security & Privacy Guide - Open Agent Studio

## 🔒 Security Architecture Overview

Open Agent Studio implements a **defense-in-depth** security architecture with multiple layers of protection:

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                            │
│  • Clerk Authentication (OAuth, 2FA, SSO)                   │
│  • Role-Based Access Control (RBAC)                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  • Next.js Middleware (CSP, CORS, Rate Limiting)            │
│  • Input Validation (Zod schemas)                           │
│  • API Route Protection                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  • Supabase Row Level Security (RLS)                        │
│  • AES-256-GCM Encryption at Rest                           │
│  • Secure Credential Vault                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  • HTTPS/TLS 1.3                                            │
│  • Security Headers (HSTS, CSP, etc.)                       │
│  • Upstash Redis for Rate Limiting                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Initial Setup

### 1. Environment Variables

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

### 2. Generate Secure Secrets

**CRITICAL:** Never use example/default values in production.

```bash
# Generate JWT secret (32+ bytes)
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Generate encryption key (32+ bytes)
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Generate webhook secret (32+ bytes)
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

Update `.env.local` with these values:

```env
JWT_SECRET=<generated-jwt-secret>
ENCRYPTION_KEY=<generated-encryption-key>
PYTHON_BACKEND_WEBHOOK_SECRET=<generated-webhook-secret>
```

### 3. Configure Authentication (Clerk)

1. Create account at [https://clerk.com](https://clerk.com)
2. Create new application
3. Get API keys from dashboard
4. Add to `.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

### 4. Configure Database (Supabase)

1. Create project at [https://supabase.com](https://supabase.com)
2. Run the schema from `src/lib/supabase/schema.sql` in SQL editor
3. Create storage buckets:
   - `ml-uploads` (10MB max, auto-delete after 7 days)
   - `user-files` (10MB max)
   - `automation-outputs` (auto-delete after 30 days)
4. Add credentials to `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

### 5. Configure Real-time Database (Convex)

1. Install Convex CLI: `npm install -g convex`
2. Login: `npx convex login`
3. Setup project: `npx convex dev`
4. Add deployment URL to `.env.local`:

```env
NEXT_PUBLIC_CONVEX_URL=https://xxx.convex.cloud
```

### 6. Configure Rate Limiting (Upstash Redis)

1. Create account at [https://upstash.com](https://upstash.com)
2. Create Redis database
3. Add credentials to `.env.local`:

```env
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
```

---

## 🔐 Security Features

### Authentication & Authorization

#### Multi-Factor Authentication (2FA)
- **Enabled by default** for all admin accounts
- Supports TOTP (Google Authenticator, Authy)
- SMS backup codes available

#### Role-Based Access Control (RBAC)

| Role      | Permissions                                    |
|-----------|------------------------------------------------|
| `admin`   | Full access to all resources                   |
| `developer` | ML inference, automation, API read/write     |
| `user`    | ML inference, automation, API read             |

To set user role:
```typescript
import { updateUserPrivacySettings } from '@/lib/clerk';

await updateUserPrivacySettings(userId, { role: 'developer' });
```

### Content Security Policy (CSP)

Strict CSP headers prevent XSS attacks:

```typescript
// Configured in next.config.ts
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://clerk.com https://*.convex.cloud;
  img-src 'self' data: blob: https://*.supabase.co;
  connect-src 'self' https://api.anthropic.com wss://*.convex.cloud;
```

### Rate Limiting

Protects against abuse and DDoS:

| Endpoint Type | Rate Limit                  |
|---------------|----------------------------|
| Standard API  | 100 requests / 15 minutes  |
| ML Inference  | 10 requests / 1 minute     |
| Authentication| 5 requests / 15 minutes    |

Rate limits are **per user** and enforced via Upstash Redis.

### Input Validation

All API endpoints use **Zod schemas** for strict type validation:

```typescript
const inferenceRequestSchema = z.object({
  modelName: z.string().min(1).max(100),
  inputData: z.any(),
  options: z.object({
    maxTokens: z.number().optional(),
    temperature: z.number().min(0).max(2).optional(),
  }).optional(),
});
```

### File Upload Security

- **File type validation** (whitelist approach)
- **Size limits** (10MB images, 100MB videos)
- **Malware scanning** (recommended: integrate ClamAV)
- **Secure storage** with user-scoped paths

```typescript
// Upload path format: {userId}/{timestamp}-{sanitized-filename}
// Example: abc123/1699876543-report.pdf
```

### Encryption

#### Data at Rest
- **AES-256-GCM** encryption for sensitive data
- Separate encryption keys per environment
- Key rotation support (every 90 days recommended)

```typescript
import { encrypt, decrypt } from '@/lib/security/encryption';

// Encrypt sensitive data
const { encrypted, iv, tag } = encrypt('sensitive-value');

// Decrypt when needed
const decrypted = decrypt(encrypted, iv, tag);
```

#### Data in Transit
- **TLS 1.3** minimum
- **HSTS** enabled (strict-transport-security)
- Certificate pinning for API calls

### Credential Management

Secure vault pattern for API keys and secrets:

```typescript
import { CredentialVault } from '@/lib/security/credential-vault';

const vault = new CredentialVault(userId);

// Store credential
await vault.storeCredential(
  'Anthropic API Key',
  'api_key',
  'sk-ant-...',
  { service: 'anthropic' },
  new Date('2025-12-31') // expiration
);

// Retrieve credential
const credential = await vault.getCredential(credentialId);
console.log(credential.value); // Decrypted value

// Generate API key
const { apiKey, id } = await vault.generateAPIKey(
  'My API Key',
  ['api:read', 'ml:inference']
);
```

---

## 🔍 Audit & Compliance

### Audit Logging

All sensitive operations are logged:

```typescript
import { logDataAccess } from '@/lib/privacy/gdpr';

await logDataAccess(
  userId,
  'credential.access',
  'api_key',
  credentialId,
  request
);
```

Logged operations:
- User login/logout
- Password changes
- API key creation/deletion
- Credential access
- ML inference requests
- Automation execution
- Data export/deletion

### GDPR Compliance

#### Right to Access (Article 15)
Users can access all their data via `/api/privacy/data-export`

#### Right to Portability (Article 20)
Export data in JSON format with all associated records

```bash
curl -X POST https://your-domain.com/api/privacy/data-export \
  -H "Authorization: Bearer $TOKEN" \
  -o user-data.json
```

#### Right to Erasure (Article 17)
Delete all user data via `/api/privacy/data-deletion`

```typescript
// User confirmation required
const response = await fetch('/api/privacy/data-deletion', {
  method: 'POST',
  body: JSON.stringify({
    confirmEmail: 'user@example.com',
    confirmPhrase: 'DELETE MY DATA',
    keepAuditTrail: true // Keep anonymized logs for compliance
  })
});
```

### Data Retention

Automatic cleanup of old data:

```sql
-- Run daily via Supabase cron jobs
SELECT cleanup_old_audit_logs();    -- Deletes logs > 30 days
SELECT cleanup_old_ml_inferences(); -- Deletes inferences > 90 days
```

Configure in `.env.local`:
```env
DATA_RETENTION_DAYS=90
LOG_RETENTION_DAYS=30
```

---

## 🛡️ Best Practices

### Development

1. **Never commit secrets** to version control
   - Use `.env.local` (gitignored)
   - Rotate secrets immediately if exposed

2. **Use environment-specific configs**
   - Development: `dev` branch, test keys
   - Production: separate database, real keys

3. **Enable debug mode only in development**
   ```env
   DEBUG=false  # Always false in production
   VERBOSE_LOGGING=false
   ```

### Production Deployment

1. **Enable all security headers**
   - Configured automatically in `next.config.ts`
   - Verify with [securityheaders.com](https://securityheaders.com)

2. **Set up monitoring**
   - Sentry for error tracking
   - Uptime monitoring (e.g., UptimeRobot)
   - Log aggregation (e.g., DataDog, LogRocket)

3. **Configure CORS properly**
   ```env
   ALLOWED_ORIGINS=https://your-domain.com,https://app.your-domain.com
   ```

4. **Use secure session settings**
   ```env
   SESSION_TIMEOUT_MINUTES=30
   MAX_FAILED_LOGIN_ATTEMPTS=5
   LOCKOUT_DURATION_MINUTES=15
   ```

5. **Enable rate limiting**
   - Requires Upstash Redis (free tier available)
   - Prevents abuse and DDoS attacks

### API Security

1. **Always validate user input**
   ```typescript
   const result = schema.safeParse(input);
   if (!result.success) {
     return NextResponse.json({ error: result.error }, { status: 400 });
   }
   ```

2. **Check user permissions**
   ```typescript
   const { hasPermissions } = await checkUserPermissions(userId, ['ml:inference']);
   if (!hasPermissions) {
     return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
   }
   ```

3. **Use HMAC signatures for webhooks**
   ```typescript
   const signature = generateSignature(payload, secret);
   request.headers.set('X-Signature', signature);
   ```

4. **Implement request signing for Python backend**
   ```python
   import hmac
   import hashlib

   def verify_signature(payload, signature, secret):
       expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
       return hmac.compare_digest(signature, expected)
   ```

---

## 🚨 Incident Response

### Suspected Security Breach

1. **Immediate Actions**
   - Rotate all API keys and secrets
   - Force logout all users: `await clerkClient.users.lockUserAccount(userId)`
   - Review audit logs for suspicious activity

2. **Investigation**
   ```sql
   -- Check recent logins
   SELECT * FROM audit_logs
   WHERE action = 'user.login'
   AND created_at > NOW() - INTERVAL '24 hours'
   ORDER BY created_at DESC;

   -- Check failed login attempts
   SELECT user_id, COUNT(*) as attempts
   FROM audit_logs
   WHERE action = 'user.login.failed'
   AND created_at > NOW() - INTERVAL '1 hour'
   GROUP BY user_id
   HAVING COUNT(*) > 10;
   ```

3. **Notification**
   - Notify affected users via email
   - Report to authorities if required (GDPR, etc.)
   - Document incident in security log

### Data Breach Response

1. **Contain the breach**
   - Identify affected data
   - Revoke compromised credentials
   - Block malicious IP addresses

2. **Assess impact**
   - Number of users affected
   - Type of data exposed (PII, credentials, etc.)
   - Potential harm to users

3. **Notification timeline**
   - **72 hours**: Notify supervisory authority (GDPR requirement)
   - **Without undue delay**: Notify affected users

---

## 📊 Security Monitoring

### Key Metrics to Monitor

1. **Authentication**
   - Failed login attempts
   - Account lockouts
   - Password reset requests

2. **API Usage**
   - Rate limit hits
   - Error rates (4xx, 5xx)
   - Response times

3. **Data Access**
   - Sensitive data access patterns
   - Unusual download volumes
   - After-hours access

### Recommended Tools

- **Sentry**: Error tracking and performance monitoring
- **Upstash**: Rate limiting and caching
- **Supabase**: Database monitoring and backups
- **Clerk**: User authentication analytics

---

## 🔄 Security Checklist

### Pre-Production

- [ ] All secrets generated and stored securely
- [ ] Environment variables configured (`.env.local`)
- [ ] Clerk authentication configured with 2FA
- [ ] Supabase RLS policies tested
- [ ] Convex schema deployed
- [ ] Upstash Redis rate limiting active
- [ ] Security headers verified
- [ ] HTTPS/TLS configured
- [ ] CORS allowlist configured
- [ ] Rate limiting tested
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak sensitive info
- [ ] Logging configured (no PII in logs)
- [ ] Backup and disaster recovery plan
- [ ] Security scan completed (npm audit, Snyk)

### Post-Production

- [ ] Monitor error rates and alerts
- [ ] Review audit logs weekly
- [ ] Rotate secrets every 90 days
- [ ] Update dependencies monthly
- [ ] Conduct security audits quarterly
- [ ] Review and update RLS policies
- [ ] Test disaster recovery annually
- [ ] GDPR compliance review

---

## 📞 Support & Reporting

### Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

Report security issues to: **security@your-domain.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours.

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Clerk Security Docs](https://clerk.com/docs/security)
- [Supabase Security](https://supabase.com/docs/guides/platform/going-into-prod)
- [Next.js Security](https://nextjs.org/docs/app/building-your-application/configuring/security-headers)
- [GDPR Compliance Guide](https://gdpr.eu/compliance/)

---

**Last Updated**: November 2025
**Version**: 1.0.0
