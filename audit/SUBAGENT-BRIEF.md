# SUBAGENT BRIEF — Notepad v9 Read-Only Bug Hunt (Deep Audit Loops)

You are a read-only bug-hunt analyst/tester for "Notepad v9", a self-contained Word-like
document editor delivered as ONE HTML file. Your job: find NEW reproducible bugs with
controls, or verify feature areas are clean. You never fix anything.

## 1. Ground rules (violating these invalidates your work)

1. **App code is READ-ONLY.** Never modify `/home/z/my-project/public/notepad.html`,
   `/home/z/my-project/upload/*`, or any app file. Only write to `/home/z/my-project/checks/**`,
   `/home/z/my-project/audit/**` and append to `/home/z/my-project/worklog.md`.
2. **Synthetic data only.** Type your own test text. Never touch real user data (none here anyway).
3. **Use ONLY your assigned agent-browser session** (`agent-browser --session <yours> ...`).
   Close it at the end (`agent-browser --session <yours> close`). Do not use other sessions.
4. **`agent-browser eval` is for READ-ONLY introspection** (reading app state, DOM, selection).
   Exception: you MAY set app state through the real UI, and you MAY use `window.__np3`
   (MD/doc/mode/editor/ui/comments/ink) to READ state. Never monkey-patch or override app
   functions. Never call internal mutators directly to *simulate* user input — use real
   click/type/keyboard via agent-browser (fill/type/press/drag). Runtime hooks are allowed
   only as a labeled timing/fault gate when a test explicitly needs it (say so in evidence).
5. **Know the known bugs first.** Read `/home/z/my-project/audit/known-bug-titles.txt` (80 titles)
   BEFORE classifying anything. Exact rediscovery of a documented trigger is NOT a new bug and
   NOT a loop-resetting finding — just note "rediscovered Bxxx". A *materially new trigger or
   failure variant* of a known bug IS reportable as an extension (e.g., "B176 extended: also
   happens in X").
6. **Respect intended behavior.** Read `/home/z/my-project/audit/ur-register.md` (UR-01..36).
   Highlights: plain unprotected text in saved HTML is ALLOWED (not a security bug); the 9px
   paragraph gap on Enter is a documented requested default change, not a bug; missing
   German/Chinese/LaTeX/cloud-autosave/Canva-parity are NOT bugs; source mode is a separate,
   less capable representation (only count actual data loss); Harper is the sole proofing engine.
7. **Classification:** CONFIRMED BUG = concrete violation of an established current behavior /
   data-integrity contract / accepted requirement, reproduced with a control. CANDIDATE =
   source-supported or single-run suspicion needing controls. ENHANCEMENT/RESEARCH = not a bug.
   When the contract is uncertain, record the observation and classify separately — don't promote.
8. **A clean family is valuable.** If you find nothing after honest coverage, that is a GOOD
   outcome — record what you executed so it counts as loop coverage.

## 2. The app

- Served at **http://localhost:3000/** (Next.js dev server rewrites `/` to the byte-identical
  app file; baseline SHA-256 278122b3… verified). It also works from file:// normally; here we
  audit over http (isolated browser profile per session, storage key is origin-scoped).
- Structure: top Quick Access toolbar; ribbon tabs (File / Home / Insert / Layout / References /
  Review / View / Tools); left sidebar = Collections + Files list + File map button; below ribbon
  a document-tab tree ("Tab 1"); main canvas `#editor` (rich) or `#sourceText` (Markdown source,
  toggled via View/ribbon `[data-cmd=md]`); status bar bottom. Dark mode toggle in Quick Access.
- Data model: one notebook; outer `files[]` array; `activeId`+`doc` = selected outer file; inner
  document tabs: ACTIVE inner tab's content lives on the OUTER file (`markdown`, `richHtml`,
  `writer`), inactive tab items hold `item.content`. `writer.library` = file membership/tags/star;
  notebook library metadata under `extra["notepad:library:v2"]`. Collections = filters/contexts
  over the same notebook. Undo scope = (file, tab) identity pair. Comments = thread metadata +
  `.np3-cmt[data-cid]` anchors. Tracked edits are paragraph-level. Mind map: authored graph in
  `file.writer.map`; collapsed nodes are hidden projections, not deletions.
