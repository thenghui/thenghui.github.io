#!/usr/bin/env bash
# shellcheck shell=bash
#
# reveal_batch.sh — batch runner for the th-job-ad-employer-reveal skill.
#
# Takes a list of recruitment-agency job ads (URLs and/or saved ad-text files), runs
# one headless GitHub Copilot CLI agent per ad to execute the th-job-ad-employer-reveal
# workflow (real employer + PIC + contact details via cross-platform ad fingerprinting),
# and aggregates the per-ad verdicts into summary.md / summary.csv.
#
# macOS-friendly: bash 3.2 compatible, stock tools only + the copilot CLI.
# python3 (or jq) is used for JSON validation and the final summary.
#
set -u

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT="./ads.txt"
OUT_DIR="./reveal-out"
MODEL=""
TIMEOUT=1800
JOBS=1
BATCH=0
DRY_RUN=0
FORCE=0
NO_SUMMARY=0
NO_REPAIR=0
CHECK_ONLY=0

usage() {
  cat <<'EOF'
reveal_batch.sh — batch runner for the th-job-ad-employer-reveal skill

Feeds a list of recruitment-agency job ads to GitHub Copilot CLI (headless, one agent
run per ad) and aggregates per-ad verdicts: real employer (ranked), PICs and their
contact details (email / phone / mobile), evidence links, ruled-out candidates.

USAGE
  reveal_batch.sh -i ads.txt [-o reveal-out] [options]

INPUT FILE (default ./ads.txt; one ad per line)
  Blank lines and lines starting with # are ignored. Supported line formats:
    https://my.jobstreet.com/job/12345678
    https://www.linkedin.com/jobs/view/4123456789 | Randstad ad, KL finance role
    /Users/you/Downloads/pasted-ad.txt          (saved ad text file)
    Senior Accountant Data Center Penang        (free text / search hint)
  Anything after | is a note handed to the agent.

OPTIONS
  -i, --input FILE     ads list (default: ./ads.txt)
  -o, --out DIR        output root (default: ./reveal-out)
  -m, --model MODEL    model for the agent runs (default: your CLI default)
  -j, --jobs N         ads processed in parallel waves of N (default: 1)
  -t, --timeout SECS   per-ad time limit, 0 = no limit (default: 1800)
      --batch          one single copilot run for the whole list (adds --fleet)
      --force          re-run ads that already have a result.json
      --no-repair      skip the JSON-repair pass when a run misses result.json
      --no-summary     skip summary.md / summary.csv generation
      --dry-run        print what would run, run nothing
      --check          verify prerequisites and exit
  -h, --help           this help

OUTPUT (per ad)  <out>/<NNNN>-<slug>/{ad.md, report.md, result.json, prompt.md, agent.log, session.md}
OUTPUT (batch)   <out>/summary.md, <out>/summary.csv, <out>/run.log

Requires: copilot CLI (logged in). python3 or jq recommended for summary/validation.
ENV
  REVEAL_EXTRA_COPILOT_FLAGS='--model gpt-5'   extra flags appended to every copilot call
EOF
}

log() {
  printf '%s [reveal] %s\n' "$(date '+%H:%M:%S')" "$*" | tee -a "$OUT_DIR/run.log" >&2
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

valid_json() { # $1 = file
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$1" >/dev/null 2>&1
  elif command -v jq >/dev/null 2>&1; then
    jq empty "$1" >/dev/null 2>&1
  else
    [ -s "$1" ]
  fi
}

have_python() { command -v python3 >/dev/null 2>&1; }

# Portable per-ad timeout (macOS has no `timeout` by default).
timeout_run() { # $1 = seconds (0 = none); rest = command
  local secs="$1"; shift
  if [ "$secs" -le 0 ]; then
    "$@"
    return $?
  fi
  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"; return $?
  fi
  if command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"; return $?
  fi
  "$@" &
  local p=$!
  (
    sleep "$secs"
    kill "$p" 2>/dev/null
  ) >/dev/null 2>&1 &
  local w=$!
  wait "$p"
  local rc=$?
  kill "$w" 2>/dev/null
  wait "$w" 2>/dev/null
  return $rc
}

JSON_SCHEMA='{
  "source_url": "string or null",
  "ad_title": "string or null",
  "agency": "string or null",
  "captured_at": "ISO-8601 string",
  "verdict_ranked": [
    {"rank": 1, "company": "string", "probability": "high|medium|low", "confidence": 0-10,
     "anchors": ["verbatim anchor 1", "..."], "evidence_urls": ["https://..."]}
  ],
  "people": [
    {"side": "agency|client", "company": "string", "name": "string", "role": "string or null",
     "email": "string or null", "phone": "string or null", "mobile": "string or null",
     "linkedin": "string or null", "contact_status": "verified|publicly_listed|inferred",
     "source_url": "string or null"}
  ],
  "ruled_out": [{"company": "string", "why": "string"}],
  "caveats": ["string"]
}'

