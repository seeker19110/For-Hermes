/* global JSZip */
importScripts('jszip.min.js');

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.type !== 'crawl-site') return;

  crawlSite(msg.payload)
    .then((filename) => {
      chrome.runtime.sendMessage({ type: 'crawl-finished', ok: true, filename }).catch(() => {});
      sendResponse({ ok: true, filename });
    })
    .catch((err) => {
      chrome.runtime.sendMessage({ type: 'crawl-finished', ok: false, error: err.message }).catch(() => {});
      sendResponse({ ok: false, error: err.message });
    });

  return true;
});

async function crawlSite(payload) {
  const { dataType, includeImages, rootUrl } = payload;
  const urls = sanitizeUrls(payload.urls || [], rootUrl).slice(0, 10);

  if (!urls.length) throw new Error('Нет URL для обхода');

  if (dataType === 'content') {
    const markdown = await buildSiteKnowledgeMarkdown(urls);
    const filename = stampName('site_knowledge', 'md');
    await downloadBlob(new Blob([markdown], { type: 'text/markdown;charset=utf-8' }), filename);
    return filename;
  }

  const filename = await buildSiteDesignZip(urls, includeImages);
  return filename;
}

async function buildSiteKnowledgeMarkdown(urls) {
  const out = [
    '# Site Knowledge Pack',
    '',
    `Generated: ${new Date().toISOString()}`,
    ''
  ];

  for (const url of urls) {
    try {
      const html = await fetchText(url);
      const extracted = extractContentFromHtml(html, url);
      out.push('---', '', `## ${extracted.title}`, '', `Source: ${url}`, '');
      out.push(extracted.markdown, '');
      if (extracted.conclusions.length) {
        out.push('### Conclusions / likely resolutions', '');
        for (const c of extracted.conclusions) out.push(`- ${c}`);
        out.push('');
      }
    } catch (err) {
      out.push('---', '', `## Failed: ${url}`, '', `Error: ${err.message}`, '');
    }
  }

  return out.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
}

async function buildSiteDesignZip(urls, includeImages) {
  const zip = new JSZip();
  const prompt = [
    '# Prompt For AI (Site Mode)',
    '',
    '1. Use all files in `pages/` to understand layout patterns and repeated components.',
    '2. Use `tokens/site_design_tokens.json` for normalized style tokens.',
    '3. Rebuild a coherent responsive design system preserving animation and hierarchy.',
    '4. Keep reusable components for header, cards, lists, forms, and content blocks.',
    ''
  ].join('\n');

  zip.file('AI_PROMPT.md', prompt);

  const tokenAccumulator = {
    colors: new Set(),
    fonts: new Set(),
    animationRules: new Set(),
    mediaRules: new Set()
  };

  const imageSet = new Set();

  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    try {
      const html = await fetchText(url);
      const parsed = extractDesignFromHtml(html, url, includeImages);
      const idx = String(i + 1).padStart(2, '0');
      zip.file(`pages/${idx}-${safeName(parsed.title)}.raw.html`, parsed.rawHtml);
      zip.file(`pages/${idx}-${safeName(parsed.title)}.safe.html`, parsed.safeHtml);
      zip.file(`pages/${idx}-${safeName(parsed.title)}.styles.css`, parsed.styles.join('\n\n'));
      zip.file(`pages/${idx}-${safeName(parsed.title)}.meta.json`, JSON.stringify(parsed.meta, null, 2));

      parsed.tokens.colors.forEach((v) => tokenAccumulator.colors.add(v));
      parsed.tokens.fonts.forEach((v) => tokenAccumulator.fonts.add(v));
      parsed.tokens.animationRules.forEach((v) => tokenAccumulator.animationRules.add(v));
      parsed.tokens.mediaRules.forEach((v) => tokenAccumulator.mediaRules.add(v));

      if (includeImages) {
        parsed.images.forEach((img) => imageSet.add(img));
      }
    } catch (err) {
      const idx = String(i + 1).padStart(2, '0');
      zip.file(`pages/${idx}-failed.txt`, `${url}\n${err.message}`);
    }
  }

  const siteTokens = {
    colors: Array.from(tokenAccumulator.colors).slice(0, 300),
    fonts: Array.from(tokenAccumulator.fonts).slice(0, 100),
    animationRules: Array.from(tokenAccumulator.animationRules).slice(0, 200),
    mediaRules: Array.from(tokenAccumulator.mediaRules).slice(0, 200)
  };

  zip.file('tokens/site_design_tokens.json', JSON.stringify(siteTokens, null, 2));

  if (includeImages && imageSet.size) {
    const images = Array.from(imageSet).slice(0, 120);
    zip.file('images/images.json', JSON.stringify(images, null, 2));

    for (const src of images) {
      if (!/^https?:/i.test(src)) continue;
      try {
        const r = await fetch(src);
        if (!r.ok) continue;
        const blob = await r.blob();
        const ext = extFromType(blob.type);
        const base = safeName(new URL(src).pathname.split('/').pop() || 'image');
        zip.file(`images/assets/${base}${ext}`, blob);
      } catch (_) {
        // ignore single image download failures
      }
    }
  }

  const blob = await zip.generateAsync({ type: 'blob' });
  const filename = stampName('site_design_package', 'zip');
  await downloadBlob(blob, filename);
  return filename;
}

