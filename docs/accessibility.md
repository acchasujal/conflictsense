# ConflictSense Accessibility Statement

**Version:** 1.0  
**Last Updated:** June 2026  
**Standard:** WCAG 2.1 AA

---

## Our Commitment

ConflictSense is built to be usable by everyone, including people with disabilities. We are committed to conforming to the **Web Content Accessibility Guidelines (WCAG) 2.1 Level AA** standard.

This accessibility statement covers the ConflictSense web application at [conflictsense.vercel.app](https://conflictsense.vercel.app).

---

## Accessibility Features

### ♿ Keyboard Navigation
ConflictSense can be **fully operated using keyboard navigation** without requiring a mouse.

| Element | Keyboard Action |
| :--- | :--- |
| Scenario cards | `Tab` to focus, `Enter` or `Space` to activate |
| Conflict cards | `Tab` to focus, `Enter` or `Space` to expand/collapse |
| Upload controls | `Tab` to focus file picker, `Enter` to open |
| Run Analysis button | `Tab` to focus, `Enter` to activate |
| Accessibility toggles | `Tab` to focus, `Enter` to toggle |

### 👁 Focus Indicators
All interactive elements display a **high-visibility blue focus ring** (`3px solid #2563EB`) when focused via keyboard. This indicator is never suppressed or hidden.

### 📢 Screen Reader Support
ConflictSense includes built-in **Screen Reader Mode** (toggle in the application header).

When enabled, the application announces:
- "Analysis started. AI agents are reviewing policy documents."
- "Conflict detected: [conflict title]. Severity: [severity]."
- "Analysis complete. [N] conflicts detected."

All interactive elements have descriptive `aria-label` attributes. The reasoning trace panel includes `aria-live="polite"` for real-time step updates. The responsible AI banner uses `role="alert"`.

### 🎞 Reduced Motion Mode
ConflictSense respects the operating system **prefers-reduced-motion** setting automatically. For users who need explicit control, a **Reduce Motion** toggle is available in the application header, which disables all shimmer animations, slide-in transitions, and chart animations instantly.

### 🎨 Colour Contrast
All text and UI elements meet or exceed **WCAG AA contrast ratios**:
- Primary text (`#0F172A` on `#FFFFFF`): 18.4:1 ✅
- Body text (`#334155` on `#FFFFFF`): 10.1:1 ✅
- Secondary text (`#64748B` on `#FFFFFF`): 4.6:1 ✅
- Critical severity badge (`#A32D2D` on `#FCEBEB`): 5.9:1 ✅
- Focus ring (`#2563EB` outline, 3px): Visible on all backgrounds ✅

### 🏷 Semantic HTML
The application uses proper HTML5 semantic elements:
- `<header>` with `aria-label="Application Header"`
- `<main>` with `aria-label="Main Application Content"`
- `<button>` for all interactive triggers
- `role="button"` with `tabIndex={0}` for custom card interactions
- `role="status"` with `aria-live="polite"` and `aria-atomic="true"` for live announcements
- `role="group"` for the accessibility settings control group

---

## Known Limitations

| Area | Status | Note |
| :--- | :--- | :--- |
| Recharts visualisations | Partial | Charts are decorative; key data is also available as text. |
| PDF document upload | N/A | Uses native `<input type="file">` with browser-native accessibility support. |

---

## Testing Approach

ConflictSense accessibility has been tested with:
- **WAVE** browser extension (automated checks)
- **axe DevTools** (automated ARIA validation)
- **Keyboard-only navigation** (Chrome, Firefox)
- **Code review** against WCAG 2.1 AA success criteria

---

## Reporting Accessibility Issues

If you encounter any accessibility barriers while using ConflictSense, please report them by opening a GitHub issue at [github.com/acchasujal/conflictsense](https://github.com/acchasujal/conflictsense/issues).

We aim to respond to accessibility reports within **5 business days**.

---

## Legal Basis

This statement is made in accordance with:
- [WCAG 2.1](https://www.w3.org/TR/WCAG21/) (W3C)
- [Section 508](https://www.section508.gov/) (US Federal)
- [EN 301 549](https://www.etsi.org/deliver/etsi_en/301500_302000/301549/03.02.01_60/en_301549v030201p.pdf) (EU)