build_prompt() { # $1=idx $2=dir $3=source-line $4=note $5=total
  local idx="$1" dir="$2" source_line="$3" note="$4" total="$5"
  local note_line=""
  [ -n "$note" ] && note_line=" note: $note"
  cat <<EOF
You are running the th-job-ad-employer-reveal skill headlessly (non-interactive mode).

GOAL
De-anonymise the recruitment-agency job ad below:
 1) identify the REAL HIRING COMPANY as a ranked verdict (>=2 independent anchors), and
 2) find the PICs and their contact details — agency consultant + client-side hiring
    contacts (email, phone, mobile) — from PUBLIC sources only.

SKILL FILES — read these first and follow their workflow exactly:
 $SKILL_DIR/SKILL.md
 $SKILL_DIR/references/platform-playbook.md

JOB AD ($idx of $total)
 source: $source_line$note_line

WORK DIRECTORY — write ALL outputs here, using absolute paths. Touch nothing else.
 Paths may contain spaces (e.g. iCloud folders): always quote them in shell commands.
 $dir

WORKFLOW (per the skill)
 1. Capture the ad VERBATIM (plain fetch first; use a browser MCP when available for
    Cloudflare-protected boards such as JobStreet / Jooble / Indeed viewjob; otherwise use
    curl with a browser-like User-Agent and note blocks). If the source is a local file, read it.
 2. Extract fingerprints: about-the-company blurb, unique sentences, closing apply line,
    buzzword stack, salary band, reference number, consultant name/phone, posted/closing dates.
 3. Exact-phrase hunt: search the most distinctive fragments IN QUOTES (DuckDuckGo in a real
    browser preferred; use the web_search tool for discovery, then verify every cited page
    yourself). Also try title + candidate company, and site:linkedin.com/jobs variants.
 4. Platform sweep (playbook recipes): client careers portal (Workday tenants), JobStreet/SEEK,
    LinkedIn jobs, Indeed, ACCA Careers / eFinancialCareers, aggregators (Jooble, JobLeads,
    Expertini, Talent.com, Careerjet, foundit, Maukerja). A near-verbatim matched sentence is
    strong; a matched closing line or about-company blurb is near-conclusive. Timing proximity
    ("Posted 2 days ago") is an extra anchor.
 5. People hunt:
    - agency side: the consultant named / phone number on the ad (search the digits, then
      name + agency on LinkedIn);
    - client side: site:linkedin.com/in "<company>" <finance|HR|talent acquisition> <city>,
      press releases (CEO / country GM), careers-page "Introduce Yourself" contacts.
    CONTACT RULES: public sources only; never bypass logins or paywalls; mark every contact as
    verified (seen on a public page, cite URL) | publicly_listed (role mailbox) | inferred
    (state the pattern, e.g. name@company.com). Never fabricate a name, number or email.

OUTPUT FILES (write all three)
 - $dir/ad.md      verbatim ad text + metadata (source URL, title, agency, salary, reference
                   number, consultant + phone, posted/closing dates, captured-at timestamp).
 - $dir/report.md  ranked report with these sections:
      1) VERDICT — real employer, probability (high/medium/low), confidence x/10, plus a
         quote-comparison table: agency ad fragment | matched client-posting fragment | source URL.
      2) EVIDENCE ADS — ranked list: platform | title | URL | match score x/10 | what matched.
      3) PEOPLE — agency consultant and client-side PIC(s): name, role, company, email, phone,
         mobile, LinkedIn, contact_status, source URL.
      4) RULED OUT — near-miss employers, one-line reason each.
      5) CAVEATS — what could not be verified.
 - $dir/result.json : STRICT JSON (no markdown fences), matching this schema:
$JSON_SCHEMA

Use null for anything unknown. Do not invent data. Then print exactly one final line:
REVEAL_DONE <top-company-or-UNKNOWN>
EOF
}