function extractContentFromHtml(html, url) {
  const doc = parseDoc(html);
  const title = (doc.querySelector('title')?.textContent || url).trim();

  const main =
    doc.querySelector('article, main, [role="main"], .post, .entry-content, .thread, .topic, .discussion') ||
    doc.body ||
    doc.documentElement;

  removeNoise(main);

  const nodes = main.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li, blockquote, pre, code');
  const lines = [];
  const conclusions = [];
  const conclusionRe = /(solution|solved|resolved|fix|workaround|root cause|итог|решение|исправ|проблем)/i;

  for (const node of nodes) {
    const text = clean(node.textContent || '');
    if (text.length < 35) continue;

    const linkCount = node.querySelectorAll('a').length;
    const wordCount = text.split(/\s+/).length;
    if (linkCount / Math.max(wordCount, 1) > 0.2) continue;

    const tag = node.tagName.toLowerCase();
    if (tag[0] === 'h') {
      const lvl = Math.min(6, Number(tag[1]) || 2);
      lines.push(`${'#'.repeat(lvl)} ${text}`, '');
    } else if (tag === 'li') {
      lines.push(`- ${text}`);
    } else if (tag === 'blockquote') {
      lines.push(`> ${text}`, '');
    } else if (tag === 'pre' || tag === 'code') {
      lines.push('```text', text, '```', '');
    } else {
      lines.push(text, '');
    }

    if (conclusionRe.test(text)) conclusions.push(text);
  }

  const dedupConclusions = Array.from(new Set(conclusions.map((c) => c.toLowerCase())))
    .map((lc) => conclusions.find((c) => c.toLowerCase() === lc))
    .slice(0, 12);

  return {
    title,
    markdown: lines.join('\n').replace(/\n{3,}/g, '\n\n').trim(),
    conclusions: dedupConclusions
  };
}

