# ConflictSense Accessibility Statement

## Overview

ConflictSense is committed to providing an accessible experience for all users, including those using assistive technologies. In preparation for the Microsoft Foundry Hackathon Accessibility Award, we have audited and upgraded the UI to meet key WCAG 2.1 guidelines.

## Accessibility Features

### 1. Keyboard Navigation
- **Focus Management:** All interactive elements (e.g., Run Analysis button, Conflict Cards, Approval Gates) are fully navigable using the `Tab` key.
- **Action Triggers:** Users can expand conflict cards and trigger actions using the `Enter` and `Space` keys without needing a mouse.
- **Tab Order:** The interface follows a logical, visual tab order flowing from the Header down to the Conflict Dashboard and the Reasoning Trace.

### 2. Screen Reader Support
- **Semantic Landmarks:** The application utilizes `<header>`, `<main>`, and `<section>` roles to allow screen readers to jump easily between the dashboard and reasoning trace.
- **ARIA Labels:** Complex interactive elements are clearly described. For instance:
  - `aria-label="Run AI Conflict Analysis"` on the main execution button.
  - `aria-label="Conflict Severity Summary"` on the dashboard metrics.

### 3. ARIA Live Regions
- **Dynamic Reasoning Trace:** As the multi-agent pipeline executes, the live terminal updates asynchronously. These updates are wrapped in `aria-live="polite"` regions so screen readers announce each new reasoning step without interrupting the user mid-sentence.
- **Alerts:** Critical enterprise risk banners and unexpected conflict warnings are marked with `role="alert"`.

### 4. Visual Contrast & Accessibility
- **WCAG Contrast:** The "severity color system" has been validated to meet WCAG AA text contrast ratios.
  - CRITICAL (#A32D2D text on #FCEBEB background)
  - HIGH (#854F0B text on #FAEEDA background)
  - MEDIUM (#185FA5 text on #E6F1FB background)
- **Focus Indicators:** Interactive components display a clear visual indicator when receiving keyboard focus.

## Testing & Validation
We regularly test ConflictSense using standard accessibility tools and keyboard-only navigation workflows. Future iterations will include automated accessibility testing integrated into our CI/CD pipeline.
