# Audit Log

## 2026-09-17 — functional-testing: browser-session.md orphaned from Read First / Stage 0

A live functional-testing round against `taxSummary` opened the workflow
browser session without `--headed`. `playwright-cli open` reported success
(pid, page title, snapshot) with a real page load, so the session looked
healthy from its own output — but no OS-level window existed for the user
to log into or complete MFA on. The user only discovered this because
nothing appeared on screen.

Root cause traced to `SKILL.md`, not to `references/browser-session.md`
itself: `--headed` (Section 2) and the pre-login window-verification check
(Section 5) were correct and complete in `browser-session.md`, but that
file was never in `SKILL.md`'s "Read First, In Order" list — only
`browser-gotchas.md` and this skill's own `gotchas.md` were. Every place
`SKILL.md` did cite `browser-session.md` (Prerequisites, Stage 0, Subagent
Dispatch Rules — three citations total) pointed only at Section 0 (session
naming), never at Sections 2 or 5. Stage 0, the exact point where the main
thread mints the session name and opens it, said "before opening it" with
no inlined launch command and no pointer to the section that defines one.
The Read First list's own line 189-190 additionally claimed session/login
handling was "covered separately by Prerequisites... and Subagent Dispatch
Rules" — that claim was false; neither section restates Sections 2 or 5.

Fixed in `SKILL.md`:
- Read First, In Order now lists `references/browser-session.md` in full as
  item 2, with an explicit note that Sections 2 and 5 are not covered by
  what Prerequisites/Subagent Dispatch Rules cite.
- Removed the false "covered separately" claim from the Read First list's
  first item.
- Stage 0 now inlines the actual launch command
  (`playwright-cli -s=<name> open --headed --browser chrome <url>`) and the
  window-verification check at the point where the session is opened,
  instead of a bare pointer to Section 0.

`references/browser-session.md` required no changes — the contract was
already correct; it was simply unreachable from the workflow that was
supposed to follow it.

## 2026-09-17 — swept other playwright-driving skills for the same gap

Checked every skill in this repo that references `playwright-cli` or
`browser-session.md` for the same orphaning pattern found above
(`functional-testing`, `user-manual-update`, `fusionx-urs`,
`api-field-mapper`; `banking-pillar-release-update` confirmed not to use
Playwright at all).

- `user-manual-update` had the identical gap: Workflow step 2 ("Walk UAT")
  cited `references/browser-session.md` Section 0 only, and Read First, In
  Order never listed the file — only this skill's own `gotchas.md`, which
  does correctly document "`open` launches headless by default" but is not
  itself the point where the launch command gets written. Fixed the same
  way: added `browser-session.md` (full file) to Read First, and inlined
  the `--headed --browser chrome` launch command plus the Section 5
  window-verification check directly into step 2.
- `fusionx-urs` was already correct: its live-walkthrough step says
  "read and follow `references/browser-session.md`; it is the
  self-contained, mandatory Playwright contract for this skill" with no
  section-scoping caveat — no orphaning, no fix needed.
- `api-field-mapper` was already correct: "Before any browser interaction,
  read and follow `references/browser-session.md`; it is this repository's
  mandatory session contract and takes precedence over this skill's
  browser-specific guidance" — full-file instruction stated before any
  citation narrows to a specific section, plus `--headed` is separately
  inlined at its own launch command. No fix needed.

Pattern going forward: any citation of `browser-session.md` that names a
specific section (e.g. "Section 0") without also either (a) telling the
reader to read the whole file first, or (b) inlining the Section 2 launch
command and Section 5 verification check at the point of use, reproduces
this gap. Check new citations against this before adding them.

## 2026-09-18 — exhaustive sweep: confirmed no remaining instance of this gap

Followed up on the two fixes above with a full sweep rather than trusting the
per-skill spot-check was complete, per user request to check "everywhere."

- Located the actual sync mechanism, `scripts/sync-shared.py`: it propagates
  `shared/browser-session.md` into exactly four targets — `fusionx-urs`,
  `functional-testing`, `user-manual-update`, `api-field-mapper` (matching
  the four already audited; `banking-pillar-release-update` is correctly
  excluded, confirmed separately to not use `playwright-cli` at all). Diffed
  all four skill-local copies against the canonical source: byte-identical,
  no drift.
- Repo-wide search confirmed no file outside these four `SKILL.md`s and their
  `references/browser-session.md` copies drives `playwright-cli`.