function extractDesignFromHtml(html, url, includeImages) {
  const doc = parseDoc(html);
  const title = clean(doc.querySelector('title')?.textContent || url);

  const rawHtml = '<!doctype html>\n' + (doc.documentElement?.outerHTML || html);

  const safeDoc = parseDoc(html);
  safeDoc.querySelectorAll('script, iframe, noscript').forEach((n) => n.remove());
  if (!includeImages) safeDoc.querySelectorAll('img').forEach((n) => n.remove());
  const safeHtml = '<!doctype html>\n' + (safeDoc.documentElement?.outerHTML || safeDoc.body?.innerHTML || '');

  const styleBlocks = Array.from(doc.querySelectorAll('style')).map((s) => s.textContent || '');
  const linkedCss = Array.from(doc.querySelectorAll('link[rel="stylesheet"]')).map((l) => l.href).filter(Boolean);

  const styles = [...styleBlocks, ...linkedCss.map((href) => `/* external stylesheet: ${href} */`)];

  const allStyleText = styleBlocks.join('\n');
  const colorMatches = allStyleText.match(/#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)/g) || [];
  const fontMatches = allStyleText.match(/font-family\s*:\s*([^;]+);/gi) || [];
  const animationMatches = allStyleText.match(/@keyframes[\s\S]*?\}/g) || [];
  const mediaMatches = allStyleText.match(/@media[\s\S]*?\}/g) || [];

  const images = includeImages
    ? Array.from(doc.querySelectorAll('img[src]')).map((img) => resolveAbsolute(img.getAttribute('src') || '', url)).filter(Boolean)
    : [];

  return {
    title,
    rawHtml,
    safeHtml,
    styles,
    images,
    meta: {
      url,
      title,
      linkedCss,
      imageCount: images.length
    },
    tokens: {
      colors: uniq(colorMatches).slice(0, 200),
      fonts: uniq(fontMatches.map((m) => m.replace(/^font-family\s*:\s*/i, '').replace(/;$/, '').trim())).slice(0, 80),
      animationRules: uniq(animationMatches.map((s) => clean(s))).slice(0, 80),
      mediaRules: uniq(mediaMatches.map((s) => clean(s))).slice(0, 80)
    }
  };
}

function removeNoise(root) {
  const noiseSelector = [
    'script',
    'noscript',
    'iframe',
    'nav',
    'header',
    'footer',
    'aside',
    'form',
    'button',
    'input',
    'select',
    'textarea',
    '[role="navigation"]',
    '[role="banner"]',
    '[role="contentinfo"]',
    '.ad',
    '.ads',
    '.advert',
    '.banner',
    '.cookie',
    '.popup',
    '.modal',
    '.newsletter',
    '.subscribe',
    '.social',
    '.share',
    '.toolbar',
    '.menu',
    '.sidebar'
  ].join(',');

  root.querySelectorAll(noiseSelector).forEach((n) => n.remove());
}

function sanitizeUrls(urls, rootUrl) {
  const root = new URL(rootUrl);
  const seen = new Set();
  const out = [];

  for (const candidate of urls) {
    try {
      const u = new URL(candidate, root.href);
      if (!/^https?:$/.test(u.protocol)) continue;
      if (u.hostname !== root.hostname) continue;
      u.hash = '';
      const value = u.href;
      if (seen.has(value)) continue;
      seen.add(value);
      out.push(value);
    } catch (_) {
      // ignore invalid URLs
    }
  }

  if (!seen.has(root.href)) out.unshift(root.href);
  return out;
}

async function fetchText(url) {
  const res = await fetch(url, { redirect: 'follow' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.text();
}

function parseDoc(html) {
  const parser = new DOMParser();
  return parser.parseFromString(html, 'text/html');
}

function resolveAbsolute(href, base) {
  try {
    return new URL(href, base).href;
  } catch (_) {
    return null;
  }
}

function uniq(arr) {
  return Array.from(new Set(arr));
}

function clean(str) {
  return String(str).replace(/\s+/g, ' ').trim();
}

function safeName(name) {
  return name.replace(/[^a-zA-Z0-9._-]/g, '_').slice(0, 80) || 'page';
}

function extFromType(mime) {
  if (mime === 'image/png') return '.png';
  if (mime === 'image/jpeg') return '.jpg';
  if (mime === 'image/webp') return '.webp';
  if (mime === 'image/gif') return '.gif';
  if (mime === 'image/svg+xml') return '.svg';
  return '.bin';
}

async function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  try {
    await chrome.downloads.download({ url, filename, saveAs: false });
  } finally {
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }
}

function stampName(prefix, ext) {
  const d = new Date();
  const stamp = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}_${String(d.getHours()).padStart(2, '0')}-${String(d.getMinutes()).padStart(2, '0')}-${String(d.getSeconds()).padStart(2, '0')}`;
  return `${prefix}_${stamp}.${ext}`;
}