build_batch_prompt() { # $1 = file with "idx<TAB>dir<TAB>source<TAB>note" rows, $2 = total
  local list="$1" total="$2"
  local ads_block
  ads_block="$(awk -F'\t' '{printf " %s. source: %s%s\n    work dir: %s\n", $1, $3, ($4 == "" ? "" : "  (note: " $4 ")"), $2}' "$list")"
  cat <<EOF
You are running the th-job-ad-employer-reveal skill headlessly (non-interactive mode), in
fleet mode: process ALL $total job ads below, one per work directory.

GOAL (per ad)
De-anonymise the recruitment-agency job ad: (1) identify the REAL HIRING COMPANY as a ranked
verdict (>=2 independent anchors), and (2) find the PICs and their contact details — agency
consultant + client-side hiring contacts (email, phone, mobile) — from PUBLIC sources only.

SKILL FILES — read these first and follow their workflow exactly:
 $SKILL_DIR/SKILL.md
 $SKILL_DIR/references/platform-playbook.md

JOB ADS ($total total)
$ads_block

WORKFLOW (per ad, per the skill)
 1. Capture the ad VERBATIM into <work dir>/ad.md (plain fetch first; browser MCP for
    Cloudflare-protected boards; curl with a browser-like User-Agent otherwise).
 2. Extract fingerprints (about-the-company blurb, unique sentences, closing apply line,
    buzzword stack, salary band, reference number, consultant name/phone, dates).
 3. Exact-phrase hunt with quoted fragments; verify every candidate page yourself.
 4. Platform sweep per the playbook (Workday careers portals, JobStreet/SEEK, LinkedIn, Indeed,
    ACCA Careers, aggregators). Near-verbatim sentence = strong; matched closing line or
    about-company blurb = near-conclusive.
 5. People hunt: agency consultant (from the ad) + client-side finance/HR contacts.
    Public sources only; mark contacts verified | publicly_listed | inferred (state pattern);
    never fabricate.

OUTPUTS (for every ad, in its work directory)
 - <work dir>/ad.md      verbatim ad + metadata.
 - <work dir>/report.md  ranked report: VERDICT (+quote-comparison table) / EVIDENCE ADS /
                         PEOPLE (with contacts + status) / RULED OUT / CAVEATS.
 - <work dir>/result.json STRICT JSON (no markdown fences), schema:
$JSON_SCHEMA

Use null for unknown values. Do not invent data. Finish with one line per ad:
REVEAL_DONE <idx> <top-company-or-UNKNOWN>
EOF
}

