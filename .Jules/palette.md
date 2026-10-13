## 2026-10-13 - Icon-only buttons accessibility pattern
**Learning:** Icon-only control buttons (e.g. discrete mode toggle, settings gear icon) in Vue/Tailwind components lack default screen reader labels and focus indicators.
**Action:** Always provide dynamic or static `aria-label` attributes on icon-only `<button>` tags and pair them with `focus-visible:ring-2 focus-visible:ring-neonLime focus-visible:outline-none` for keyboard accessibility.
