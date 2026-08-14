# Skill: Premium Frontend Engineering

Build a fast, accessible, responsive, editorial jewellery storefront that does not look AI-generated.

Preferred baseline:
- TypeScript
- Vite
- React only if interaction complexity justifies it

Architecture:
components/, features/, pages/, services/, state/, styles/, types/

Centralize API access, error handling and types.

The frontend is not authoritative for price, stock, discount or delivery totals.

UI:
- restrained black/gold
- editorial typography
- generous whitespace
- real product imagery
- subtle motion
- mobile-first
- coherent icon system
- no generic AI gradients
- no excessive glassmorphism
- no giant rounded-card repetition
- no fake luxury imagery

Accessibility:
- semantic HTML
- keyboard navigation
- focus states
- labels
- alt text
- reduced-motion
- accessible dialogs/menus
- meaningful heading order

Performance:
- responsive images
- lazy load below-fold media
- avoid huge bundles
- avoid duplicate requests
- avoid layout shift
- optimize images

Every data page must have loading, empty and error states.

Never inject untrusted HTML or ship secrets.
