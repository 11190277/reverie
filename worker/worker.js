const SB_URL = 'https://uuwxsxurutcpuotmqgce.supabase.co/rest/v1/eli_shared_memory';
const SB_KEY = 'sb_publishable_uKuxx2yiM9kqDKPki-EVJg_LnENlLLY';

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Max-Age': '86400'
        }
      });
    }

    const url = new URL(request.url);

    // Kelivo记忆写入接口
    if (url.pathname === '/eli-memory') {
      const content = url.searchParams.get('content');
      if (!content) {
        return new Response('missing content', { status: 400, headers: { 'Access-Control-Allow-Origin': '*' } });
      }
      const resp = await fetch(SB_URL, {
        method: 'POST',
        headers: {
          'apikey': SB_KEY,
          'Authorization': 'Bearer ' + SB_KEY,
          'Content-Type': 'application/json',
          'Prefer': 'resolution=merge-duplicates'
        },
        body: JSON.stringify({ id: 'kelivo', content, updated_at: new Date().toISOString() })
      });
      return new Response(resp.ok ? 'ok' : 'fail', {
        status: resp.ok ? 200 : 500,
        headers: { 'Access-Control-Allow-Origin': '*' }
      });
    }

    // Moss TTS中转
    if (url.pathname.startsWith('/moss/')) {
      const target = 'https://api.mosi.cn' + url.pathname.slice(5) + url.search;
      const headers = new Headers(request.headers);
      headers.delete('host');
      headers.delete('origin');
      headers.delete('referer');
      const resp = await fetch(target, {
        method: request.method,
        headers,
        body: (request.method === 'GET' || request.method === 'HEAD') ? undefined : request.body
      });
      const out = new Response(resp.body, resp);
      out.headers.set('Access-Control-Allow-Origin', '*');
      out.headers.set('Access-Control-Expose-Headers', '*');
      return out;
    }

   // 花园MCP中转
if (url.pathname.startsWith('/garden/')) {
  const target = 'https://galatea.abysslumina.com' + url.pathname.slice(7) + url.search;
  const reqHeaders = new Headers();
  for (const [k, v] of request.headers.entries()) {
    const kl = k.toLowerCase();
    if (kl === 'host' || kl === 'origin' || kl === 'referer') continue;
    reqHeaders.set(k, v);
  }
  reqHeaders.set('Accept', 'application/json, text/event-stream');
  const body = (request.method === 'GET' || request.method === 'HEAD') ? undefined : await request.arrayBuffer();
  const resp = await fetch(target, {
    method: request.method,
    headers: reqHeaders,
    body
  });
  const respHeaders = new Headers(resp.headers);
  respHeaders.set('Access-Control-Allow-Origin', '*');
  respHeaders.set('Access-Control-Allow-Headers', '*');
  respHeaders.set('Access-Control-Expose-Headers', '*');
  return new Response(resp.body, {
    status: resp.status,
    statusText: resp.statusText,
    headers: respHeaders
  });
}
