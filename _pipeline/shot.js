// Usage: NODE_PATH=$(npm root -g) node shot.js <index.html> <out_dir>
// Routes Unsplash to stand.png (the shell can't reach Unsplash); jsDelivr images load for real.
const { chromium } = require('playwright'); const path = require('path');
const [file, out] = [path.resolve(process.argv[2]), path.resolve(process.argv[3] || '.')];
const stand = path.join(__dirname, 'stand.png');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }); const errs = [];
  for (const [n, w, h] of [['desk', 1366, 900], ['phone', 390, 844]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    p.on('pageerror', e => errs.push(n + ': ' + e.message));
    await p.route(/images\.unsplash\.com|fonts\.(googleapis|gstatic)\.com/, r => r.request().url().includes('unsplash') ? r.fulfill({ path: stand, contentType: 'image/png' }) : r.abort());
    await p.goto('file://' + file);
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); } window.scrollTo(0, 0); });
    await p.waitForTimeout(1500);
    const info = await p.evaluate(() => { const hb = document.querySelector('.hero-media img')?.getBoundingClientRect(); const ba = document.getElementById('ba')?.getBoundingClientRect(); const w = document.querySelector('header .logo .word b');
      return { sw: document.documentElement.scrollWidth, ph: document.querySelectorAll('.ph').length, imgs: document.images.length, broken: [...document.images].filter(i => i.complete && !i.naturalWidth).map(i => i.src.slice(0, 90)), hero: hb && [Math.round(hb.width), Math.round(hb.height)], ba: ba && [Math.round(ba.width), Math.round(ba.height)], nameTruncated: w ? w.scrollWidth > w.clientWidth : null }; });
    console.log(n, JSON.stringify(info));
    await p.screenshot({ path: path.join(out, n + '_top.png') });
    const f = await p.$('footer, .foot'); if (f) { await f.scrollIntoViewIfNeeded(); await p.waitForTimeout(400); await f.screenshot({ path: path.join(out, n + '_foot.png') }); }
    if (n === 'desk') { const el = await p.$('#ba'); if (el) { await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(800); await p.screenshot({ path: path.join(out, 'ba_desk.png') }); } }
  }
  console.log('errors', JSON.stringify(errs)); await b.close();
})();
