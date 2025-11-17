/**
 * Encryption Utilities
 * AES-256-GCM encryption for sensitive data
 */

import crypto from "crypto";
import { securityConfig } from "@/config/security.config";

const algorithm = securityConfig.encryption.algorithm;
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;

if (!ENCRYPTION_KEY) {
  throw new Error("ENCRYPTION_KEY environment variable is required");
}

// Derive a 32-byte key from the environment variable
const getKey = (): Buffer => {
  return crypto
    .createHash("sha256")
    .update(String(ENCRYPTION_KEY))
    .digest();
};

/**
 * Encrypt sensitive data
 */
export function encrypt(text: string): {
  encrypted: string;
  iv: string;
  tag: string;
} {
  try {
    const key = getKey();
    const iv = crypto.randomBytes(securityConfig.encryption.ivLength);
    const cipher = crypto.createCipheriv(algorithm, key, iv);

    let encrypted = cipher.update(text, "utf8", "hex");
    encrypted += cipher.final("hex");

    const tag = cipher.getAuthTag();

    return {
      encrypted,
      iv: iv.toString("hex"),
      tag: tag.toString("hex"),
    };
  } catch (error) {
    console.error("Encryption error:", error);
    throw new Error("Failed to encrypt data");
  }
}

/**
 * Decrypt sensitive data
 */
export function decrypt(encrypted: string, iv: string, tag: string): string {
  try {
    const key = getKey();
    const decipher = crypto.createDecipheriv(
      algorithm,
      key,
      Buffer.from(iv, "hex")
    );

    decipher.setAuthTag(Buffer.from(tag, "hex"));

    let decrypted = decipher.update(encrypted, "hex", "utf8");
    decrypted += decipher.final("utf8");

    return decrypted;
  } catch (error) {
    console.error("Decryption error:", error);
    throw new Error("Failed to decrypt data");
  }
}

/**
 * Hash sensitive data (one-way, for comparison)
 */
export async function hash(text: string): Promise<string> {
  const salt = crypto.randomBytes(securityConfig.encryption.saltLength);
  const hash = await new Promise<Buffer>((resolve, reject) => {
    crypto.pbkdf2(
      text,
      salt,
      100000,
      securityConfig.encryption.keyLength,
      "sha512",
      (err, derivedKey) => {
        if (err) reject(err);
        resolve(derivedKey);
      }
    );
  });

  return `${salt.toString("hex")}:${hash.toString("hex")}`;
}

/**
 * Verify hashed data
 */
export async function verifyHash(
  text: string,
  hashedText: string
): Promise<boolean> {
  try {
    const [salt, originalHash] = hashedText.split(":");
    const hash = await new Promise<Buffer>((resolve, reject) => {
      crypto.pbkdf2(
        text,
        Buffer.from(salt, "hex"),
        100000,
        securityConfig.encryption.keyLength,
        "sha512",
        (err, derivedKey) => {
          if (err) reject(err);
          resolve(derivedKey);
        }
      );
    });

    return hash.toString("hex") === originalHash;
  } catch (error) {
    console.error("Hash verification error:", error);
    return false;
  }
}

/**
 * Generate secure random token
 */
export function generateToken(length: number = 32): string {
  return crypto.randomBytes(length).toString("hex");
}

/**
 * Generate API key with prefix
 */
export function generateAPIKey(prefix: string = "oas"): string {
  const randomPart = crypto.randomBytes(32).toString("base64url");
  return `${prefix}_${randomPart}`;
}

/**
 * Securely compare two strings (timing-safe)
 */
export function secureCompare(a: string, b: string): boolean {
  try {
    const bufferA = Buffer.from(a, "utf8");
    const bufferB = Buffer.from(b, "utf8");

    if (bufferA.length !== bufferB.length) {
      return false;
    }

    return crypto.timingSafeEqual(bufferA, bufferB);
  } catch (error) {
    return false;
  }
}
