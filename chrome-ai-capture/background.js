/* global JSZip */
importScripts('jszip.min.js');

const MAX_RAW_HTML_CHARS = 300000;
const MAX_SAFE_HTML_CHARS = 300000;
const MAX_STYLES_CHARS = 180000;
const MAX_IMAGES_IN_SITE_DESIGN = 40;

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
      if (!extracted.markdown || extracted.markdown.length < 80) {
        continue;
      }
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
      const rawHtmlTrimmed = clampText(parsed.rawHtml, MAX_RAW_HTML_CHARS, `Raw HTML truncated for ${url}`);
      const safeHtmlTrimmed = clampText(parsed.safeHtml, MAX_SAFE_HTML_CHARS, `Safe HTML truncated for ${url}`);
      const stylesText = parsed.styles.join('\n\n');
      const stylesTrimmed = clampText(stylesText, MAX_STYLES_CHARS, `Styles truncated for ${url}`);

      zip.file(`pages/${idx}-${safeName(parsed.title)}.raw.html`, rawHtmlTrimmed);
      zip.file(`pages/${idx}-${safeName(parsed.title)}.safe.html`, safeHtmlTrimmed);
      zip.file(`pages/${idx}-${safeName(parsed.title)}.styles.css`, stylesTrimmed);
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
    const images = Array.from(imageSet).slice(0, MAX_IMAGES_IN_SITE_DESIGN);
    zip.file('images/images.json', JSON.stringify(images, null, 2));

    for (const src of images) {
      if (!/^https?:/i.test(src)) continue;
      try {
        const r = await fetch(src);
        if (!r.ok) continue;
        const contentType = r.headers.get('content-type') || '';
        const ext = extFromType(contentType);
        const bytes = new Uint8Array(await r.arrayBuffer());
        const base = safeName(new URL(src).pathname.split('/').pop() || 'image');
        zip.file(`images/assets/${base}${ext}`, bytes, { binary: true });
      } catch (_) {
        // ignore single image download failures
      }
    }
  }

  const blob = await zip.generateAsync({
    type: 'blob',
    compression: 'DEFLATE',
    compressionOptions: { level: 6 }
  });
  const filename = stampName('site_design_package', 'zip');

  try {
    await downloadBlob(blob, filename);
    return filename;
  } catch (err) {
    const fallbackName = stampName('site_design_fallback', 'md');
    const fallbackBody = buildDesignFallbackReport(urls, err);
    await downloadBlob(new Blob([fallbackBody], { type: 'text/markdown;charset=utf-8' }), fallbackName);
    return fallbackName;
  }
}

