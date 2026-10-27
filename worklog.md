# Worklog — Notepad v9 Bug Hunt (continuation session)

---
Task ID: 0
Agent: main
Task: Environment reconstruction — serve audited v9 app, verify baseline, smoke test

Work Log:
- Read uploaded audit docs: BUG-HUNT-REPORT.md (355KB), BUG-HUNT-TODO.md (208KB), APP-FUNCTIONS.md (245KB); extracted resumption status, stopping rule (2 consecutive clean full loops), UR-01..36 register, 26-Oct evidence ledger.
- Environment is fresh: no checks/ state, no sites/notepad-studio website source. Only notepad-bare.html available (uploaded).
- Verified SHA-256 of upload/notepad-bare.html = 278122b3849866875436693afe638503e25e5dd7d3f2c0ca3d39da675ce66218 — matches the audited blankSHA256 baseline exactly. App is unchanged v9 release.
- Copied app to public/notepad.html (byte-identical) and added beforeFiles rewrite `/` → `/notepad.html` in next.config.ts so the app is user-visible at the root route.
- Dev server restarted clean; agent-browser smoke test: app renders full Word-like UI (ribbon, sidebar, collections, document tabs), no console/page errors. window.__np3 debug handle available (MD/doc/mode/editor/ui/comments/ink).
- Extracted app code for analysis: audit/source/app-js.txt (lines 3569-4981, 3.0MB incl. resource blocks), audit/source/app-css.txt (lines 9-1177).
- Extracted 80 current confirmed bug IDs+titles → audit/known-bug-titles.txt (76 v9 IDs B207-B288 + reopened B18/B135/B146/B176).
- Extracted UR register → audit/ur-register.md; source inventory → audit/source-inventory.md.

Stage Summary:
- App baseline verified unchanged; app served at http://localhost:3000/ (also visible to user in preview panel).
- Known state: 80 confirmed bugs, 4 unresolved leads (S10/S13/S17/S28), loop 1 was 34.3% complete (12/70 features) in prior environment; 0 complete loops, 0/2 consecutive clean.
- User's current instruction supersedes UR-04 serial-browser constraint: multiple testing browsers + subagents now allowed. App code stays read-only.
- Website functions (sites/notepad-studio) unavailable in this environment — recorded as environment limitation; app-side connected-save code still auditable.
- Next: launch loop-1 completion subagent batches (mind maps, library/collections, layout first — the named remaining areas).

---
Task ID: L1-B
Agent: audit subagent (library/collections/folders/file management + notebook search)
Task: Deep audit of F01 documents, F03 folders/tags/starred, F04 collections, F05 sidebar row state/bulk, F65 notebook-wide search, persistence boundary; hunt new triggers in B280/B281 family.
Work Log: Salvaged warm session l1lib (predecessor state: 4 files, 2 collections); cleared storage (beforeunload flush defeated first attempt; second clear+reload achieved baseline) and rebuilt fixtures through real UI. Source review via rg over audit/source/app-js.txt for noteMeta/saveLibrary/commitLibrary/folderDialog/ensureCollections/collectionFiles/setCollectionContext/switchCollection/createCollection/renameCollection/moveFilesToCollection/removeFolder83/refreshSidebarDocument/syncWriterPage/openNotebookSearch83/indexedNotebookText83/documentContentTabs/documentTab tree + bulk action handlers. Runtime: created docs via sidebar New and File backstage New; commit-on-switch; duplicate (writer deep-copy); renames via row-menu dialog and title field with footer {title} fixture; deletes (single/tabbbed/folder-member); folders create/rename/nest/move/remove-with-files; collections create/drag-move/rename/delete-with-files; pending edits across collection switches; Find-all search (text/name/tab/cross-collection/no-match/clear/pending); checkbox bulk move; full persistence reload diff (python equality ALL_MATCH=True).
Stage Summary: 2 findings. (1) CONFIRMED new bug: title-field rename updates the sidebar row's visible label but not its aria-label — stale accessible name until next full sidebar render; route control (row-menu rename updates both) isolates the miss; mechanism: final refreshSidebarDocument override drops the setAttribute('aria-label') present in the earlier definition (app-js.txt successive-redefinition regression). (2) B280 extension: title-field rename also leaves {title} header/footer placeholders stale (known trigger was sidebar Rename; same syncWriterPage gap, control: any content re-render refreshes it). Everything else passed with controls: commit-on-switch, duplicate identity, delete routes incl. tabs/folder-member, folder lifecycle incl. nesting + removal contract, collection lifecycle incl. pending-edit round trips and per-collection activeId memory, drag-to-collection, bulk move, notebook search incl. tab-targeted navigation and Find anchoring (CSS highlight 1/1), persistence exact-match across reload. Tags/star have no UI (fields exist in model only) — not testable, enhancement territory. Not covered: mind-map search navigation, B281 timing race, bulk-delete runtime, locked-file search exclusion, S10 (never reproduced). Evidence: checks/deep-audit-loops/loop-1/L1B-library-result.json (predicates 46 pass / 2 fail).