- Scanned all 82 installed `SKILL.md` files across every plugin/skill in the
  local Claude Code environment (`~/.claude`, all marketplaces/plugins): none
  outside this repo reference `playwright-cli` at all, so this gap class
  cannot exist anywhere else in the current setup.
- One non-operational hit: `docs/superpowers/specs/2026-09-09-functional-
  testing-skill-design.md:249` also says "Section 0 in particular" — a dated
  historical design note, never read at runtime by an executing skill round,
  so it cannot itself cause a headless launch. Left unchanged (rewriting a
  dated historical doc to match current behavior would misrepresent what was
  true when it was written); recorded here rather than silently passed over.

Conclusion: the gap fixed in `functional-testing` and `user-manual-update`
above was the full extent of it. No further instances found.

## 2026-09-18 — generalized the gap class beyond browser-session.md; found and fixed two more instances

The 2026-09-18 sweep above scoped "this gap" to citations of `browser-session.md`
specifically. That scope was too narrow, and its "no further instances found"
conclusion was wrong — corrected here rather than left standing.

**The general rule, not a browser-specific one:** whenever a task requires
reading a reference file for guidance, and that file is cited by naming one
specific section, the citation must actually cover everything the file says
about that task — not just whichever section happens to get named. A
citation that names one section while sibling sections elsewhere in the same
file independently govern the same task reproduces the browser-session.md
bug, regardless of which skill or which reference file is involved. The
`browser-session.md` fixes above are one instance of this general class, not
the whole class.

Re-swept every `references/*.md` citation in every skill's `SKILL.md` against
this generalized rule (not just browser-session.md citations). Found two more
real instances, both in `fusionx-urs/SKILL.md`, both in citations of
`references/docx-formatting.md` (a single 2,300+ line multi-topic reference
file organized into many independently-titled sections):

- **Numbering.** The STEP 3.5 edit-gate paragraph said "Read
  `references/docx-formatting.md`'s numbering section in full" (singular,
  unqualified) — but numbering guidance is split across three separate,
  independently-confirmed-critical sections: "Numbering — heading indent must
  increase progressively per level" (indent/hanging values — confirmed wrong
  once via a direct screenshot comparison), "Numbering is one continuous
  system, not several separate features" (which elements get real `numPr`
  vs. bullets vs. typed text, plus the ToC-entry exception), and "Numbered
  sub-points inside story cells" (the story-cell list mechanism — confirmed
  wrong once via an undercounted-rows defect). A reader following "the
  numbering section" as written could easily land on just one of the three
  and never see the other two. Fixed: the citation now names and summarizes
  all three sections explicitly and says to read all three, not just
  whichever one is found first.
- **ToC/List of Figures/List of Tables.** The page-numbering workflow step
  pointed only at the "...must be genuine, live, updatable Word fields"
  section to explain "why each of these phases is required" — but a second,
  separate section, "...— structural placement (not hyperlink color)," covers
  a different confirmed defect class entirely (ToC appearing as a numbered
  sub-heading instead of sitting unnumbered before Section 1; the explicit
  black/no-underline color override a real Word `TOC` field needs). Fixed:
  the citation now names and summarizes both sections and says to read both.

Checked but found **not** to reproduce this pattern: `fusionx-urs`'s citations
of `build-input.md` (single-purpose schema doc, no section-scoping),
`urs-format.md` and `open-banking.md` (referenced as whole files or as flat
glossaries, never a narrowed single-section citation), and the "## DOCX
FORMATTING" top-level pointer to `docx-formatting.md` itself (names topics —
fonts/colors/table-styles/column-widths — against the whole file, doesn't
name one specific heading while excluding siblings). Also re-checked
`api-field-mapper`'s and `functional-testing`'s citations of
`browser-gotchas.md` and `live-capture-examples.md`, and
`banking-pillar-release-update`'s citation of
`repurposing-for-other-pillars.md` — all instruct reading the whole file, no
section-narrowing.

Both fixes applied directly to the `fusionx-urs` `SKILL.md` in this repo and
synced back to the locally installed skill copy (this time the edit was made
in the repo clone first — confirmed the installed copy was stale and copied
the fix across, the reverse direction from the browser-session.md fixes
above, which were made in the installed copy first).

This gap class is now understood to require checking on any future reference
file, not just `browser-session.md` — that's the standing rule, not a
one-time cleanup.