function extractContentFromHtml(html, url) {
  const title = extractTitle(html, url);
  const sourceHtml = stripNoiseHtml(pickMainSectionHtml(html));
  const nodes = extractTagBlocks(sourceHtml, ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote', 'pre', 'code']);
  const lines = [];
  const conclusions = [];
  const seen = new Set();
  const isGithubIssuesOrPulls = /github\.com\/[^/]+\/[^/]+\/(issues|pulls)\b/i.test(url);
  const isGithubOrgRoot = /github\.com\/[^/]+\/?(?:\?.*)?$/i.test(url);
  const conclusionRe = /(solution|solved|resolved|fix|workaround|root cause|итог|решение|исправ|проблем)/i;

  for (const node of nodes) {
    const text = normalizeKnowledgeText(htmlToText(node.innerHtml));
    if (isBoilerplateKnowledgeLine(text)) continue;
    if (text.length < 35) continue;

    const linkCount = (node.innerHtml.match(/<a\b/gi) || []).length;
    const wordCount = text.split(/\s+/).length;
    if (linkCount / Math.max(wordCount, 1) > 0.2) continue;
    const key = text.toLowerCase();
    if (seen.has(key)) continue;

    const tag = node.tag.toLowerCase();
    if (isGithubOrgRoot && (tag === 'li' || tag === 'p')) {
      const compactRepo = compactGithubOrgRepoLine(text);
      if (!compactRepo) continue;

      const repoName = compactRepo.split(':')[0].trim().toLowerCase();
      const repoSeenKey = `repo:${repoName}`;
      if (seen.has(repoSeenKey)) continue;
      seen.add(repoSeenKey);

      lines.push(`- ${compactRepo}`);
      continue;
    }

    if (isGithubIssuesOrPulls && (tag === 'li' || tag === 'p')) {
      const compact = compactGithubIssueLine(text);
      if (!compact) continue;
      const compactKey = compact.toLowerCase();
      if (seen.has(compactKey)) continue;
      seen.add(compactKey);
      lines.push(`- ${compact}`);
      if (conclusionRe.test(compact)) conclusions.push(compact);
      continue;
    }

    seen.add(key);
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
  const title = extractTitle(html, url);

  const rawHtml = ensureDoctype(html);
  let safeHtmlBody = html
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<iframe\b[^>]*>[\s\S]*?<\/iframe>/gi, '')
    .replace(/<noscript\b[^>]*>[\s\S]*?<\/noscript>/gi, '');
  if (!includeImages) {
    safeHtmlBody = safeHtmlBody.replace(/<img\b[^>]*>/gi, '');
  }
  const safeHtml = ensureDoctype(safeHtmlBody);

  const styleBlocks = [];
  const styleRe = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
  let styleMatch;
  while ((styleMatch = styleRe.exec(html)) !== null) {
    styleBlocks.push(styleMatch[1] || '');
  }

  const linkedCss = [];
  const linkRe = /<link\b[^>]*>/gi;
  let linkMatch;
  while ((linkMatch = linkRe.exec(html)) !== null) {
    const tag = linkMatch[0];
    const rel = (extractAttr(tag, 'rel') || '').toLowerCase();
    if (!rel.includes('stylesheet')) continue;
    const href = extractAttr(tag, 'href');
    if (!href) continue;
    const absolute = resolveAbsolute(href, url);
    if (absolute) linkedCss.push(absolute);
  }

  const styles = [...styleBlocks, ...linkedCss.map((href) => `/* external stylesheet: ${href} */`)];

  const allStyleText = styleBlocks.join('\n');
  const colorMatches = allStyleText.match(/#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)/g) || [];
  const fontMatches = allStyleText.match(/font-family\s*:\s*([^;]+);/gi) || [];
  const animationMatches = allStyleText.match(/@keyframes[\s\S]*?\}/g) || [];
  const mediaMatches = allStyleText.match(/@media[\s\S]*?\}/g) || [];

  const images = [];
  if (includeImages) {
    const imgRe = /<img\b[^>]*>/gi;
    let imgMatch;
    while ((imgMatch = imgRe.exec(html)) !== null) {
      const src = extractAttr(imgMatch[0], 'src');
      const absolute = resolveAbsolute(src || '', url);
      if (absolute) images.push(absolute);
    }
  }

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

function resolveAbsolute(href, base) {
  try {
    return new URL(href, base).href;
  } catch (_) {
    return null;
  }
}

function ensureDoctype(html) {
  return /^\s*<!doctype/i.test(html) ? html : `<!doctype html>\n${html}`;
}

function extractTitle(html, fallback) {
  const m = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  let title = clean(htmlToText((m && m[1]) || fallback));
  if (/^github\s*[·-]\s*where software is built$/i.test(title)) {
    title = githubTitleFromUrl(fallback);
  }
  return title;
}

function pickMainSectionHtml(html) {
  const patterns = [
    /<article\b[^>]*>[\s\S]*?<\/article>/i,
    /<main\b[^>]*>[\s\S]*?<\/main>/i,
    /<div\b[^>]*(id|class)=["'][^"']*(content|post|entry-content|thread|topic|discussion)[^"']*["'][^>]*>[\s\S]*?<\/div>/i,
    /<body\b[^>]*>[\s\S]*?<\/body>/i
  ];
  for (const p of patterns) {
    const m = html.match(p);
    if (m && m[0]) return m[0];
  }
  return html;
}

function stripNoiseHtml(html) {
  let out = html;
  const removeTags = ['script', 'style', 'noscript', 'iframe', 'nav', 'header', 'footer', 'aside', 'form', 'button', 'select', 'textarea'];
  for (const tag of removeTags) {
    const re = new RegExp(`<${tag}\\b[^>]*>[\\s\\S]*?<\\/${tag}>`, 'gi');
    out = out.replace(re, ' ');
  }
  out = out.replace(/<input\b[^>]*>/gi, ' ');
  out = out.replace(/\s(?:class|id)=["'][^"']*(ad|ads|advert|banner|cookie|popup|modal|newsletter|subscribe|social|share|toolbar|menu|sidebar)[^"']*["'][^>]*>/gi, '>');
  return out;
}

function extractTagBlocks(html, tags) {
  const tagPattern = tags.join('|');
  const re = new RegExp(`<(${tagPattern})\\b[^>]*>([\\s\\S]*?)<\\/\\1>`, 'gi');
  const out = [];
  let m;
  while ((m = re.exec(html)) !== null) {
    out.push({ tag: (m[1] || '').toLowerCase(), innerHtml: m[2] || '' });
  }
  return out;
}

function extractAttr(tagHtml, attrName) {
  const re = new RegExp(`${attrName}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i');
  const m = tagHtml.match(re);
  return m ? (m[2] || m[3] || m[4] || '').trim() : null;
}

function htmlToText(html) {
  const withBreaks = html
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|li|h1|h2|h3|h4|h5|h6|blockquote|pre)>/gi, '\n');
  const noTags = withBreaks.replace(/<[^>]+>/g, ' ');
  return decodeEntities(noTags).replace(/\s+/g, ' ').trim();
}

function decodeEntities(text) {
  return text
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCharCode(parseInt(dec, 10)));
}

function normalizeKnowledgeText(text) {
  let out = clean(text);
  if (!out) return out;

  // Common on GitHub: repeated accessibility labels or duplicated status chips.
  for (let i = 0; i < 4; i++) {
    const prev = out;
    out = out.replace(/((?:[^\s]+\s+){1,7}[^\s]+)\s+\1/gi, '$1');
    if (out === prev) break;
  }

  out = out.replace(/\s*·\s*/g, ' · ');
  out = out.replace(/<\/?[^>]+>/g, ' ');
  out = out.replace(/\s{2,}/g, ' ').trim();
  return out;
}

function isBoilerplateKnowledgeLine(text) {
  const t = text.trim();
  if (!t) return true;

  const patterns = [
    /^there was an error while loading/i,
    /^please reload this page/i,
    /^github\s*[·-]\s*where software is built$/i,
    /^first time contributing to /i,
    /^you can read this repository.?s contributing guidelines/i,
    /^if you know how to fix an issue/i,
    /want to contribute to /i,
    /^insights:\s*/i,
    /^pull requests:\s*/i,
    /^issues:\s*/i
  ];

  return patterns.some((re) => re.test(t));
}

function compactGithubIssueLine(text) {
  if (!text || text.length < 18) return '';
  let t = text;

  const junkSnippets = [
    'This issue or pull request already exists',
    "Issue doesn't seem to be related to Claude Code",
    "Something isn't working",
    'New feature or request',
    'Issue specifically occurs on macOS',
    'Issue specifically occurs on Windows',
    'Good for newcomers',
    'Non-showstopper bug or popular feature request',
    'Minor bug or general feature request',
    'Showstopper bug preventing substantial subset of users from using the product, or incorrect docs'
  ];
  for (const j of junkSnippets) {
    const re = new RegExp(escapeRegex(j), 'gi');
    t = t.replace(re, ' ');
  }

  t = t.replace(/\s+/g, ' ').trim();

  const issueMeta = t.match(/Status:\s*([A-Za-z]+)\.\s*#\s*(\d+)\s+In\s+([^;]+);\s*·\s*([A-Za-z0-9._-]+)\s+opened on\s+(.+)$/i);
  if (issueMeta) {
    const status = issueMeta[1];
    const id = issueMeta[2];
    const repo = clean(issueMeta[3]);
    const author = issueMeta[4];
    const opened = clean(issueMeta[5]);

    let title = t.slice(0, issueMeta.index).trim();
    title = title.replace(/\s+(bug|enhancement|invalid|feature-request|model|platform:[^\s]+|provider:[^\s]+|p[123]|dev-experience|area:[^\s]+)(\s|$)/gi, ' ');
    title = title.replace(/\b(p[123]|platform:[^\s]+|provider:[^\s]+|dev-experience|area:[^\s]+)\b/gi, ' ');
    title = title.replace(/\s+/g, ' ').trim();
    if (!title || title.length < 6) return '';

    return `#${id} [${status}] ${title} (${repo}) — ${author}, ${opened}`;
  }

  // Fallback for simpler list items like: "Code reviews keep timing out # 674 · chicks-net opened on Nov 12, 2025"
  const fallback = t.match(/^(.*?)\s+#\s*(\d+)\s*·\s*([A-Za-z0-9._-]+)\s+opened on\s+(.+)$/i);
  if (fallback) {
    const title = clean(fallback[1]);
    if (title.length < 6) return '';
    return `#${fallback[2]} ${title} — ${fallback[3]}, ${clean(fallback[4])}`;
  }

  return '';
}

function githubTitleFromUrl(url) {
  try {
    const u = new URL(url);
    const seg = u.pathname.split('/').filter(Boolean);
    if (seg.length >= 2) {
      const repo = `${seg[0]}/${seg[1]}`;
      const tail = seg[2] ? `/${seg[2]}` : '';
      return `GitHub ${repo}${tail}`;
    }
  } catch (_) {
    // ignore
  }
  return 'GitHub';
}

function compactGithubOrgRepoLine(text) {
  if (!/\bPublic\b/i.test(text)) return '';

  let t = clean(text);
  t = t.replace(/\s+\S+\/\S+['’]s past year of commit activity[\s\S]*$/i, '');
  t = t.replace(/\s+Updated\s+\w+\s+\d{1,2},\s+\d{4}.*$/i, '');

  let repo = '';
  let m = t.match(/^([A-Za-z0-9._-]+)\s+\1\b/i);
  if (m) {
    repo = m[1];
    t = t.replace(/^([A-Za-z0-9._-]+)\s+\1\b/i, '$1');
  }
  if (!repo) {
    m = t.match(/^([A-Za-z0-9._-]+)\s+Public\b/i);
    if (m) repo = m[1];
  }
  if (!repo) return '';

  t = t.replace(new RegExp(`^${escapeRegex(repo)}\\s+`, 'i'), '');
  t = t.replace(/^Public\s+/i, '');
  t = t.replace(/\s+[A-Za-z+#.][A-Za-z0-9+#. -]{0,20}\s+\d[\d.,kKM+]*\s+\d[\d.,kKM+]*$/, '');
  t = clean(t);
  if (t.length < 12) return '';

  return `${repo}: ${t}`;
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function clampText(text, maxChars, note) {
  const value = String(text || '');
  if (value.length <= maxChars) return value;
  return `${value.slice(0, maxChars)}\n\n<!-- ${note}; original_size=${value.length} -->\n`;
}

function buildDesignFallbackReport(urls, err) {
  const out = [
    '# Design Capture Fallback',
    '',
    `Generated: ${new Date().toISOString()}`,
    '',
    `Reason: ${err && err.message ? err.message : String(err)}`,
    '',
    'The full ZIP could not be saved. This fallback confirms crawl execution and lists processed URLs.',
    '',
    '## URLs',
    ''
  ];
  for (const url of urls) out.push(`- ${url}`);
  out.push('');
  out.push('Use: fewer pages, disable images, or run single-page Design mode for full fidelity.');
  out.push('');
  return out.join('\n');
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
  let objectUrl;
  try {
    objectUrl = URL.createObjectURL(blob);
    const downloadId = await chrome.downloads.download({ url: objectUrl, filename, saveAs: false });
    if (downloadId || downloadId === 0) return;
  } catch (_) {
    // fallback below
  } finally {
    if (objectUrl) {
      setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
    }
  }

  // Fallback for environments where blob URLs are unreliable in service workers.
  if (blob.size > 8 * 1024 * 1024) {
    throw new Error('Файл слишком большой для fallback-скачивания. Выберите Content mode или меньше страниц.');
  }

  const dataUrl = await blobToDataUrl(blob);
  const fallbackId = await chrome.downloads.download({ url: dataUrl, filename, saveAs: false });
  if (!fallbackId && fallbackId !== 0) {
    throw new Error('Chrome downloads API не вернул downloadId');
  }
}

async function blobToDataUrl(blob) {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  let binary = '';
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
  }
  const mime = blob.type || 'application/octet-stream';
  return `data:${mime};base64,${btoa(binary)}`;
}

function stampName(prefix, ext) {
  const d = new Date();
  const stamp = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}_${String(d.getHours()).padStart(2, '0')}-${String(d.getMinutes()).padStart(2, '0')}-${String(d.getSeconds()).padStart(2, '0')}`;
  return `${prefix}_${stamp}.${ext}`;
}
