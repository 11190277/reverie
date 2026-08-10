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
    let target;
    if (url.pathname.startsWith('/moss/')) {
      target = 'https://api.mosi.cn' + url.pathname.slice(5) + url.search;
    } else {
      return new Response('add /moss/ prefix', {
        status: 400,
        headers: { 'Access-Control-Allow-Origin': '*' }
      });
    }
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
};
