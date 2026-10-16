// Drop-in for the chrome-devtools MCP `evaluate_script` (and adaptable to Playwright page.evaluate).
// Page: any job-search results page (SEEK/JobStreet, Indeed search, company "all jobs" pages).
// Returns unique job links with their nearest card text — far smaller than a full page snapshot.
//
// Usage (chrome-devtools): evaluate_script(pageId: <list page>, waitForStableDom: false, function: <this file's body>)
() => {
  const out = [];
  const seen = new Set();
  document
    .querySelectorAll('a[href*="/job/"], a[href*="/viewjob"], a[href*="jk="], a[href*="/jobs/view"]')
    .forEach(a => {
      const href = a.href.split('?')[0];
      if (!href || seen.has(href)) return;
      seen.add(href);
      const card =
        a.closest('article') ||
        a.closest('[data-card-type]') ||
        a.closest('li') ||
        a.closest('div');
      const txt = (card?.innerText || a.innerText || '')
        .replace(/\n+/g, ' | ')
        .trim()
        .slice(0, 350);
      out.push({href, txt});
    });
  return {
    title: document.title,
    heading: document.querySelector('h1')?.innerText,
    count: out.length,
    jobs: out.slice(0, 40)
  };
}

// Companion: extract readable text from a job DETAIL page (for fingerprint comparison):
// () => ({title: document.title, url: location.href,
//         text: document.body.innerText.replace(/\n{2,}/g, '\n').slice(0, 6000)})
//
// Companion: extract search-engine results (DuckDuckGo / Bing DOM):
// () => { const res = [];
//   document.querySelectorAll('article[data-testid="result"], li.b_algo').forEach(li => {
//     const a = li.querySelector('a[data-testid="result-title-a"], h2 a');
//     if (a) res.push({title: a.innerText.slice(0,150), url: a.href.slice(0,160),
//                      snippet: (li.innerText||'').slice(0,220)}); });
//   return {title: document.title, results: res.slice(0,15)}; }
