const startBtn = document.getElementById('startBtn');
const statusEl = document.getElementById('status');

chrome.runtime.onMessage.addListener((msg) => {
  if (!msg || msg.type !== 'crawl-finished') return;
  setStatus(msg.ok ? `Готово: ${msg.filename}` : `Ошибка: ${msg.error}`, !!msg.ok);
});

startBtn.addEventListener('click', () => run().catch((err) => setStatus(err.message || String(err), false)));

async function run() {
  setStatus('Запуск...');

  const dataType = document.getElementById('dataType').value;
  const depth = document.getElementById('depth').value;
  const includeImages = document.getElementById('includeImages').checked;

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id || !tab?.url) throw new Error('Активная вкладка не найдена');

  const rootUrl = new URL(tab.url);
  if (!/^https?:$/.test(rootUrl.protocol)) {
    throw new Error('Поддерживаются только http/https страницы');
  }

  if (depth === 'single') {
    await runSingle(tab.id, { dataType, includeImages });
    return;
  }

  setStatus('Собираю ссылки сайта...');
  const links = await collectSiteLinks(tab.id);
  if (!links.urls.length) {
    throw new Error('Не удалось найти подходящие соседние ссылки');
  }

  setStatus(`Запускаю deep crawl (${links.urls.length} стр.)...`);
  const response = await chrome.runtime.sendMessage({
    type: 'crawl-site',
    payload: {
      dataType,
      includeImages,
      rootUrl: tab.url,
      urls: links.urls
    }
  });
  if (!response?.ok) {
    throw new Error(response?.error || 'Deep crawl завершился с ошибкой');
  }
  setStatus(`Скачано: ${response.filename || 'готово'}`, true);
}

async function runSingle(tabId, config) {
  setStatus('Извлекаю страницу...');

  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: extractCurrentPage,
    args: [config]
  });

  if (!result?.result) throw new Error('Не удалось получить данные страницы');
  const data = result.result;

  if (config.dataType === 'content') {
    const md = data.markdown || '';
    await copyToClipboard(md);
    await downloadBlob(new Blob([md], { type: 'text/markdown;charset=utf-8' }), fileStamp('knowledge', 'md'));
    setStatus('Скачано + скопировано в буфер', true);
    return;
  }

  setStatus('Делаю desktop/mobile скрины...');
  const screenshots = await captureResponsiveScreenshots();

  setStatus('Упаковываю ZIP...');
  const zip = new JSZip();
  zip.file('index.raw.html', data.rawHtml || '');
  zip.file('index.safe.html', data.safeHtml || '');
  zip.file('styles/all-styles.css', data.allStyles || '');
  zip.file('design_tokens.json', JSON.stringify(data.tokens || {}, null, 2));
  zip.file('images/images.json', JSON.stringify(data.images || [], null, 2));
  zip.file('AI_PROMPT.md', buildAIPrompt());

  if (screenshots.desktop) {
    zip.file('screenshots/desktop.png', dataUrlToUint8Array(screenshots.desktop), { binary: true });
  }
  if (screenshots.mobile) {
    zip.file('screenshots/mobile.png', dataUrlToUint8Array(screenshots.mobile), { binary: true });
  }

  if (config.includeImages && Array.isArray(data.images)) {
    const imageUrls = data.images
      .map((i) => i.src)
      .filter((u) => /^https?:/i.test(u))
      .slice(0, 40);

    for (const imgUrl of imageUrls) {
      try {
        const r = await fetch(imgUrl);
        if (!r.ok) continue;
        const contentType = r.headers.get('content-type') || '';
        const bytes = new Uint8Array(await r.arrayBuffer());
        const safeName = safeFileName(new URL(imgUrl).pathname.split('/').pop() || 'image');
        const ext = inferExt(contentType, safeName);
        zip.file(`images/assets/${safeName}${ext}`, bytes, { binary: true });
      } catch (_) {
        // ignore single image failures
      }
    }
  }

  const zipBlob = await zip.generateAsync({ type: 'blob' });
  await downloadBlob(zipBlob, fileStamp('design-package', 'zip'));

  // Single page rule: copy for one page as requested.
  await copyToClipboard(data.safeHtml || data.rawHtml || '');

  setStatus('ZIP скачан + HTML скопирован', true);
}

async function collectSiteLinks(tabId) {
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: collectCrawlLinks
  });

  return result?.result || { urls: [], blocked: false };
}

async function captureResponsiveScreenshots() {
  const win = await chrome.windows.getCurrent();
  const original = {
    width: win.width,
    height: win.height,
    left: win.left,
    top: win.top,
    state: win.state
  };

  const out = { desktop: null, mobile: null };

  try {
    if (win.state !== 'normal') {
      await chrome.windows.update(win.id, { state: 'normal' });
      await sleep(300);
    }

    out.desktop = await chrome.tabs.captureVisibleTab(win.id, { format: 'png' });

    await chrome.windows.update(win.id, {
      width: 420,
      height: 920,
      left: win.left,
      top: win.top
    });
    await sleep(700);
    out.mobile = await chrome.tabs.captureVisibleTab(win.id, { format: 'png' });
  } finally {
    const restore = {
      width: original.width,
      height: original.height,
      left: original.left,
      top: original.top
    };
    if (original.state && original.state !== 'normal') {
      restore.state = original.state;
    }
    await chrome.windows.update(win.id, restore).catch(() => {});
  }

  return out;
}

