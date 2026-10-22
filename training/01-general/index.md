---
layout: default
title: Training Outlines
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --tc-navy: #0c2340;
  --tc-navy-2: #14355c;
  --tc-gold: #c99b2e;
  --tc-gold-deep: #8a6813;
  --tc-ink: #1a2735;
  --tc-muted: #5b6b7d;
  --tc-line: #e3e8ef;
  --tc-paper: #f5f7fa;
}

/* Widen the theme's default 500px content column for this catalogue page only. */
body {
  padding: 0;
  margin: 0;
  background: var(--tc-paper);
  color: var(--tc-ink);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.6;
}
a { color: var(--tc-navy-2); }
a:hover, a:focus { color: var(--tc-gold-deep); font-weight: inherit; }

.wrapper {
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 28px 56px;
}

header {
  position: static;
  float: none;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 22px 0 18px;
  margin: 0 0 26px;
  border-bottom: 1px solid var(--tc-line);
}
header h1 {
  margin: 0;
  font-family: 'Sora', 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: .2px;
}
header h1 a { color: var(--tc-navy); text-decoration: none; }
header h1 a:hover { color: var(--tc-gold-deep); }
header p:not(.view) { display: none; }
header .view { margin: 0; }
header .view a {
  display: inline-block;
  padding: 7px 12px;
  border: 1px solid var(--tc-line);
  border-radius: 999px;
  background: #fff;
  color: var(--tc-navy);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
}
header .view a:hover { border-color: var(--tc-gold); color: var(--tc-gold-deep); }

section {
  width: 100%;
  float: none;
  border: 0;
  padding: 0;
  margin: 0;
}

footer {
  position: static;
  float: none;
  width: 100%;
  margin-top: 48px;
  padding: 20px 0 0;
  border-top: 1px solid var(--tc-line);
  color: var(--tc-muted);
  font-size: 12px;
}
footer p { margin: 0; }
footer small { font-size: 12px; }