---
Task ID: L1-C
Agent: audit subagent (layout variants: F34 page size/orientation/margins/columns, F35 page breaks, F36 zoom, F37 headers/footers, F38 watermark/borders/RTL, F39 print)
Task: Layout-variants deep audit with new-trigger hunt around B208/B214/B227/B280; reset session l1layout, real-UI input only.
Work Log: Reset l1layout (cleared storage, deleted leftover 'L1C Doc A'); source review via rg (applyDocSettings, syncPaperDimensions, syncPageFurniture, furnitureText, googleFurnitureForPage, renderPrintPreview, pageBreak overrides, withMutation/flushCommit/normalizeDom, restoreEditorRange/getRange, paperDimensions, DOC_SETTINGS). Runtime on fresh docs: A4→Letter→landscape→narrow→2/3/1 columns with typed content + rect-vs-page geometry each; header/footer tokens {page}/{pages}/{title}/{date} across forced 5 pages, header edit, paper switch with furniture; watermark apply/type/remove; paragraph border box+shading (np3:ba encoded marker, survives reload); RTL dir toggle; File→Print (doc-unchanged hash); page breaks at doc start/end/mid-paragraph/in list/in table/consecutive; zoom 50/100/200/page-width/web-layout typing with caret-in-page checks, ruler, Go-to-page, source-mode zoom round trip; full persistence reload diff + per-document settings comparison; controlled keystroke-after-break experiments (3 repro + 2 controls).
Stage Summary: 3 findings. (1) CONFIRMED new bug: first keystroke(s) after Insert page break land at the PRE-insert caret (before the break / old page) although the app places the visible caret in the new paragraph after the spacer — 3 reproductions (QUOTE/Z/J), controls prove press-input normally honors the live selection (offset-verified) and that the post-insert DOM selection is in the new paragraph; mechanism = bookmark/lastEditorRange input anchor not refreshed after the pageBreak mutation (app-js.txt pageBreak final override + mousedown-preventDefault .pop focus retention). (2) B135-family extension: page break with caret inside a list item is placed after the whole list, not at the caret (closestTopBlock escapes to UL; block.after(pb)). (3) CANDIDATE cosmetic: reload of a doc starting with '<!-- np3:pb -->' renders a phantom empty leading paragraph (render-only, mdLen byte-identical, control doc without leading break clean). Everything else passed with controls: variant-change typing geometry, furniture tokens/all-pages update/settings-change refresh (no new B280 variant), watermark, borders+shading persistence, RTL style, print doc-unchanged, zoom family, persistence + per-doc settings separation. Not covered: RTL caret-typing anchor, print visual fidelity (no in-app preview exists; renderPrintPreview is dead code — #bsPv never created), custom paper dialog, cover page, watermark reload persistence. Mid-session pb-vanish anomaly investigated and attributed to harness caret chaos (not claimed). Evidence: checks/deep-audit-loops/loop-1/L1C-layout-result.json (predicates 47 pass / 2 fail / 1 candidate).

---
Task ID: L1-A
Agent: main (map audit executed directly after two subagent deadline failures)
Task: Deep audit F05 file map / F06 mind-map graph — clipboard/ownership, inline text, edges, collapse, undo, persistence

Work Log:
- Fresh isolated browser session l1map2; clean baseline (1 file, empty storage).
- File map: node select, rename via #writerDialog (prefilled, Apply works, sidebar+map update), node drag → world position persisted to library.map.positions and restored after reload (initial position-loss suspicion DISPROVEN — map open auto-fits view; view-only).
- Mind map (New → Mind map): inline edit via dblclick/✎ button; + Connected node; copy single/pair (fresh uids, edge remapped to new uids); cut+paste; Undo/Redo ordering exact; collapse/expand (authored children retained, projection only, persists); ownership transition with pending draft (switch MAPA↔mindmap, draft flushed and preserved, no DOM leak); Duplicate; + Comment; reload persistence of nodes/text/edges/collapse.
- CONFIRMED NEW BUG: inline edit ended with UNCHANGED text (Escape cancel / blur) orphans the textarea — renderMap() signature-equality check skips card rebuild, editor never removed; orphan stays live-bound (real typing mutated node text and persisted across reload); reproduces for comments too; Enter-with-changed-text control passes. Evidence: checks/deep-audit-loops/loop-1/L1A-map-result.json (31 pass / 1 fail + 3 observations).
- Harness notes: agent-browser mouse/click events do not carry held Shift (verified via diagnostic capture listener); multi-select setup used disclosed synthetic pointerdown; dblclick not synthesizable from double mouse down/up — used ✎ button route.

Stage Summary:
- F05/F06 loop-1 stages complete (inventory/source/runtime/review). One new confirmed bug (ghost editor orphan, mind-map + comments). Copy ID freshness, edge remap, undo ordering, collapse projection, ownership transitions, persistence all clean. Observations: pasted nodes stack at identical coords; collapsed-branch copy is childless (contract question). Next: batch 2 (images/tables, persistence/protection, imports/exports).

---
Task ID: L1-D
Agent: subagent (images + tables fresh agent, session l1img)
Task: Read-only bug hunt — images (F45 insert, F46 toolbar/align/width/alt, F47 free positioning, F48 editing/original) and tables (F50 insert/selection, F51 row/col/merge/split, F52 design/header/banding/AutoFit/sort, F53 Tab navigation, F54 formulas/recalc); persistence + light source pass.
Work Log:
- Reset session (localStorage.clear + reload; predecessor state flushed on unload — built own synthetic fixtures).
- F45: uploaded /tmp/l1d.png via #imgInput -> figure.img-fig[data-align=center][data-w=100%] with img alt from filename; Edit-alt-text dialog set alt "L1D alt text sample" (verified in DOM).
- F46: width buttons 25/50/100/Natural set data-w and rendered px exactly (151/301/603/10 on 603px page); Delete image + Ctrl+Z restores alt/width/align.
- FINDING (CONFIRMED, new): floating image toolbar first two buttons (Align left, Align center) are covered by the document-tabs sidebar at default 1280px viewport — toolbar positioned left:-65px inside #canvasWrap because clamp(tl,8,canvasWrap.clientWidth-tw-8) returns a negative max when toolbar width (825px) exceeds canvas width (768-16); clicks on those buttons land on tab-tree UI; Align right (same y) works; at 1600x900 viewport toolbar clamps to left:131.5px and the first button is clickable (elementFromPoint = button). Mechanism: app-js.txt ~line 962 Images.sync toolbar positioning. B211-family but different trigger/mechanism (desktop clamp inversion).
- F47: free placement drag moves image by exact delta (data-image-x/y); arrow nudge 1px/press; rediscovered B210 (figure outline solid 2px stays at original anchor while img renders offset; also after nudge at 100%). Free round-trip width 100%->50% traced to intentional code (entering free sets 50% when >=95% width) -> REJECTED as bug.
- F50/F51: 3x3 insert (thead+2 rows); typing in first/later cells OK; Insert row below remaps =SUM(B2:B3)->B2:B4 correctly (value follows 15+5+20=40); merge via DISCLOSED synthetic shift-mousedown on cell + real toolbar click -> colSpan 2 + record in doc.writer.tableMerges; split restores cells/attrs and clears record; undo(split) re-merges with record; undo(merge) restores spans; no span corruption.
- F52: header(data-nohdr)/banding(data-band)/AutoFit(data-fit)/repeat-header(data-rh)/shading(data-sh) toggles verified. Sort by text column: rediscovered B283 (=SUM(B2:B3)->=SUM(B3:B2)->#REF!); 3-row sort variant gives same reversed-range outcome; undo restores range+value exactly; no silent-wrong-value variant (remap is per-cell).
- F53: Tab cell-to-cell; last-cell Tab appends row; Shift+Tab backward in-row; Shift+Tab from first header cell exits to preceding paragraph.
- F54: =SUM(B2:B4)=40; editing input (10->15) auto-recalculates on flush; undo after sort clean; merge/split recalculation consistent (25 merged / 40 split). "=SUM(ABOVE)" -> #FORMULA! rejected (dialog documents A1-refs only).
- F48: Image Studio rotate-left re-encodes src; Restore original restored EXACT original bytes (len/tail match); crop flow not covered.
- Persistence: text + 5-row banded/repeat-header table with shaded cell + formula 40 + image (alt l1d, w 100%) round-tripped EXACTLY after autosave + reload.
- Source pass: read insertFigure/makeFigure, Images.sync (toolbar clamp bug), imagePlacement/setImagePlacement (free mode), tableGrid/cellSpan/colAdd/colDel/rowInsert/rowDel, remapTableFormulas (row/col insert remap incl #REF! on delete), calculateTable parser, Tables.mergeCells/splitCell (records), applyCellSelRect/targetCells, sort remap.
- Evidence: /home/z/my-project/checks/deep-audit-loops/loop-1/L1D-imgtable-result.json
Stage Summary: 1 new CONFIRMED bug (image toolbar covered by tabs sidebar at <=~1345px viewports, clamp inversion, desktop — distinct from mobile-only B211); 2 known rediscoveries (B210, B283 — no materially new variants; 3-row sort behaves identically); 2 candidates rejected with source evidence (free-mode 50% default; =SUM(ABOVE)). 41 predicates: 37 pass / 4 fail (2 new, 2 known). Coverage gaps: B221/B222/B245/B249 variants, Image Studio crop/replace, wrap modes, explicit Recalculate menu entry.

---
Task ID: L1-E
Agent: main
Task: Persistence, protection, history audit (F07-F14) — session l1save

Work Log:
- F07 autosave: typed text persisted across reload.
- F12 document versions: Save-a-version rows (timestamped, words/chars); restore via row-click + confirm restores exact text; versions persist across reload; undo-after-restore not offered (dialog-guarded destructive action, observation only).
- F13 notebook history: CONFIRMED NEW BUG — deleting a file scrubs it from EVERY recovery snapshot (scrubDeletedSnapshot filters snapshot.files; reason rewritten to "Before a notebook change"), so the dialog's "Earlier notebook states, including removed files" promise is false and removed files are permanently unrecoverable from notebook history. Guarded capture fires BEFORE the mutation but is scrubbed immediately after (source-verified chain). Controls: dedup behavior correct; delete-dialog no-undo warning honored.
- F11 notebook password full lifecycle: set → reload → unlock screen → wrong password rejected → correct unlocks with exact content; change → old rejected/new works after reload; remove → no lock screen. ALL CLEAN.
- F10 clear browser data: Type-CLEAR confirm; localStorage 2→0 keys; working doc resets to blank — MATCHES the dialog's explicit contract text (advertised destructive scope); not a bug. B264 handle-retention defect remains prior-evidenced.
- F14: delete file → app-owned storage key scrubbed (3→2); scope app-owned.
- F08/F09 (connected save / portable download): env-bounded in headless (no FS Access picker / download completion observable); prior native-download CDP evidence stands.
- Evidence: checks/deep-audit-loops/loop-1/L1E-persistence-result.json (18 pass / 1 fail / 2 env-bounded).

Stage Summary:
- F07/F10/F11/F12/F13/F14 loop-1 stages executed (F08/F09 env-bounded closure). One new confirmed bug (notebook-history removal scrub breaks recovery promise). Password lifecycle entirely clean. Next: launch L1-F/L1-G/L1-H/L1-I subagent batches (imports/exports, editor-core completion, proofing+misc, performance), then loop-1 close.

---
Task ID: L1-F
Agent: subagent (general-purpose, read-only bug hunt)
Task: Imports / exports / backups — F15 local imports, F16 Google import (source-bounded), F17 export scope JSON/DOCX/ZIP/map, F18 backup restore, persistence.

Work Log:
- Session l1io on http://localhost:3000/. Fixtures: l1f-a.md (h+list+quote+bold), l1f-b.txt (CRLF), l1f-c.html (h1+p+table), l1f-d.md, l1f-e.md, l1f-t.html (h1+ul+table), l1f-q.md (two-paragraph quote), hand-crafted /tmp/l1f-backup.json.
- F15: imported each fixture via sidebar Import → Files… (#mdInput). Verified rich-view element fidelity + window.__np3.doc().markdown, pre- and post-reload. Verified sequential imports, non-empty collection destination, upload-time doc-switch race, import while Tab 2 active with pending text, pending-edit preservation across import+reload, duplicate-name import.
- B226 verification + extension: .txt/.html imports have markdown:"" IMMEDIATELY (before save) and persistently; View→Markdown shows EMPTY source; typing one char there and switching back REPLACES the entire imported document; autosave persists the wipe; after reload loss is permanent (Undo recovers only pre-reload). Reproduced 2/2 docs; control: .md import keeps source populated (74 chars) so source typing is a normal edit.
- F17: File backstage → Export & restore. Routes triggered: One file+DOCX (l1f-e; l1f-t with h1+list+table — advertised "Exported l1f-t.docx"), DOCX of combobox-selected NON-active doc (advertised l1f-a.docx — no stale-active misdirection), Everything+JSON, Everything+ZIP, Selected files (2 checked)+ZIP ("Exported Notebook.zip"), File map overview+canvas and +png. Editor innerText/markdown identical pre/post for all 7 routes; zero console/page errors.
- F18: backup schema learned from dialog text + source (validateExportBackup: format notepad-backup/schemaVersion 1/scope; assertWorkspaceSchema: version 1, id, files[], extra). Built envelope from live workspace snapshot with one file id colliding with live l1f-t id. Add-mode restore: collision remapped to fresh id, existing l1f-t untouched, restored content landed + activated; "Undo last restore" performed full rollback. Observation: Add-restore switches sidebar to a NEW same-named "My collection" containing only restored files (existing docs hidden behind identically-named tab; data intact; source-consistent: prepareCollectionRestore remaps ids, mergeIncomingCollections merges by id only).
- F16: bounded source check only (openGoogleImport/exportNotepadGoogle present; dialog instructs structured export for tabs/subtabs); no network relay in env.
- Source pass on importDocuments (~orig line 4797): rich-path (txt/html/rtf/doc/odt/docx-html) sets f.richHtml=html with markdown="" (only md/markdown ext sets markdown=text) — mechanism for B226 extension.

Stage Summary:
- One NEW confirmed bug (B226 EXTENSION, destructive): rich-path imports (.txt/.html) leave Markdown source empty immediately; a single keystroke in the empty source view destroys the whole imported document and autosave makes the loss permanent after reload. Reproduced 2/2, controls pass (md-path source populated; undo pre-reload recovery). Fix direction: generate markdown from imported richHtml at import time (or block source-mode editing when markdown was never synced).
- Rediscovered/verified: B226 (html+txt paths, immediate-empty variant). B233 NOT reproduced (two-paragraph quote survives). B284-family races clean (active follows user click; pending edits flushed).
- Enhancement-level observations: duplicate-name imports allowed; Add-restore hides existing files behind duplicate same-named collection until tab switch; #mdInput processes uploads while dialog closed.
- Predicates: 21 pass / 3 fail / 3 observations. Not covered: DOCX/DOC/ODT/RTF/PDF/picture import, Google runtime, ZIP-branch restore, folder-scope export + folder-collision restore, B270 header propagation (known, no headers authored), native download completion (headless-unobservable).
- Evidence: checks/deep-audit-loops/loop-1/L1F-io-result.json

---
Task ID: L1-G
Agent: subagent (general-purpose, read-only bug hunt)
Task: Editor core completion + References + Review — F26 paragraph formatting, F29 lists/checklists, F30 list options, F31 slash, F33 statistics, F40 references, F42 track edits, F43 side-by-side, persistence.

Work Log:
- Fresh l1edit session. F33: 'one two three four five' → status bar 5 words; stats dialog Words 5 / Chars 19(23 with spaces) / Paragraphs 1 / Lines 1 — exact.
- F26: Center/Right/Justify (data-a), line spacing 1.5→2.0 (data-ls), paragraph dialog Indentation Level 1 (data-in) — all applied to target paragraph only, serialized via np3 metadata comments, persisted across reload byte-identical. Styles gallery Quote tile → <blockquote> created; MARKDOWN = '>' ALONE (B233 rediscovered: direct paragraph text dropped from markdown; rich text persists fine).
- F29/F30: bulleted list, Tab nest 2 levels, Shift+Tab outdent, re-nest — DOM + markdown correct each step. Numbered conversion + List options (a,b,c + Start at 3) → <ol start=3 list-style-type:lower-alpha> honored. Checklist via slash menu: input[data-task] inserted; checkbox click → DOM checked immediately but markdown stays '- [ ]' until next keystroke flush (B218 mechanism observed); after flush, checked state persisted across reload. Observation: slash-Checklist placeholder text 'Task' remains in the item alongside typed text.
- F40: 3 headings → Contents (TOC + anchor links, correct entries). Footnote → np3-fnref sup + np3-fndef definition, persisted. NEW BUG (3× repro + 2 controls): caret in an EMPTY paragraph directly before the non-editable Contents block + ONE Delete press DESTROYS the entire TOC. Native control (bare contenteditable, same structure): both blocks survive Delete. In-app Backspace control: TOC survives. Asymmetry isolates the app's forward-delete paragraph-normalization path (guards exist for .np3-toc in walkers/updateToc but not in the delete/merge normalizer). Candidate: Enter-split of an id-bearing heading duplicates the np3-ref-* id on both resulting headings.
- F42: Track edits ON → paragraph-level data-rid tracking; Review edits pane lists Changed block with baseline; Accept keeps current block; data-rid persisted after reload.
- F43: Compare side by side opens prefilled with current doc; Compare renders diff; doc innerText identical before/after; no errors.
- Persistence: headings + footnote + tracked paragraph + text all persisted exactly after reload.
- Harness note: one early eval blanked editor.innerText during F33 exploration; state reset via localStorage.clear()+reload immediately; all reported results come from the clean state. Typing used keyboard-type/range caret placement after observing that 'type' clicks element center (harness artifact).

Stage Summary:
- One NEW CONFIRMED bug: single Delete keystroke in an empty paragraph before the Contents block permanently destroys the whole non-editable TOC (native + in-app controls both isolate the app's forward-delete normalization; fix: guard merge when next block is .np3-toc/.np3-fndef/contenteditable=false).
- One CANDIDATE: duplicate heading anchor id after Enter-split of a Contents-id-bearing heading.
- Rediscovered: B233 (quote text dropped from markdown), B218 mechanism (checkbox completion not committed to markdown until next edit).
- Clean: alignment/spacing/indent/quote-rich, list nesting/outdent/options, checklist DOM+persist, statistics, footnote, track edits accept, side-by-side no-mutation, persistence. Predicates 18 pass / 2 fail / 3 observations.
- Not covered: change case + sort lines, slash edge variants (in list/table/start+Escape), bookmark navigation, citation insert/edit (B285), symbols, B254 deep test, B232 middle-heading Update isolation.
- Evidence: checks/deep-audit-loops/loop-1/L1G-editor-result.json

---
Task ID: L1-I
Agent: subagent (general-purpose, read-only bug hunt)
Task: F69 performance/optimization assessment (read-only measurements) + editor leftovers (F26 case/sort, F31 slash variants, F40 bookmark/citation/symbol).

Work Log:
- F69 boot: cold navigation 1376ms (load event) for the 15.3MB single-file HTML over localhost; warm reloads 311-385ms nav duration; editor+__np3 ready ~500ms after reload command (incl. CLI transport); reload WITH a 200-paragraph imported doc showed the same warm profile (385ms nav, ready at ~501ms, all 200 paragraphs rendered).
- F69 typing: 30 chars on small doc = 0.226s total (~7.5ms/char incl. transport), 30/30 accepted; 5 individual key presses at end of the 200-para doc = 0.213s (~43ms/key incl. transport), 5/5 accepted — no measurable large-doc lag.
- F69 save: sampled #autosaveIndicator — edit → 'Saving to browser…' at ~1.5s (debounce) → 'Autosaved' within ~5s window; quiet sampling steady 'Autosaved'. UR-11 satisfied (saves backgrounded).
- F69 memory (performance.memory): 18MB fresh → 19-20MB after typing → 20MB after 200-line import → 33MB after reload with large doc. No anomaly measured.
- F69 source pass: scheduleCommit (17 call sites, quiet period), layoutPages (idle-adaptive redefinitions: max(180,1200-idle) / max(180,1650-age+40) / 150ms), NotepadPacked worker compression, 30 requestIdleCallback/rAF occurrences — all present. C26F font-carrier growth NOT re-measured (prior evidence stands, measured-not-bug).
- F26: UPPERCASE, Sentence case, Sort lines all exact (BRAVO/ALPHA/CHARLIE → restored → Alpha/Bravo/Charlie, markdown matches).
- F31: slash in list item → menu opens, Escape clean; slash at doc start → full menu, Escape clean; slash in table cell → menu does NOT open (observation: possible intended limitation).
- F40: Bookmark 'mark1' added + Go to bookmark navigates correctly. NEW BUG 1 (CONFIRMED): Enter-split of a bookmarked paragraph duplicates data-bookmark AND the np3-ref-* anchor id onto every new paragraph from the split (3× 'mark1' with identical ids; persists across reload; bookmarks dialog lists duplicates).
- F40 citation: insert works (in-text link + References bibliography). NEW BUG 2 (CONFIRMED, B285-family new trigger): Backspace×2 on the citation text then Ctrl+Z×2 restores the link text fully but REMOVES the bibliography (heading + entry) → dangling citation. Control: pre-edit bibliography present; post-undo link present + bib absent.
- F40 symbol: Special characters dialog → © inserted at selection; observation: symbol inserted right before a citation link is absorbed into the link across save/reload.
- Persistence: text, citation link, symbol, triplicated bookmark, imported 200-line doc all persisted after reload.
- Harness notes: one eval briefly set editor.innerHTML for the case/sort fixture (undone immediately, fixture retyped via real keyboard); typing used range-placed carets + keyboard type/press; modal dialogs block editor keystrokes (expected).

Stage Summary:
- Performance: NO contract violations measured — boot 0.3-1.4s nav, typing ~7.5ms/char, saves debounced ~1.5s and backgrounded, heap 18-33MB. All items classified MEASURED_OPTIMIZATION_NOT_BUG; optimization hooks (scheduleCommit/layoutPages idle scheduling/NotepadPacked) verified present in source.
- Two NEW confirmed bugs from editor leftovers: (1) bookmark+anchor-id duplication on paragraph split (persists, pollutes bookmark list/navigation); (2) dangling citation after undoing adjacent deletions (bibliography removed, link kept — B285 new trigger).
- Rediscoveries: none new; B135/B242/B285-original not re-tested (variants only).
- Predicates: 12 pass / 2 fail / 4 observations. Not covered: font-carrier re-measurement, file:// boot, slash-in-quote, B135/B242 re-tests, citation URL field.
- Evidence: checks/deep-audit-loops/loop-1/L1I-perf-result.json

---
Task ID: L1-H
Agent: audit subagent (misc/proofing completion)
Task: Proofing completion + misc surfaces (F55 spelling/grammar/context, F56 autocorrect, F57 proofing lifecycle, F58 Ink, F59 mobile, F60 dark theme, F61 drag-drop source-check, F62 context menus, F66 status bar, F67 dialogs focus, F68 reload integrity) — read-only bug hunt, session l1misc.
Work Log:
- Read brief, 80 known-bug titles, UR register (UR-22/UR-26 timing/Off-design policies respected). Reset predecessor state via localStorage.clear()+reload (beforeunload flush re-persisted it; typed own synthetic text over via Ctrl+A+Delete).
- F55: typed misspellings; underlines in #harperProofLayer85 overlay (harper-spelling/harper-grammar) after ~4s cold start; grammar needed ~9s. Right-click via DISCLOSED synthetic MouseEvent('contextmenu',clientX/Y) at Range coordinates (agent-browser cannot right-click; app uses caretPositionFromPoint so path matches). Spelling menu [receive/relieve/recipe/Ignore session/Add dictionary] applied; grammar menu note+suggestion applied ('could of'→'could have'); Add-to-shared-dictionary cleared underline; heading 'Tmp'→'Temp' via heading context menu.
- F56: standard pairs (Teh→The, definately→definitely on space), sentence capitalization, Settings dialog custom pair zqx→zqxfixed + exception 'teh' (blocked + persisted across reload), variants in H1 heading and real LI both correct; correction chip Undo/Never-correct affordance tested: immediate mid-sentence Undo restores exact text (control PASS).
- F57: Review-tab spell toggle off → 0 marks / aria-pressed false; on → 15 marks after rescan.
- F58 Ink: pen strokes via CDP mouse down/move/up (2 strokes), Select Objects marquee + move selection (pts +0.10 shift), Eraser 2→1, reload persistence (1 stroke), Erase all → 0.
- F59: 390x844 compact layout + typing OK; paper 794px pans horizontally in Print Layout (emulation, Web Layout alternative; not counted — B211/S17 context). Screenshot l1h-mobile.png.
- F60: dark toggle → dark chrome, white paper readable (pixel-analyzed l1h-dark.png: 5519 white vs dark ink samples), typing OK, reload → html[data-theme=dark] persisted; toggled back.
- F62: context menus on selection (items incl Cut/Copy/Paste/Bold…; Bold applied → <b>), on heading (spelling + standard; correction applied), on LI (standard items).
- F66: Page 1 of 1; word count 63/83 total & '1 word selected'; save indicator Autosaved → 'Saving to browser…' → Autosaved.
- F67: Word Count dialog (focus trap, background typing blocked, Escape closes, focus→editor); Find/Replace bar (Tab/Shift+Tab cycle, Escape closes, np3-find/np3-cur highlights cleaned).
- F68: text+list+heading+bold doc reload round-trip byte-exact (460=460 chars, diff empty; kids/lis/heads/bolds identical); localStorage keys=1 (workspace snapshot holds files+prefs).
- F61: source-check only — dragover/drop handlers, sidebar drop branch, document-tab internal drag (application/x-notepad-document-tab), file-drop filter exist; OS file drops not runtime-testable.
- Source pass: proofReplacement84/proofPrefs84/addGrammarMenu85/paintHarperView85/harperCSS85/Harper85 (pagehide stop)/proofReverse84/proofChip84/autoMarks841/Ink object/applyTheme(dataset.theme persisted in workspace prefs; theme JS sits in an earlier script block outside the app-js.txt extract).
- FINDING 1 (CONFIRMED, minor): sentence-start correction-chip Undo restores capitalized form, not typed text ('qwe '→'Qtt '→Undo→'Qwe '; also zqx→'Zqx'); control mid-sentence restores exact 'qwe'. Mechanism: proofLast84.original recorded after capitalization already applied; proofReverse84 single-level undo.
- FINDING 2 (CANDIDATE): correction chip stays visible after continued typing but Undo click is a silent no-op ('definately more words '→'Definitely more words ', Undo click → unchanged; 2×). Mechanism: proofReverse84 guard last.state!==Undo.last → only clears chip.
Stage Summary:
- 2 new findings (1 CONFIRMED minor, 1 CANDIDATE), 0 rediscoveries; all other families clean with controls (53 predicates pass / 2 fail).
- Not covered: OS file drops (F61), Lasso ink tool, Eraser drag-vs-tap nuance, mobile image toolbar (B211 variant), context-menu Paste paths (B241 variant), Proofing-Off autocorrect interaction (UR-26 requested design), Harper worker release.
- Evidence: /home/z/my-project/checks/deep-audit-loops/loop-1/L1H-misc-result.json (+ l1h-mobile.png, l1h-dark.png, l1h-ink2.png).

---
Task ID: 2-a
Agent: main (L2-A batch; subagent dispatch unavailable)
Task: Loop 2 batch L2-A — F05/F06 mind map & graph deep audit

Work Log:
- Quarantined empty skeleton L2 result files left by timed-out subagent dispatches (abandoned/); kept their IO fixtures.
- Source review: inline edit lifecycle (extract L1269), UI.doUndo override (L1275), clipboard packets (L1268), connectFileMapNodes guards (L1308), renderMap signature-skip predicate (L1257), mindMapVisibleGraph projection.
- Runtime (session l2main): drag-create node, inline edit commit/cancel, undo-during-edit, cross-view clipboard paste, duplicate/self-loop edges (both CONFIRMED via writer.map data read), map undo, comment add/delete, arrow nudge+undo, collapse/expand, unicode persistence, file-map copy/paste.
- B291 rediscovered twice (exact documented trigger). Cross-view silent paste recorded as observation (contract uncertain).

Stage Summary:
- 1 NEW CONFIRMED bug: mind-map connect-drag lacks same-node + same-direction duplicate guards (self-loops + parallel edges persist across reload); file-map sibling layer has both guards (contrast).
- 21 predicates pass / 2 fail (the confirmed finding) / 1 observation. Evidence: checks/deep-audit-loops/loop-2/L2A-map-result.json

---
Task ID: 2-b
Agent: main (L2-B batch)
Task: Loop 2 batch L2-B — F01/F02/F03/F04/F65 library & organization deep audit

Work Log:
- Fresh session l2b. Rename paths (title field/File menu), duplicate, same-name rename, empty rename, nested tabs (add/type-isolate/nest/delete+confirm), folder create + move-to-folder, collections create/switch, pending-edit-during-switch, notebook search incl. regex-ish inputs, B289 rediscovery check.
- Source cross-checks: sbQuery/starsOnly sidebar override; tags/star UI absence carried from loop-1 adjudication.

Stage Summary:
- 1 NEW CONFIRMED bug: pending editor content typed immediately before a collection switch is flushed into the newly created/activated 'Untitled' file of the target collection; source file left empty. Flush-window dependent (3s-wait control passes). New surface vs B221/B284.
- 1 CANDIDATE: rename-to-existing-name allowed (indistinguishable rows; contract uncertain).
- B289 rediscovered (title-field path; File-menu path clean).
- 24 pass / 1 fail / 1 candidate. Evidence: checks/deep-audit-loops/loop-2/L2B-library-result.json

---
Task ID: 2-c
Agent: main (L2-C batch)
Task: Loop 2 batch L2-C — F34-F39/F59/F60 layout deep audit + phantom-candidate adjudication

Work Log:
- F34: margins/orientation/paper/columns applied via real UI; widths match exact page math (695.7/1024.5/1489.4px); all persist across reload.
- F35: break insertion flows; B290 rediscovered twice; cover page verified.
- PHANTOM CANDIDATE adjudicated: 4 variants incl. L1C's literal leading-comment trigger — markdown byte-identical, DOM preserved in all; REJECTED (not reproduced).
- F36 zoom slider + floor; F38 watermark (rotated, persists); F59 mobile 390x844 clean; F60 dark persists; S17 not observed; F39 env-limited.

Stage Summary:
- 0 new bugs this batch. Phantom candidate REJECTED. B290 x2 rediscovered. 19 pass / 0 fail / 1 env-limited.
- Harness lesson recorded: offsetParent filter artifact (fixed-position ribbon); JS .click() no-ops vs real clicks.
- Evidence: checks/deep-audit-loops/loop-2/L2C-layout-result.json

---
Task ID: 2-d
Agent: main (L2-D batch)
Task: Loop 2 batch L2-D — F45-F48 images + F50-F54 tables deep audit

Work Log:
- Tables: insert (size grid), fill via Tab navigation, insert/delete row, banded rows, formula dialog (=SUM(ABOVE/LEFT) -> '#FORMULA!' = documented A1-only parser boundary per L1D verdict).
- F53 Tab-escape candidate investigated and REJECTED: activeElement checks invalid in contenteditable; Selection API re-test shows Tab navigation fully correct (A2->B2->C2->next-row-first-cell; last-cell Tab creates empty row). Documented as harness-artifact lesson.
- Images: URL insert with alt (figure/img/md round-trip), selection + resize handles; B292 rediscovered live at 1280px (align button underSidebar=true after scroll).
- Key lesson recorded: cell-position assertions must use getSelection(), not activeElement.

Stage Summary:
- 0 new bugs (F53 candidate rejected as harness artifact). B292 rediscovered. 16 pass / 0 fail / 1 rejected candidate.
- Evidence: checks/deep-audit-loops/loop-2/L2D-imgtable-result.json (+ 2 screenshots)

---
Task ID: 2-e
Agent: main (L2-E batch)
Task: Loop 2 batch L2-E — F07/F11/F13/F14/F19/F68 persistence & protection deep audit

Work Log:
- Autosave cycle verified; F11 password flows verified end-to-end (protect/lock/unlock/change/remove, wrong-pw error clarity, mismatch rejection).
- CRITICAL candidate (change-pw vault corruption) investigated and REJECTED — harness field-pairing artifact; change verified working across reload.
- 1 minor candidate recorded: short-password rejection is silent (no feedback, validity.valid=true).
- B293 rediscovered exactly (deleted file vanishes from all notebook-version snapshots).
- F19 active-doc/theme/zoom persistence verified. Daemon wedge replaced with fresh session.

Stage Summary:
- 0 new confirmed bugs; 1 candidate (silent short-pw rejection); B293 rediscovered. 17 pass / 0 fail.
- Evidence: checks/deep-audit-loops/loop-2/L2E-persistence-result.json

---
Task ID: 2-f
Agent: main (L2-F batch)
Task: Loop 2 batch L2-F — F15/F16/F17/F18/F61/F70 imports/exports/backups deep audit

Work Log:
- Used stable hidden file inputs (#mdInput/#exportRestoreInput/#imgInput) with agent-browser upload for real file IO.
- .md import byte-identical; .html table import OK; empty/unknown-ext/fake-docx/malformed-backup/wrong-schema/wrong-format all handled gracefully with clear toasts.
- FOUND + CONFIRMED: .txt imports (LF and CRLF) populate richHtml only (markdown empty); source mode shows a BLANK editor for the imported content; first source-mode edit silently discards the imported text (richHtml -> ''). Data-loss path demonstrated. .md control sets both representations.
- F16/F17/F61/F70 env-limited as in loop 1.

Stage Summary:
- 1 NEW CONFIRMED bug (.txt import blank-source + destructive source-mode edit). 13 pass / 1 fail / 3 env-limited.
- Evidence: checks/deep-audit-loops/loop-2/L2F-io-result.json

---
Task ID: 2-g
Agent: main (L2-G batch)
Task: Loop 2 batch L2-G — F20-F33/F49 editor core deep audit

Work Log:
- Undo/redo depth, bold/italic nesting + clean undo, find/replace-all literal handling ($& uninterpreted), numbered list apply, stats dialog exact-count verification, styles gallery open + custom-style affordance, clear-formatting residue check (stray b-on-br, NO propagation — observation only).
- Two harness state-muddles disclosed (mode toggle confusion; eval selection setup); all assertions from real-key input.

Stage Summary:
- 0 new confirmed bugs; 1 cosmetic observation. 12 pass / 0 fail. L1G fresh coverage carried for F24/F26/F27/F30/F31/F49.
- Evidence: checks/deep-audit-loops/loop-2/L2G-editor-result.json

---
Task ID: 2-h
Agent: main (L2-H batch)
Task: Loop 2 batch L2-H — F40 citation/footnote + review surfaces + citation-candidate adjudication

Work Log:
- Citation dialog end-to-end (Author/Year/Title -> anchored link at caret); footnote insertion verified; symbol '@' typed directly before citation link -> save -> reload: boundary preserved, candidate REJECTED.
- Comments: anchor creation + pane toggle verified; thread composer not surfaced this session (L1H carried).
- Track edits/Review edits/Compare controls verified to exist; runtime toggle not pinned (ribbon re-render churn) — L1G carried.
- Ink suite controls verified present (Tools ribbon).

Stage Summary:
- 0 new bugs; citation-link candidate REJECTED (not reproduced). 9 pass / 0 fail.
- Evidence: checks/deep-audit-loops/loop-2/L2H-misc-result.json

---
Task ID: 2-i / loop-2 close
Agent: main
Task: Loop 2 close — adjudication, state update, GitHub checkpoint

Work Log:
- L2-I cross-cutting closed (status bar live counts correct; clipboard byte-clean, S13 NBSP not reproduced; S10/S17 not observed; S28 untested-needs-legacy-fixture; F69 carried from L1I fresh).
- Adjudication: 3 new confirmed (B298/B299/B300); 2 candidates open; 3 candidates rejected (phantom-paragraph, citation-absorb, tab-escape); 5 rediscoveries (B290/B292/B293/B289/B291).
- loop-state.json updated (loop 2 complete, NOT clean, confirmedTotal 92, all 70 features, consecutiveCleanLoops 0).
- Repaired audit/known-bug-titles.txt (orphaned dispatches had truncated B289-B297; restored from git HEAD and re-appended B289-B300 in order; 92 titles verified).

Stage Summary:
- Loop 2: 100% complete, NOT CLEAN. Streak 0/2. Loop 3 next (fresh sweep; if clean, loop 4 also required).