function extractCurrentPage(config) {
  const noiseSelector = [
    'script',
    'noscript',
    'iframe',
    'svg[aria-hidden="true"]',
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

  const pageMeta = {
    title: document.title,
    url: location.href,
    capturedAt: new Date().toISOString()
  };

  if (config.dataType === 'content') {
    const root =
      document.querySelector('article, main, [role="main"], .post, .entry-content, .thread, .topic, .discussion') ||
      document.body;

    const clone = root.cloneNode(true);
    clone.querySelectorAll(noiseSelector).forEach((n) => n.remove());

    const nodes = clone.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li, blockquote, pre, code');
    const lines = [`# ${pageMeta.title}`, '', `Source: ${pageMeta.url}`, ''];

    const insightHits = [];
    const insightRe = /(solution|solved|resolved|fix|workaround|root cause|итог|решение|исправ|проблем)/i;

    for (const node of nodes) {
      const text = (node.textContent || '').replace(/\s+/g, ' ').trim();
      if (text.length < 35) continue;

      const linkCount = node.querySelectorAll('a').length;
      const wordCount = text.split(/\s+/).length;
      const linkDensity = linkCount / Math.max(wordCount, 1);
      if (linkDensity > 0.2) continue;

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

      if (insightRe.test(text)) insightHits.push(text);
    }

    if (insightHits.length) {
      lines.push('## Conclusions / likely resolutions', '');
      const seen = new Set();
      for (const hit of insightHits) {
        const norm = hit.toLowerCase();
        if (seen.has(norm)) continue;
        seen.add(norm);
        lines.push(`- ${hit}`);
        if (seen.size >= 12) break;
      }
      lines.push('');
    }

    return {
      ...pageMeta,
      markdown: lines.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n'
    };
  }

  const documentClone = document.documentElement.cloneNode(true);
  const safeClone = document.documentElement.cloneNode(true);
  safeClone.querySelectorAll('script, iframe, noscript').forEach((n) => n.remove());
  if (!config.includeImages) {
    safeClone.querySelectorAll('img').forEach((img) => img.remove());
  }

  let allStyles = '';
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      const rules = Array.from(sheet.cssRules || []);
      allStyles += rules.map((r) => r.cssText).join('\n') + '\n';
    } catch (err) {
      if (sheet.href) {
        allStyles += `/* inaccessible stylesheet: ${sheet.href} */\n`;
      }
    }
  }

  const tokens = collectDesignTokens();
  const images = Array.from(document.images).map((img) => ({
    src: img.currentSrc || img.src,
    alt: img.alt || '',
    width: img.naturalWidth || img.width || null,
    height: img.naturalHeight || img.height || null
  }));

  return {
    ...pageMeta,
    rawHtml: '<!doctype html>\n' + documentClone.outerHTML,
    safeHtml: '<!doctype html>\n' + safeClone.outerHTML,
    allStyles,
    tokens,
    images
  };

  function collectDesignTokens() {
    const bodyCS = getComputedStyle(document.body);
    const rootCS = getComputedStyle(document.documentElement);
    const elList = Array.from(document.querySelectorAll('*')).slice(0, 600);

    const colors = new Set();
    const fonts = new Set();
    const transitions = new Set();
    const animations = new Set();

    for (const el of elList) {
      const cs = getComputedStyle(el);
      const color = cs.color;
      const bg = cs.backgroundColor;
      if (color && color !== 'rgba(0, 0, 0, 0)' && color !== 'transparent') colors.add(color);
      if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') colors.add(bg);
      if (cs.fontFamily) fonts.add(cs.fontFamily);
      if (cs.transitionDuration && cs.transitionDuration !== '0s') {
        transitions.add(`${cs.transitionProperty} ${cs.transitionDuration} ${cs.transitionTimingFunction}`);
      }
      if (cs.animationName && cs.animationName !== 'none') {
        animations.add(`${cs.animationName} ${cs.animationDuration} ${cs.animationTimingFunction}`);
      }
    }

    return {
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio
      },
      typography: {
        baseFontFamily: bodyCS.fontFamily,
        baseFontSize: bodyCS.fontSize,
        baseLineHeight: bodyCS.lineHeight,
        uniqueFonts: Array.from(fonts).slice(0, 50)
      },
      colors: Array.from(colors).slice(0, 120),
      motion: {
        transitions: Array.from(transitions).slice(0, 80),
        animations: Array.from(animations).slice(0, 80)
      },
      cssVariables: collectCssVars(rootCS)
    };
  }

  function collectCssVars(styleDecl) {
    const vars = {};
    for (let i = 0; i < styleDecl.length; i++) {
      const key = styleDecl[i];
      if (!key.startsWith('--')) continue;
      vars[key] = styleDecl.getPropertyValue(key).trim();
    }
    return vars;
  }
}