repair_run() { # $1 = dir ; $2 = idx
  local dir="$1" idx="$2"
  local prompt
  prompt="A previous headless run of th-job-ad-employer-reveal (ad $idx) did not leave a valid result.json in $dir.
Read whatever is there (ad.md, report.md, agent.log, session.md) and write $dir/result.json as STRICT JSON matching this schema:
$JSON_SCHEMA
If the run genuinely produced nothing, still write result.json with verdict_ranked: [], people: [], ruled_out: [], caveats: [\"run produced no usable output; see agent.log\"], source_url: null, ad_title: null, agency: null, captured_at: \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\". Do not invent findings. Reply with exactly: RESULT_REPAIRED"
  copilot -p "$prompt" -s --allow-all >>"$dir/agent.log" 2>&1
}

run_one() { # $1=idx $2=dir $3=source-line $4=note $5=total
  local idx="$1" dir="$2" source="$3" note="$4" total="$5"
  if [ "$FORCE" -eq 0 ] && [ -s "$dir/result.json" ] && valid_json "$dir/result.json"; then
    log "skip $idx (already done: $dir)"
    return 0
  fi
  mkdir -p "$dir"
  # Local ad-text file: copy it into the work dir so the agent always has a stable copy.
  if [ -f "$source" ]; then
    cp "$source" "$dir/source-ad.txt"
    source="local file $source (copied to $dir/source-ad.txt)"
  fi
  local prompt
  prompt="$(build_prompt "$idx" "$dir" "$source" "$note" "$total")"
  printf '%s\n' "$prompt" >"$dir/prompt.md"

  local cmd=(copilot -p "$prompt" -s --allow-all --share "$dir/session.md" --name "reveal-$idx")
  [ -n "$MODEL" ] && cmd+=(-m "$MODEL")
  if [ -n "${REVEAL_EXTRA_COPILOT_FLAGS:-}" ]; then
    # shellcheck disable=SC2206
    cmd+=($REVEAL_EXTRA_COPILOT_FLAGS)
  fi

  log "start $idx -> $dir"
  timeout_run "$TIMEOUT" "${cmd[@]}" >"$dir/agent.log" 2>&1
  local rc=$?

  if ! { [ -s "$dir/result.json" ] && valid_json "$dir/result.json"; }; then
    if [ "$NO_REPAIR" -eq 0 ] && [ -f "$dir/agent.log" ]; then
      log "repair $idx (no valid result.json)"
      repair_run "$dir" "$idx" || true
    fi
  fi

  if [ -s "$dir/result.json" ] && valid_json "$dir/result.json"; then
    log "ok    $idx (agent rc=$rc) -> $dir"
    return 0
  fi
  log "FAIL  $idx (agent rc=$rc) — see $dir/agent.log"
  return 1
}

generate_summary() {
  if ! have_python; then
    log "python3 not found — skipping summary; per-ad results are in $OUT_DIR"
    return 0
  fi
  python3 - "$OUT_DIR" <<'PY'
import csv
import glob
import json
import os
import sys
from datetime import datetime

out = os.path.abspath(sys.argv[1])
rows = []

for d in sorted(glob.glob(os.path.join(out, '[0-9][0-9][0-9][0-9]-*'))):
    if not os.path.isdir(d):
        continue
    base = os.path.basename(d)
    rec = {
        'index': base.split('-')[0],
        'run_dir': base,
        'status': 'FAILED',
        'source_url': '', 'ad_title': '', 'agency': '',
        'top_company': '', 'probability': '', 'confidence': '', 'evidence': '',
        'client_pic': '', 'client_role': '', 'client_email': '', 'client_phone': '',
        'client_mobile': '', 'client_status': '', 'agency_pic': '', 'agency_phone': '',
        'agency_email': '', 'report': os.path.join(base, 'report.md'),
    }
    rp = os.path.join(d, 'result.json')
    if os.path.exists(rp):
        data = None
        try:
            with open(rp, encoding='utf-8') as f:
                data = json.load(f)
            rec['status'] = 'OK'
        except Exception:
            rec['status'] = 'BAD_JSON'
        if isinstance(data, dict):
            rec['source_url'] = data.get('source_url') or ''
            rec['ad_title'] = data.get('ad_title') or ''
            rec['agency'] = data.get('agency') or ''
            verdicts = [v for v in (data.get('verdict_ranked') or []) if isinstance(v, dict)]
            verdicts.sort(key=lambda v: v.get('rank') if isinstance(v.get('rank'), (int, float)) else 99)
            top = verdicts[0] if verdicts else {}
            rec['top_company'] = top.get('company') or ''
            rec['probability'] = top.get('probability') or ''
            conf = top.get('confidence')
            rec['confidence'] = '' if conf is None else str(conf)
            rec['evidence'] = ' | '.join([u for u in (top.get('evidence_urls') or []) if u][:3])
            people = [p for p in (data.get('people') or []) if isinstance(p, dict)]
            clients = [p for p in people if str(p.get('side') or '').lower() == 'client']
            agency_people = [p for p in people if str(p.get('side') or '').lower() != 'client']
            cp = clients[0] if clients else {}
            ap = agency_people[0] if agency_people else {}
            rec['client_pic'] = cp.get('name') or ''
            rec['client_role'] = cp.get('role') or ''
            rec['client_email'] = cp.get('email') or ''
            rec['client_phone'] = cp.get('phone') or ''
            rec['client_mobile'] = cp.get('mobile') or ''
            rec['client_status'] = cp.get('contact_status') or ''
            rec['agency_pic'] = ap.get('name') or ''
            rec['agency_phone'] = ap.get('phone') or ap.get('mobile') or ''
            rec['agency_email'] = ap.get('email') or ''
    rows.append(rec)

ok = [r for r in rows if r['status'] == 'OK']
bad = [r for r in rows if r['status'] != 'OK']


def cell(value):
    return str(value if value is not None else '').replace('|', '\\|').replace('\n', ' ').strip()


md = []
md.append('# Job-Ad Employer Reveal — Batch Summary')
md.append('')
md.append('- Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
md.append('- Output dir: `' + out + '`')
md.append('- Ads: {} — OK: {} / not OK: {}'.format(len(rows), len(ok), len(bad)))
md.append('')
md.append('| # | Ad | Agency | Top employer | Prob | Conf | Client PIC | Email | Phone / Mobile | Agency contact | Report |')
md.append('|---|---|---|---|---|---|---|---|---|---|---|')
for r in rows:
    phone = r['client_phone'] or r['client_mobile']
    agency_contact = ' '.join(x for x in [r['agency_pic'], r['agency_phone']] if x)
    employer = r['top_company'] or ('UNKNOWN' if r['status'] == 'OK' else '')
    md.append('| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | `{}` |'.format(
        cell(r['index']), cell(r['ad_title'] or r['source_url']), cell(r['agency']),
        cell(employer), cell(r['probability']), cell(r['confidence']),
        cell(r['client_pic']), cell(r['client_email']), cell(phone),
        cell(agency_contact), cell(r['report'])))
md.append('')
if bad:
    md.append('## Not OK — inspect these runs')
    md.append('')
    for r in bad:
        md.append('- `{}/` — status {} (see `{}/agent.log`)'.format(r['run_dir'], r['status'], r['run_dir']))
    md.append('')

with open(os.path.join(out, 'summary.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(md) + '\n')

fields = ['index', 'run_dir', 'status', 'ad_title', 'agency', 'source_url', 'top_company',
          'probability', 'confidence', 'evidence', 'client_pic', 'client_role', 'client_email',
          'client_phone', 'client_mobile', 'client_status', 'agency_pic', 'agency_email',
          'agency_phone', 'report']
with open(os.path.join(out, 'summary.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)

print('summary: {} ads (OK {}, not OK {}) -> {}/summary.md, {}/summary.csv'.format(
    len(rows), len(ok), len(bad), out, out))
PY
}

do_check() {
  local rc=0
  echo "reveal_batch.sh v$VERSION — prerequisite check"
  echo "  script : $SCRIPT_DIR/reveal_batch.sh"
  echo "  skill  : $SKILL_DIR"
  echo
  if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "  [ok]   skill file: $SKILL_DIR/SKILL.md"
  else
    echo "  [FAIL] skill file missing: $SKILL_DIR/SKILL.md"; rc=1
  fi
  if [ -f "$SKILL_DIR/references/platform-playbook.md" ]; then
    echo "  [ok]   playbook: $SKILL_DIR/references/platform-playbook.md"
  else
    echo "  [warn] playbook missing: $SKILL_DIR/references/platform-playbook.md"
  fi
  if command -v copilot >/dev/null 2>&1; then
    echo "  [ok]   $(command -v copilot) — $(copilot --version 2>&1 | head -1)"
  else
    echo "  [FAIL] copilot CLI not on PATH (install/login first)"; rc=1
  fi
  if have_python; then
    echo "  [ok]   $(command -v python3) — $(python3 --version 2>&1)"
  elif command -v jq >/dev/null 2>&1; then
    echo "  [warn] python3 not found; jq available but summary generation is skipped"
  else
    echo "  [warn] neither python3 nor jq found — summaries will be skipped"
  fi
  if [ -f "$INPUT" ]; then
    local n
    n="$(grep -c -v -e '^[[:space:]]*$' -e '^[[:space:]]*#' "$INPUT" 2>/dev/null || true)"
    [ -n "$n" ] || n=0
    echo "  [ok]   ads list: $INPUT ($n ad lines)"
  else
    echo "  [info] ads list not found yet: $INPUT (create it, one ad per line)"
  fi
  echo
  [ "$rc" -eq 0 ] && echo "Prerequisites OK." || echo "Prerequisites FAILED."
  return $rc
}

# ---------------------------------------------------------------- argument parsing

while [ $# -gt 0 ]; do
  case "$1" in
    -i|--input) INPUT="${2:-}"; shift 2 ;;
    -o|--out) OUT_DIR="${2:-}"; shift 2 ;;
    -m|--model) MODEL="${2:-}"; shift 2 ;;
    -j|--jobs) JOBS="${2:-1}"; shift 2 ;;
    -t|--timeout) TIMEOUT="${2:-1800}"; shift 2 ;;
    --batch) BATCH=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    --no-summary) NO_SUMMARY=1; shift ;;
    --no-repair) NO_REPAIR=1; shift ;;
    --check) CHECK_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$JOBS" in ''|*[!0-9]*) die "--jobs must be a positive integer" ;; esac
