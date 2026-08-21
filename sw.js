self.addEventListener('install', e => {
  e.waitUntil(
    caches.open('reverie-v1').then(c =>
      c.addAll(['/', '/index.html', '/eventide.js', '/icon.png'])
    )
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
