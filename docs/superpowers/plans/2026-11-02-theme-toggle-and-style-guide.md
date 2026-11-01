# Theme Toggle and Teaching Design Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the AI BME course theme control with the portal, publish a reusable teaching design guide, and update the HTML explainer specification to put its theme control at the upper left.

**Architecture:** The course keeps its current theme state, persistence, and Mermaid integration; its two HTML templates use the same SVG icon pair, with CSS selecting the visible icon. The new top-level Markdown guide becomes the shared visual reference. The machine-learning explainer specification incorporates the same control treatment but deliberately specifies `inset-inline-start` for its requested upper-left placement.

**Tech Stack:** TypeScript, Vite, CSS, Markdown, Node test runner.

**Spec:** User-approved chat design (2026-11-02): portal-equivalent 40px SVG theme toggle for `ai_bme_intro`; a reusable visual guide covering colors, typography, cards, tabs, theme control, accessibility and RTL; machine-learning explainer theme toggle at upper left.

## Global Constraints

- Preserve Persian/RTL behavior and use CSS logical properties.
- Never edit generated `generated/**` or `dist/**` content manually.
- Preserve `ai_bme_intro` theme persistence via its existing `theme` localStorage key and Mermaid refresh behavior.
- Do not change authored course content or `course.json`.
- The shared guide is written to `/home/saeed/Desktop/teaching-portal/` (the workspace root).
- `machine_learning` explanatory pages use an upper-left fixed theme button, despite the portal and course site using upper-right.

## Review Focus

- Both course page templates contain the same two-icon button markup.
- The visible course icon matches the current `data-theme`; clicking still persists and updates Mermaid.
- The 40px fixed control does not cause page overflow or cover essential navigation on a 360px viewport.
- The style guide provides literal tokens and component rules rather than vague visual descriptions.
- The explainer specification contains no stale upper-right / `right:16px` / `padding-right:52px` direction for its theme button.

---

### Task 1: Align the AI BME course theme control

**Files:**
- Modify: `ai_bme_intro/src/routes.ts`
- Modify: `ai_bme_intro/src/render.ts`
- Modify: `ai_bme_intro/src/main.ts`
- Modify: `ai_bme_intro/src/styles.css`
- Test: existing `ai_bme_intro` Node test suite, plus a focused test if template tests exist

**Interfaces:**
- Consumes: the existing `#theme` control and `applyTheme(theme: string)` in `src/main.ts`.
- Produces: an unchanged theme API with two inline SVG icons selected by CSS.

- [ ] **Step 1: Write a failing test or focused assertion**

Assert that each course-page template renders `.icon-sun` and `.icon-moon`, and that CSS selects the icon matching `data-theme`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `npm test`
Expected: FAIL because templates currently render an emoji-only toggle.

- [ ] **Step 3: Replace both template controls with identical inline SVG markup**

Keep `id="theme"`, `type="button"`, `aria-label="تغییر پوسته"`, and title. Remove the emoji `textContent` update from `applyTheme`; CSS controls the active icon.

- [ ] **Step 4: Apply portal-equivalent theme-toggle styling**

Set `#theme` to a 40px circular fixed control at `inset-block-start:14px; inset-inline-end:16px`, using `var(--card)`, `var(--text)`, `var(--border)`, a `0 2px 8px rgba(0,0,0,.15)` shadow, 20px SVG strokes, accent hover/focus, and `data-theme` icon visibility rules.

- [ ] **Step 5: Verify the course**

Run: `npm run check`
Expected: PASS.

### Task 2: Publish the reusable teaching visual style guide

**Files:**
- Create: `TEACHING-PORTAL-STYLE-GUIDE.md`

**Interfaces:**
- Consumes: current portal tokens in `courses_portal/src/styles/tokens.css`, course style tokens in `ai_bme_intro/src/styles.css`, and the approved control design.
- Produces: a standalone Markdown implementation reference for future courses and sessions.

- [ ] **Step 1: Create the guide with exact visual tokens and component contracts**

Include: intended scope; dark/light color tables; Vazirmatn and code-font rules; type scale and spacing/radius; RTL and LTR-island rules; responsive layout; hero; cards; tags; tabs with visible active underline and no visible vertical scrollbar; buttons/focus; course and explainer theme-toggle placement exception; light/dark behavior; accessibility; and a pre-publication checklist.

- [ ] **Step 2: Validate the guide against the two live implementations**

Check every quoted token/value and component rule against the portal/course CSS; correct any mismatch.

### Task 3: Update the HTML explainer specification for the upper-left control

**Files:**
- Modify: `machine_learning/docs/html-explainer-page-spec.md`

**Interfaces:**
- Consumes: the reusable style guide’s theme-control contract and the existing explainer requirements.
- Produces: unambiguous upper-left placement instructions for generated HTML explainers.

- [ ] **Step 1: Update every theme-control placement reference**

Change the page diagram and mandatory rule from upper-right / `right:16px` to upper-left / `inset-inline-start:16px` (or `left:16px` only where the standalone spec uses physical placement). Update the mobile tabs clearance from `padding-right:52px` to logical `padding-inline-start:52px`.

- [ ] **Step 2: Add the SVG visual contract**

Specify the 40px circular control’s card/text/border colors, 20px stroke-only sun/moon SVGs, CSS switching, accent hover, and focus outline, while retaining the existing head script and chart update behavior.

- [ ] **Step 3: Read the modified specification end-to-end**

Verify it contains no contradictory upper-right placement or stale physical-right mobile clearance.

### Task 4: Final verification and review

**Files:**
- Verify: all Task 1–3 paths

- [ ] **Step 1: Run course verification**

Run: `npm run check` in `ai_bme_intro/`
Expected: PASS.

- [ ] **Step 2: Inspect documentation paths and diff hygiene**

Run: `git diff --check` in `ai_bme_intro/`, and review the Markdown files for exact paths and contradictory placement text.

- [ ] **Step 3: Request independent full-worktree review**

Provide the reviewer this plan, changed paths, and test output; address any material finding before completion.
