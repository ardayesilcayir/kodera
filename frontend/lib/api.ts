import type {
  DesignGenerateError,
  DesignGenerateSuccess,
  DecryptError,
  DecryptSuccess,
  OrbitDesignRequestBody,
  ScanSession,
} from '@/lib/orbitTypes';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GENERATE_TIMEOUT_MS = 120_000;

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } catch (err: any) {
    if (err.name === 'AbortError') {
      throw new Error(`Request timed out after ${Math.round(timeoutMs / 1000)}s — the solver may need lighter parameters`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

async function parseJson(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { parse_error: text };
  }
}

export type { OrbitDesignRequestBody, ScanSession } from '@/lib/orbitTypes';
export type {
  MissionType,
  OrbitFamily,
  DesignResultJson,
  RankedRecommendationJson,
  CoverageMetricsJson,
} from '@/lib/orbitTypes';

export const api = {
  async generateConstellation(data: OrbitDesignRequestBody): Promise<ScanSession> {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/design/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      },
      GENERATE_TIMEOUT_MS,
    );
    const json = (await parseJson(response)) as DesignGenerateSuccess | DesignGenerateError;

    if (!response.ok) {
      const detail = (json as { detail?: unknown }).detail;
      const msg =
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((d) => (d as { msg?: string }).msg).filter(Boolean).join('; ')
            : JSON.stringify(json);
      throw new Error(msg || `Constellation generation failed (${response.status})`);
    }

    if ((json as DesignGenerateError).status === 'error') {
      throw new Error((json as DesignGenerateError).message || 'Design engine error');
    }

    const ok = json as DesignGenerateSuccess;
    if (!ok.encrypted_data) {
      throw new Error('Invalid API response: missing encrypted_data');
    }

    const decRes = await fetch(`${API_BASE_URL}/api/v1/design/decrypt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ encrypted_token: ok.encrypted_data }),
    });
    const decJson = (await parseJson(decRes)) as DecryptSuccess | DecryptError;

    if (!decRes.ok) {
      throw new Error('Decrypt request failed');
    }
    if ((decJson as DecryptError).status === 'error') {
      throw new Error((decJson as DecryptError).message || 'Decrypt failed');
    }

    const design = (decJson as DecryptSuccess).decrypted_data;
    return { request: data, design };
  },

  async repositionSatellite(data: unknown) {
    const response = await fetch(`${API_BASE_URL}/api/v1/design/reposition`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await parseJson(response);
    if (!response.ok) throw new Error('Reposition failed');
    return json;
  },

  async decryptToken(encrypted_token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/design/decrypt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ encrypted_token }),
    });
    const json = (await parseJson(response)) as DecryptSuccess | DecryptError;
    if (!response.ok || json.status === 'error') {
      throw new Error((json as DecryptError).message || 'Decryption failed');
    }
    return json.decrypted_data;
  },

  async getMe(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error('Failed to fetch profile');
    return response.json();
  },
};