function collectCrawlLinks() {
  const root = new URL(location.href);
  const links = Array.from(document.querySelectorAll('a[href]'));
  const badPath = /(login|signup|register|cart|checkout|privacy|terms|cookie|wp-admin|feed|\/settings|\/notifications)/i;
  const topicWords = buildTopicWords();
  const scored = [];

  for (const [idx, a] of links.entries()) {
    try {
      const u = new URL(a.href, root.href);
      if (u.hostname !== root.hostname) continue;
      if (!/^https?:$/.test(u.protocol)) continue;
      u.hash = '';
      if (badPath.test(u.pathname)) continue;
      const href = u.href;
      const anchorText = (a.textContent || '').trim();
      const score = scoreLink(href, anchorText, idx);
      scored.push({ href, score });
    } catch (_) {
      // ignore
    }
  }

  scored.sort((a, b) => b.score - a.score);

  const out = new Set([root.href]);
  for (const row of scored) {
    out.add(row.href);
    if (out.size >= 10) break;
  }

  return { urls: Array.from(out).slice(0, 10), blocked: false };

  function buildTopicWords() {
    const stop = new Set([
      'the', 'and', 'for', 'with', 'from', 'that', 'this', 'your', 'you', 'are', 'not', 'all', 'new',
      'home', 'docs', 'blog', 'post', 'page', 'about', 'what', 'how', 'why', 'when', 'where',
      'или', 'для', 'как', 'это', 'что', 'над', 'под', 'без', 'про', 'при', 'есть'
    ]);
    const source = [
      document.title || '',
      location.pathname || '',
      (document.querySelector('h1')?.textContent || '')
    ].join(' ');
    return source
      .toLowerCase()
      .split(/[^a-z0-9а-яё]+/i)
      .filter((w) => w.length >= 3 && !stop.has(w))
      .slice(0, 40);
  }

  function scoreLink(href, anchorText, idx) {
    const value = `${href} ${anchorText}`.toLowerCase();
    let score = 0;

    for (const w of topicWords) {
      if (value.includes(w)) score += 6;
    }

    const rootSeg = root.pathname.split('/').filter(Boolean)[0];
    const pathSeg = new URL(href).pathname.split('/').filter(Boolean)[0];
    if (rootSeg && pathSeg && rootSeg === pathSeg) score += 18;

    if (/thread|discussion|issue|pull|commit|wiki|readme|docs|article|blog/i.test(value)) score += 12;
    if (/\/blob\/|\/tree\/|\/issues\/|\/pull\//i.test(href)) score += 10;

    // Slight preference to links visible earlier on page.
    score += Math.max(0, 8 - Math.floor(idx / 40));
    return score;
  }
}

function dataUrlToUint8Array(dataUrl) {
  const base64 = dataUrl.split(',')[1] || '';
  const bin = atob(base64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

function inferExt(mime, fallbackName) {
  if (fallbackName.includes('.')) return '';
  if (mime === 'image/png') return '.png';
  if (mime === 'image/webp') return '.webp';
  if (mime === 'image/gif') return '.gif';
  if (mime === 'image/svg+xml') return '.svg';
  if (mime === 'image/jpeg') return '.jpg';
  return '.bin';
}

function safeFileName(name) {
  return name.replace(/[^a-zA-Z0-9._-]/g, '_').slice(0, 80) || 'file';
}

function buildAIPrompt() {
  return [
    '# Prompt For AI Reconstruction',
    '',
    '1. Use `index.safe.html` for safe DOM structure and `index.raw.html` for JS logic hints.',
    '2. Use `styles/all-styles.css` and `design_tokens.json` as source of truth for colors, typography, spacing, and animation.',
    '3. Compare `screenshots/desktop.png` vs `screenshots/mobile.png` and implement responsive behavior.',
    '4. Rebuild as clean components (React + Tailwind or vanilla) with the same layout and motion.',
    '5. Keep accessibility: semantic tags, alt text, keyboard focus states.',
    ''
  ].join('\n');
}

function setStatus(text, ok = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle('ok', ok);
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (_) {
    // Clipboard can fail in restricted pages; don't block download.
  }
}

async function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  try {
    await chrome.downloads.download({ url, filename, saveAs: false });
  } finally {
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  }
}

function fileStamp(prefix, ext) {
  const d = new Date();
  const stamp = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}_${String(d.getHours()).padStart(2, '0')}-${String(d.getMinutes()).padStart(2, '0')}-${String(d.getSeconds()).padStart(2, '0')}`;
  return `${prefix}_${stamp}.${ext}`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
