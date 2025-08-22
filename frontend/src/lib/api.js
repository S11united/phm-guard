const base = import.meta.env.VITE_API_BASE?.replace(/\/+$/,'') || '';

async function tryFetch(url, options, timeoutMs = 20000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(id);
  }
}

export async function runCheck(payload) {
  const targets = [
    base ? `${base}/run` : '/run',
    base ? `${base}/api/run` : '/api/run'
  ];
  let lastErr;
  for (const url of targets) {
    try {
      const res = await tryFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }, 20000);
      if (res.ok) return await res.json();
      lastErr = new Error(`HTTP ${res.status}`);
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr || new Error('runCheck failed');
}

export async function fetchHistory() {
  const targets = [
    base ? `${base}/history` : '/history',
    base ? `${base}/api/history` : '/api/history'
  ];
  for (const url of targets) {
    try {
      const r = await tryFetch(url);
      if (r.ok) return await r.json();
    } catch {}
  }
  return [];
}

export async function fetchLast() {
  const targets = [
    base ? `${base}/last` : '/last',
    base ? `${base}/api/last` : '/api/last',
    base ? `${base}/` : '/'
  ];
  for (const url of targets) {
    try {
      const r = await tryFetch(url, {}, 8000);
      if (r.ok) return await r.json();
    } catch {}
  }
  return null;
}
