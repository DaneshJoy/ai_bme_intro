# Course Theme Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the independent course site's theme toggle match the new portal toggle.

**Architecture:** Keep the existing theme state, localStorage persistence, and Mermaid update logic. Replace the emoji content in both page templates with the same inline sun/moon SVG pair, and style `#theme` with the portal-equivalent 40px fixed circular control whose visible icon depends on `data-theme`.

**Tech Stack:** TypeScript, Vite, CSS, Node test runner.

**Spec:** User-approved chat design (2026-11-02): 40px top-right SVG sun/moon button, portal-matching colors/hover; theme behavior unchanged.

## Global Constraints

- Preserve Persian/RTL behavior and use logical CSS properties.
- Do not edit `generated/**` or `dist/**` manually.
- Preserve the existing `theme` localStorage key and Mermaid theme refresh.
- Do not change authored course content or `course.json`.

## Review Focus

- Both the content and code-index page templates render the same button markup.
- Dark mode shows the moon icon; light mode shows the sun icon.
- Toggling still persists the selected theme and updates Mermaid rendering.
- The fixed button remains usable at small viewports and does not create horizontal overflow.
- Keyboard focus remains visibly indicated.

---

### Task 1: Match the course theme toggle to the portal

**Files:**
- Modify: `src/routes.ts`
- Modify: `src/render.ts`
- Modify: `src/main.ts`
- Modify: `src/styles.css`
- Test: existing `test/**` suite, or an added focused test if template tests exist

**Interfaces:**
- Consumes: `#theme` button queried in `src/main.ts`.
- Produces: a two-SVG theme control with unchanged click and persistence behavior.

- [ ] **Step 1: Write a failing focused test or assertion**

Assert each rendered page includes both `.icon-sun` and `.icon-moon`, and that the active theme selects the matching icon.

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `npm test`
Expected: FAIL because current templates render emoji-only controls.

- [ ] **Step 3: Replace both emoji controls with identical accessible inline SVG sun/moon markup**

Keep `id="theme"`, `type="button"`, `aria-label`, and title unchanged. Remove the `textContent` update in `applyTheme`; CSS controls icon visibility.

- [ ] **Step 4: Style `#theme` in `src/styles.css`**

Use a fixed 40px circular card at `inset-block-start: 14px` and `inset-inline-end: 16px`, with `var(--card)`, `var(--text)`, `var(--border)`, a 2px/8px shadow, 20px stroked SVGs, and accent hover/focus styling. Hide/show the appropriate SVG using `:root[data-theme]` selectors.

- [ ] **Step 5: Run complete verification**

Run: `npm run check`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/routes.ts src/render.ts src/main.ts src/styles.css test
git commit -m "style: align course theme toggle with portal"
```