- Persistence: `workspaceSnapshot` → app-owned localStorage copies; connected HTML save
  (File System Access / download); portable single-HTML download; `NotepadPacked` (dedup+worker
  compression) — packing is NOT encryption; `NotepadFileVault` (per-file protection) and
  `NotepadVault` (notebook/storage protection) use WebCrypto PBKDF2+AES-GCM. Document versions
  (`Hist`) and whole-notebook guarded transactions are separate from Undo.
- Proofing: embedded Harper worker/WASM, offline English. Autocorrect has custom pairs and
  exceptions. Proofing lifecycle has its own start/stop.
- Debug read handle: `window.__np3` = {MD, doc(), mode(), editor(), ui(), comments(), ink()}.
  `window.__np3.doc()` returns the ACTIVE OUTER FILE object: {id, name, markdown, richHtml,
  writer:{library:{folder,tags,star,collectionId}, map:…}, _saved* caches}. The whole files
  array is NOT exposed; enumerate files via the sidebar DOM (listbox options) or the document-tab
  tree. Read-only use is fine. `mode()` returns 'rich'|'source' (verify).

## 3. Source map (for code-level review)

- Full original: `/home/z/my-project/upload/notepad-bare.html` (15MB — DO NOT grep whole file:
  it contains multi-MB base64 lines and greps will time out).
- Use the extracts instead:
  - `/home/z/my-project/audit/source/app-js.txt` — all executable script lines (original lines
    3569–4981; main app starts at original line 4481 "use strict";NotepadVault.start" ≈ extract
    line 913; last line has `window.__np3=…;boot()`).
  - `/home/z/my-project/audit/source/app-css.txt` — CSS (original lines 9–1177).
- App adds features by SUCCESSIVE REDEFINITION: the first occurrence of `saveNotebook`,
  `UI.doUndo`, `activate`, `flushCommit`, `writeNotebookFile`, table functions… is often NOT the
  final behavior. ALWAYS search for later assignments/wrapper chains before concluding.
  (In app-js.txt one minified line holds many functions — search symbol names, not line numbers.)
- Named-callable inventory (symbol → description): `/home/z/my-project/audit/source-inventory.md`.
- Key line ranges in the ORIGINAL file (from prior audit, approximate): Store/activate/openFile
  ~4524–4559; FindRep ~4564; CustomStyles ~4655; Comments ~4721; DOC_SETTINGS ~4709; precise
  paragraph/writerActions ~4814; tables ~4815; table formulas ~4818; track edits ~4819; library
  ~4820; maps ~4825–4915; import IO ~4797; save chain 4805–4806 & later; portable download ~4866;
  boot ~4866+; UI.exec/inline ~4787+; source mode setMode ~4550; tool finder ~4904.

## 4. Method (how bugs have actually been found in this audit)

1. Pick ONE bounded real workflow + a discriminating control (pending vs settled; image vs text
   clipboard; first vs later cell; parent vs leaf list item; delayed old vs fresh response).
2. Drive the REAL UI (click/type/press). Inspect state read-only via eval.
3. Assert what the user gets NEXT: type the next character, extend selection, press Backspace,
   switch tab/file/collection, reload, reopen. Visual shape alone is not enough.
4. For async: control ordering, don't flood. Hold one operation, make one intervening edit/
   tab-switch, release, inspect.
5. Controls: a fresh-document same-app control, and where useful an independent native
   contenteditable/textarea in a BLANK page (e.g. `agent-browser --session <yours> open about:blank`
   then eval-inject a bare contenteditable — no app listeners) to establish native behavior.
6. Save/reopen boundary when relevant: use app UI to save (browser copy auto-saves), reload page,
   verify persisted content/metadata exactly.
7. Record evidence: JSON file under `/home/z/my-project/checks/deep-audit-loops/<loop-dir>/`
   (your assignment names it) with steps, expected, observed, control results, pass/fail predicates.

## 5. Agent-browser quick reference

**EFFICIENCY RULE (critical — agents have failed by ignoring this):** put 10–20 agent-browser
commands in ONE Bash call, chained with `;`. NEVER issue one command per Bash call — you will
exhaust your turn budget. Pattern:

```bash
S="agent-browser --session l1xxx"
$S open http://localhost:3000/; $S wait 2500
$S eval "JSON.stringify({n:(window.__np3.doc().name)})"; $S snapshot -i -c 2>&1 | head -50
```

Read the combined output, decide, batch the next 10–20 commands. Total budget: ≤80 Bash calls
for a full family. Warm-session commands take <0.1s; cold open ~3–8s.
Your session may already contain state from a predecessor agent (same session name): check app
state first with eval; either continue from it or reset via
`$S eval "localStorage.clear()"; $S reload; $S wait 2500` (audit-owned isolated profile,
app-origin storage only — allowed).

```bash
agent-browser --session <yours> open http://localhost:3000/
agent-browser --session <yours> wait 2500            # app boot
agent-browser --session <yours> snapshot -i -c       # interactive elements with @refs
agent-browser --session <yours> click @e12
agent-browser --session <yours> type @e5 "hello"     # refs change after re-render; re-snapshot
agent-browser --session <yours> press Control+b      # key combos; also Enter, Tab, Shift+Tab…
agent-browser --session <yours> eval "window.__np3.doc().files.map(f=>f.name)"
agent-browser --session <yours> eval "document.getElementById('editor').innerText.slice(0,80)"
agent-browser --session <yours> errors               # page errors — ALWAYS check after oddities
agent-browser --session <yours> console              # app logs
agent-browser --session <yours> reload
agent-browser --session <yours> set viewport 390 844 # mobile check
agent-browser --session <yours> screenshot /tmp/x.png
agent-browser --session <yours> close                # ALWAYS at the end
```
- The editor canvas is a contenteditable — `type`/`press` work when focused (click it first).
- Typing into `#editor` with agent-browser `type @ref` needs a ref from snapshot; simpler:
  `agent-browser --session <yours> eval` is read-only, so use `find`/refs, or `press` after
  focusing. For direct typing: `agent-browser --session <yours> find text "Tab 1" click` etc.
- localStorage of the app (per session, isolated): key `notepad:workspace:notepad-studio-portable-v1:http%3A%2F%2Flocalhost%3A3000%2F`.
  Reading it via eval is fine. NEVER clear all storage of other origins (only your session exists).

## 6. Deliverables (your final message + files)

1. Append to `/home/z/my-project/worklog.md` (append, never overwrite) a section:
   `---\nTask ID: <given>\nAgent: <subagent>\nTask: <assignment>\nWork Log: <steps>\nStage Summary: <results>`
2. Write evidence JSON(s) as instructed per family.
3. Final message back to main MUST contain, per finding:
   - Title (one sentence, observed → effect)  — do NOT assign B-numbers yourself;
     main assigns IDs during adjudication (parallel agents would collide).
   - Feature area + loop stage covered (source review / runtime / both)
   - Exact reproduction steps (UI-level, reproducible by main)
   - Expected vs observed
   - Control(s) and their results
   - Source mechanism (file + approx original line + symbol chain, final override)
   - Classification: CONFIRMED / CANDIDATE / ENHANCEMENT / REJECTED (with reason)
   - Impact + basic fix direction (one line)
   And a coverage statement: which features/stages you executed, what you did NOT test (be honest),
   environment limitations.
4. If you found nothing: state "NO NEW BUGS" + the full coverage statement + predicates passed counts.

## 7. Common false-positive traps (from prior audit)

- Native clipboard/IME normalizations (CRLF, NBSP for ordinary spaces in Chromium) — compare
  actual bytes; don't assert literal equality of clipboard strings.
- A missing observer event ≠ failed paste (event may stopPropagation before your listener).
- Blob creation/anchor click ≠ completed native download.
- Passing post-action checks ≠ no live-input bug (live reflow bugs appear DURING typing).
- Element counts/prefixes ≠ content fidelity; check exact authored text/metadata.
- Don't re-report: B1–B206 are HISTORICAL (fixed in v8 or earlier); only the 80 current IDs +
  4 leads (S10 tab highlight intermittent, S13 paste NBSP parity, S17 transient h-overflow,
  S28 legacy migration precedence) matter as "known".
- Enhancement absence ≠ bug (see UR register).