/* Hero */
.tc-hero {
  position: relative;
  overflow: hidden;
  color: #fff;
  background: linear-gradient(135deg, #0a1e38 0%, #0c2340 48%, #14355c 100%);
  border-radius: 22px;
  padding: 46px 46px 42px;
  margin: 4px 0 46px;
  box-shadow: 0 18px 44px rgba(12,35,64,.18);
}
.tc-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(560px 300px at 90% -10%, rgba(201,155,46,.30), transparent 65%),
    radial-gradient(480px 260px at -5% 115%, rgba(38,92,150,.55), transparent 60%);
}
.tc-hero::after {
  content: "";
  position: absolute;
  inset: 0;
  opacity: .05;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255,255,255,.7) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.7) 1px, transparent 1px);
  background-size: 46px 46px;
}
.tc-hero > * { position: relative; z-index: 1; }
.tc-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  padding: 7px 14px;
  border: 1px solid rgba(201,155,46,.55);
  border-radius: 999px;
  background: rgba(201,155,46,.16);
  color: #eccf83;
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}
.tc-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--tc-gold);
  box-shadow: 0 0 10px rgba(201,155,46,.9);
}
.tc-hero h1 {
  margin: 0 0 14px;
  color: #fff;
  font-family: 'Sora', 'Inter', sans-serif;
  font-size: clamp(32px, 4.2vw, 46px);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -.6px;
}
.tc-hero p {
  max-width: 780px;
  margin: 0;
  color: #b9c8da;
  font-size: 17px;
  line-height: 1.65;
}
.tc-hero p a { color: #e9c96b; text-decoration: underline; text-underline-offset: 2px; }
.tc-hero p a:hover { color: #fff; }
.tc-hero-tags { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 26px; }
.tc-hero-tags span {
  padding: 7px 13px;
  border: 1px solid rgba(255,255,255,.17);
  border-radius: 999px;
  background: rgba(255,255,255,.07);
  color: #e6edf5;
  font-size: 12px;
  font-weight: 600;
}

/* Category groups */
.tc-group { margin: 0 0 46px; }
.tc-group-head { margin-bottom: 20px; }
.tc-kicker {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 7px;
  color: var(--tc-gold-deep);
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 1.7px;
  text-transform: uppercase;
}
.tc-kicker::before {
  content: "";
  width: 28px;
  height: 3px;
  border-radius: 2px;
  background: var(--tc-gold);
}
.tc-group h2,
.tc-profile h2 {
  margin: 0 0 6px;
  color: var(--tc-navy);
  font-family: 'Sora', 'Inter', sans-serif;
  font-size: clamp(23px, 2.6vw, 29px);
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -.3px;
}
.tc-group-head p {
  max-width: 760px;
  margin: 0;
  color: var(--tc-muted);
  font-size: 14.5px;
  line-height: 1.6;
}

/* Cards */
.tc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 22px;
}
.tc-card {
  --tc-accent: linear-gradient(90deg, #c99b2e, #e8c96a);
  --tc-accent-soft: #fdf6e3;
  --tc-accent-ink: #8a6813;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 26px 26px 22px;
  border: 1px solid var(--tc-line);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(12,35,64,.04), 0 10px 26px rgba(12,35,64,.06);
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.tc-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  border-radius: 18px 18px 0 0;
  background: var(--tc-accent);
}
.tc-card:hover {
  transform: translateY(-5px);
  border-color: #d3dce8;
  box-shadow: 0 18px 42px rgba(12,35,64,.14);
}
.tc-card--green {
  --tc-accent: linear-gradient(90deg, #1f7a4d, #48a877);
  --tc-accent-soft: #e8f5ee;
  --tc-accent-ink: #155c39;
}
.tc-card--blue {
  --tc-accent: linear-gradient(90deg, #1d4470, #3c76b0);
  --tc-accent-soft: #e8f0f8;
  --tc-accent-ink: #173a5f;
}
.tc-card-top { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.tc-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--tc-accent-soft);
  color: var(--tc-accent-ink);
}
.tc-icon svg { width: 22px; height: 22px; }
.tc-pill {
  margin-left: auto;
  padding: 6px 11px;
  border-radius: 999px;
  background: var(--tc-navy);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .55px;
  text-transform: uppercase;
  white-space: nowrap;
}
.tc-title {
  margin: 0 0 5px;
  font-family: 'Sora', 'Inter', sans-serif;
  font-size: 21px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -.2px;
}
.tc-title a { color: var(--tc-navy); text-decoration: none; }
.tc-title a:hover { color: var(--tc-gold-deep); }
.tc-subtitle {
  margin: 0 0 12px;
  color: var(--tc-accent-ink);
  font-size: 13.5px;
  font-weight: 600;
  line-height: 1.45;
}
.tc-desc {
  margin: 0 0 16px;
  color: var(--tc-muted);
  font-size: 14px;
  line-height: 1.65;
}
.tc-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 20px; }
.tc-tag {
  padding: 4px 9px;
  border: 1px solid var(--tc-line);
  border-radius: 6px;
  background: var(--tc-paper);
  color: #41546a;
  font-size: 11px;
  font-weight: 600;
}
.tc-card-foot {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: auto;
  padding-top: 17px;
  border-top: 1px solid #eef1f5;
}
.tc-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 11px 15px;
  border-radius: 9px;
  background: var(--tc-navy);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  line-height: 1;
  text-decoration: none;
  transition: background .18s ease, color .18s ease;
}
.tc-btn svg { width: 15px; height: 15px; }
.tc-btn:hover,
.tc-btn:focus { background: var(--tc-gold); color: var(--tc-navy); font-weight: 600; }
.tc-doc {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 10px 11px;
  border: 1px solid var(--tc-line);
  border-radius: 9px;
  background: #fff;
  color: var(--tc-muted);
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  text-decoration: none;
}
.tc-doc svg { width: 14px; height: 14px; }
.tc-doc:hover,
.tc-doc:focus { border-color: var(--tc-gold); color: var(--tc-gold-deep); font-weight: 600; }
.tc-title a:focus-visible,
.tc-btn:focus-visible,
.tc-doc:focus-visible,
header a:focus-visible,
.tc-hero a:focus-visible {
  outline: 3px solid rgba(201,155,46,.55);
  outline-offset: 3px;
}

/* Trainer strip */
.tc-profile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  flex-wrap: wrap;
  padding: 28px 30px;
  border: 1px solid var(--tc-line);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(12,35,64,.04), 0 8px 22px rgba(12,35,64,.05);
}
.tc-profile-main { flex: 1 1 560px; }
.tc-profile h2 { margin-bottom: 6px; font-size: 24px; }
.tc-profile p { margin: 0; color: var(--tc-muted); font-size: 14px; line-height: 1.6; }
.tc-profile .tc-btn { flex: none; }