case "$TIMEOUT" in ''|*[!0-9]*) die "--timeout must be an integer (seconds, 0 = none)" ;; esac
[ "$JOBS" -ge 1 ] || die "--jobs must be >= 1"

if [ "$CHECK_ONLY" -eq 1 ]; then
  do_check
  exit $?
fi

[ -f "$INPUT" ] || die "ads list not found: $INPUT (create it, one ad per line; see --help)"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
[ -f "$OUT_DIR/run.log" ] || : >"$OUT_DIR/run.log"

LIST="$OUT_DIR/ads.resolved.tsv"
: >"$LIST"

i=0
while IFS= read -r raw || [ -n "$raw" ]; do
  line="$(printf '%s' "$raw" | sed -e 's/[[:space:]]*$//' -e 's/^[[:space:]]*//')"
  [ -z "$line" ] && continue
  case "$line" in \#*) continue ;; esac
  main="$line"
  note=""
  case "$line" in
    *\|*)
      main="${line%%|*}"
      note="${line#*|}"
      main="$(printf '%s' "$main" | sed -e 's/[[:space:]]*$//' -e 's/^[[:space:]]*//')"
      note="$(printf '%s' "$note" | sed -e 's/[[:space:]]*$//' -e 's/^[[:space:]]*//')"
      ;;
  esac
  [ -z "$main" ] && continue
  slug="$(printf '%s' "$main" | sed -e 's|^https://||' -e 's|^http://||' -e 's|[^A-Za-z0-9._-]|_|g' | cut -c1-70)"
  [ -z "$slug" ] && slug="ad"
  i=$((i + 1))
  idx="$(printf '%04d' "$i")"
  printf '%s\t%s\t%s\t%s\n' "$idx" "$OUT_DIR/$idx-$slug" "$main" "$note" >>"$LIST"