@media (max-width: 760px) {
  .wrapper { padding: 0 18px 40px; }
  .tc-hero { padding: 32px 24px 30px; border-radius: 18px; margin-bottom: 34px; }
  .tc-hero p { font-size: 15.5px; }
  .tc-hero-tags span { font-size: 11.5px; }
  .tc-grid { grid-template-columns: 1fr; }
  .tc-card { padding: 24px 22px 20px; }
  .tc-profile { padding: 24px 22px; gap: 20px; }
  .tc-profile .tc-btn { width: 100%; justify-content: center; }
}

@media (max-width: 480px) {
  header .view { display: none; }
}

@media (prefers-reduced-motion: reduce) {
  .tc-card { transition: none; }
  .tc-card:hover { transform: none; }
}

@media print {
  body { padding: 0; background: #fff; }
  .wrapper { max-width: none; padding: 0; }
  header, footer { display: none; }
  .tc-hero {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .tc-card { break-inside: avoid; box-shadow: none; }
}
</style>

<div class="tc-hero">
  <span class="tc-eyebrow"><span class="tc-dot"></span>AI Training Catalogue</span>
  <h1>Training Outlines</h1>
  <p>Practical, hands-on AI training programmes by <a href="03_Trainer_Profile/CTH-HRDC-Trainer-Profile.html">Ts. Chong Theng Hui</a> — delivered in-house, face-to-face, and HRDC-claimable. Every programme is built around real workplace tasks and a practical takeaway you can use immediately.</p>
  <div class="tc-hero-tags">
    <span>In-house delivery</span>
    <span>Hands-on</span>
    <span>HRDC-claimable</span>
    <span>Tailored to your team</span>
  </div>
</div>

<div class="tc-group">
  <div class="tc-group-head">
    <span class="tc-kicker">Start here</span>
    <h2>AI Tools for Beginners</h2>
    <p>Entry-level, hands-on programmes for everyday users — no technical or design background required.</p>
  </div>
  <div class="tc-grid">

    <article class="tc-card tc-card--gold">
      <div class="tc-card-top">
        <span class="tc-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
        </span>
        <span class="tc-pill">1 Day · 7 Hours</span>
      </div>
      <h3 class="tc-title"><a href="ai_tools_entry_level/chatgpt-for-beginners-training-outline.html">ChatGPT for Beginners</a></h3>
      <p class="tc-subtitle">Practical AI Skills for Everyday Work</p>
      <p class="tc-desc">A beginner-friendly programme covering setup, prompting, everyday workplace tasks, Custom Instructions and responsible use — ending with a personal action plan.</p>
      <div class="tc-tags">
        <span class="tc-tag">ChatGPT</span>
        <span class="tc-tag">6 modules</span>
      </div>
      <div class="tc-card-foot">
        <a class="tc-btn" href="ai_tools_entry_level/chatgpt-for-beginners-training-outline.html" aria-label="View the ChatGPT for Beginners training outline">View outline
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
      </div>
    </article>

    <article class="tc-card tc-card--gold">
      <div class="tc-card-top">
        <span class="tc-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
        </span>
        <span class="tc-pill">1 Day · 7 Hours</span>
      </div>
      <h3 class="tc-title"><a href="ai_tools_entry_level/microsoft-copilot-for-beginners-training-outline.html">Microsoft Copilot for Beginners</a></h3>
      <p class="tc-subtitle">Your AI Assistant Across Microsoft 365</p>
      <p class="tc-desc">A beginner-friendly programme covering Copilot chat across web and mobile, AI-assisted drafting and analysis in Microsoft 365, and meeting preparation.</p>
      <div class="tc-tags">
        <span class="tc-tag">Microsoft 365 Copilot</span>
        <span class="tc-tag">6 modules</span>
      </div>
      <div class="tc-card-foot">
        <a class="tc-btn" href="ai_tools_entry_level/microsoft-copilot-for-beginners-training-outline.html" aria-label="View the Microsoft Copilot for Beginners training outline">View outline
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
      </div>
    </article>

    <article class="tc-card tc-card--gold">
      <div class="tc-card-top">
        <span class="tc-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
        </span>
        <span class="tc-pill">1 Day · 7 Hours</span>
      </div>
      <h3 class="tc-title"><a href="ai_tools_entry_level/canva-for-beginners-training-outline.html">Canva for Beginners</a></h3>
      <p class="tc-subtitle">Everyday Design &amp; AI with Magic Studio</p>
      <p class="tc-desc">A beginner-friendly programme covering Canva design basics, workplace visuals, Magic Studio AI tools and a personal action plan — no design background needed.</p>
      <div class="tc-tags">
        <span class="tc-tag">Canva + Magic Studio</span>
        <span class="tc-tag">6 modules</span>
      </div>
      <div class="tc-card-foot">
        <a class="tc-btn" href="ai_tools_entry_level/canva-for-beginners-training-outline.html" aria-label="View the Canva for Beginners training outline">View outline
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
      </div>
    </article>

  </div>
</div>

<div class="tc-group">
  <div class="tc-group-head">
    <span class="tc-kicker">Productivity &amp; data</span>
    <h2>For Office &amp; Data Teams</h2>
    <p>Programmes that blend everyday AI productivity with the data literacy teams need to measure what matters.</p>
  </div>
  <div class="tc-grid">

    <article class="tc-card tc-card--green">
      <div class="tc-card-top">
        <span class="tc-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
        </span>
        <span class="tc-pill">1.5 Days · 11 Hours</span>
      </div>
      <h3 class="tc-title"><a href="ai_office_productivity/ai-for-office-productivity-training-outline.html">AI for Office Productivity</a></h3>
      <p class="tc-subtitle">Work Smarter with ChatGPT, Gemini Notebook &amp; Personal AI Agents</p>
      <p class="tc-desc">An interactive programme taking office professionals from prompt fundamentals and ChatGPT personalisation to Gemini Notebook research — capped by a personal AI agent build.</p>
      <div class="tc-tags">
        <span class="tc-tag">ChatGPT</span>
        <span class="tc-tag">Gemini Notebook</span>
        <span class="tc-tag">12 modules</span>
      </div>
      <div class="tc-card-foot">
        <a class="tc-btn" href="ai_office_productivity/ai-for-office-productivity-training-outline.html" aria-label="View the AI for Office Productivity training outline">View outline
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
      </div>
    </article>

    <article class="tc-card tc-card--green">
      <div class="tc-card-top">
        <span class="tc-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="20" x2="6" y2="16"/><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/></svg>
        </span>
        <span class="tc-pill">1 Day · 7 Hours</span>
      </div>
      <h3 class="tc-title"><a href="ai_productivity_healthcare/digital-productivity-data-awareness-training-outline.html">Digital Productivity &amp; Data Awareness</a></h3>
      <p class="tc-subtitle">Working Smarter with Microsoft 365, Copilot &amp; Gemini Notebook</p>
      <p class="tc-desc">A practical programme combining Microsoft 365 and Copilot productivity with KPI fundamentals, dashboard interpretation and a workplace improvement project.</p>
      <div class="tc-tags">
        <span class="tc-tag">Microsoft 365</span>
        <span class="tc-tag">Copilot</span>
        <span class="tc-tag">7 sessions</span>
      </div>
      <div class="tc-card-foot">
        <a class="tc-btn" href="ai_productivity_healthcare/digital-productivity-data-awareness-training-outline.html" aria-label="View the Digital Productivity and Data Awareness training outline">View outline
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
        <a class="tc-doc" href="ai_productivity_healthcare/M8%20-%20DIGITAL%20PRODUCTIVITY%20%26%20DATA%20AWARENESS%20%281%20DAY%29.docx" aria-label="Download the Digital Productivity and Data Awareness outline as DOCX">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          DOCX
        </a>
      </div>
    </article>

  </div>
</div>

<div class="tc-group">
  <div class="tc-group-head">
    <span class="tc-kicker">Technical teams</span>
    <h2>For IT Teams</h2>
    <p>Hands-on programmes that put AI coding assistants to work across real development workflows.</p>
  </div>
  <div class="tc-grid">

    <article class="tc-card tc-card--blue">
      <div class="tc-card-top">
        <span class="tc-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </span>
        <span class="tc-pill">1 Day · 7 Hours</span>
      </div>
      <h3 class="tc-title"><a href="ai_dev/ai-coding-assistants-training-outline.html">AI Coding Assistants</a></h3>
      <p class="tc-subtitle">Accelerating Software Development with AI Coding Assistants</p>
      <p class="tc-desc">A tool-agnostic programme for developers in any language or framework — code generation, refactoring, documentation and debugging with Claude Code, Codex and GitHub Copilot.</p>
      <div class="tc-tags">
        <span class="tc-tag">Claude Code</span>
        <span class="tc-tag">Codex</span>
        <span class="tc-tag">GitHub Copilot</span>
        <span class="tc-tag">6 modules</span>
      </div>
      <div class="tc-card-foot">
        <a class="tc-btn" href="ai_dev/ai-coding-assistants-training-outline.html" aria-label="View the AI Coding Assistants training outline">View outline
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
        <a class="tc-doc" href="ai_dev/ai-coding-assistants-training-outline.docx" aria-label="Download the AI Coding Assistants outline as DOCX">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          DOCX
        </a>
      </div>
    </article>

    <article class="tc-card tc-card--blue">
      <div class="tc-card-top">
        <span class="tc-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
        </span>
        <span class="tc-pill">1 Day · 7 Hours</span>
      </div>
      <h3 class="tc-title"><a href="ai_dev/ai-based-development-training-outline.html">.NET Core Development with Claude Code</a></h3>
      <p class="tc-subtitle">Accelerating .NET Core Development with Claude Code</p>
      <p class="tc-desc">A focused programme for .NET Core teams — install and configure Claude Code, manage context, scaffold and refactor code, generate documentation and debug issues.</p>
      <div class="tc-tags">
        <span class="tc-tag">Claude Code</span>
        <span class="tc-tag">.NET Core</span>
        <span class="tc-tag">6 modules</span>
      </div>
      <div class="tc-card-foot">
        <a class="tc-btn" href="ai_dev/ai-based-development-training-outline.html" aria-label="View the .NET Core Development with Claude Code training outline">View outline
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>
      </div>
    </article>

  </div>
</div>

<div class="tc-profile">
  <div class="tc-profile-main">
    <span class="tc-kicker">Your trainer</span>
    <h2>Ts. Chong Theng Hui</h2>
    <p>HRDC Accredited Trainer (TTT/22718) · Chief Technology &amp; AI Officer · 20+ years in data, product and AI innovation.</p>
  </div>
  <a class="tc-btn" href="03_Trainer_Profile/CTH-HRDC-Trainer-Profile.html" aria-label="View the trainer profile for Ts. Chong Theng Hui">View trainer profile
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
  </a>
</div>