done <"$INPUT"

TOTAL="$i"
[ "$TOTAL" -ge 1 ] || die "no ads found in $INPUT"

log "ads: $TOTAL — out: $OUT_DIR — jobs: $JOBS — timeout: ${TIMEOUT}s${MODEL:+ — model: $MODEL}"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY RUN — nothing executed. Plan:"
  printf '%s\n' "  input : $INPUT"
  printf '%s\n' "  out   : $OUT_DIR"
  while IFS=$'\t' read -r idx dir main note <&3; do
    printf '  [%s] %s\n        dir: %s\n' "$idx" "$main" "$dir"
  done 3<"$LIST"
  printf '\n  per ad would run:\n    copilot -p <skill prompt> -s --allow-all --share <dir>/session.md --name reveal-<idx>%s\n' "${MODEL:+ -m $MODEL}"
  exit 0
fi

# ---------------------------------------------------------------- run

if [ "$BATCH" -eq 1 ]; then
  prompt="$(build_batch_prompt "$LIST" "$TOTAL")"
  printf '%s\n' "$prompt" >"$OUT_DIR/batch-prompt.md"
  cmd=(copilot -p "$prompt" -s --allow-all --fleet --share "$OUT_DIR/session.md" --name "reveal-batch")
  [ -n "$MODEL" ] && cmd+=(-m "$MODEL")
  log "batch run (fleet) — $TOTAL ads"
  timeout_run "$TIMEOUT" "${cmd[@]}" >"$OUT_DIR/batch-agent.log" 2>&1 || log "batch run finished with non-zero status (see $OUT_DIR/batch-agent.log)"
  awk -F'\t' '{print $2}' "$LIST" | while IFS= read -r d; do
    [ -d "$d" ] || mkdir -p "$d"
  done
else
  n=0
  while IFS=$'\t' read -r idx dir main note <&3; do
    run_one "$idx" "$dir" "$main" "$note" "$TOTAL" </dev/null 3<&- &
    n=$((n + 1))
    if [ "$n" -ge "$JOBS" ]; then
      wait
      n=0
    fi
  done 3<"$LIST"
  wait
fi

if [ "$NO_SUMMARY" -eq 0 ]; then
  generate_summary | tee -a "$OUT_DIR/run.log"
fi

ok_count=0
bad_count=0
while IFS=$'\t' read -r idx dir main note <&3; do
  if [ -s "$dir/result.json" ] && valid_json "$dir/result.json"; then
    ok_count=$((ok_count + 1))
  else
    bad_count=$((bad_count + 1))
  fi
done 3<"$LIST"

log "done — ok: $ok_count / $TOTAL, not ok: $bad_count"
if [ "$NO_SUMMARY" -eq 0 ] && [ -f "$OUT_DIR/summary.md" ]; then
  echo
  cat "$OUT_DIR/summary.md"
  echo
  echo "Per-ad details: $OUT_DIR/<NNNN>-<slug>/report.md   Aggregated: $OUT_DIR/summary.csv"
fi

[ "$bad_count" -eq 0 ]
