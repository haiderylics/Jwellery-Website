# Jewellery Website — Design System & UI Direction

**Visual objective:** Premium jewellery brand. Modern, quiet luxury. Human-designed. Editorial. No obvious AI/template fingerprints.

---

## 1. Design Philosophy

The website should feel:

- premium
- elegant
- editorial
- confident
- minimal
- tactile
- warm
- trustworthy

It should not feel:

- flashy
- cheap
- overdecorated
- generic Shopify clone
- AI-generated
- crowded
- overly animated

Primary principle:

> Let the jewellery be the visual hero. The UI should frame it, not compete with it.

---

## 2. Color System

### Core

```text
Obsidian:       #0B0B0B
Soft Black:     #131313
Warm White:     #F7F4EE
Pure White:     #FFFFFF
Gold:           #C9A227
Light Gold:     #E3C96A
Muted Text:     #A7A7A7
Border:         #292929
Success:        use a restrained accessible green
Error:          use a restrained accessible red
```

Do not use gold for every element.

Gold is an accent for:

- selected states
- fine borders
- headings/eyebrows
- important CTA accents
- product labels
- micro-details

---

## 3. Typography

Use one primary editorial serif + one clean sans-serif if licensing/performance permits.

Suggested direction:

- Serif for brand storytelling/headings
- Sans-serif for UI/body

Do not use 4–5 font families.

Typography hierarchy:

```text
Display
H1
H2
H3
Eyebrow
Body
Small
Caption
```

Maintain a deliberate rhythm.

---

## 4. Layout

Use generous whitespace.

Desktop:

- max content width around 1200–1320px
- fluid gutters
- consistent grid
- restrained section spacing

Mobile:

- 16–20px side padding
- product cards optimized for thumb interaction
- no tiny controls
- sticky/cart interactions must not block content

---

## 5. Header

Header order:

1. Announcement bar when active
2. Brand/logo
3. Navigation
4. Search
5. Cart
6. Mobile menu

Desktop navigation should feel editorial rather than app-like.

Avoid excessive borders and icons.

---

## 6. Announcement Bar

Purpose:

- Eid sale
- Independence Day
- new collection
- limited-time event

Style:

- dark background
- subtle gold accent
- short message
- optional CTA

Do not make it visually loud.

---

## 7. Hero

Hero should use real jewellery imagery.

Structure:

```text
Small eyebrow
Strong editorial headline
Short supporting text
Primary CTA
Secondary text/CTA
Hero image
```

Avoid:

- AI-generated people wearing fake jewellery
- generic luxury stock photography
- fake lifestyle imagery

Use actual business product photography wherever possible.

---

## 8. Product Cards

Card contains:

- image
- category/label
- product name
- price
- optional compare-at price
- availability
- optional custom badge

Hover:

- restrained image swap or subtle scale
- no exaggerated animations

Mobile:

- touch-first
- no hover-only information

---

## 9. Product Grid

Desktop:

- 4 columns for large catalog screens
- 3 where product imagery needs more breathing room

Tablet:

- 2–3 columns

Mobile:

- 2 columns for browse efficiency
- 1 column when image/detail complexity demands it

Do not force a rigid grid if product image aspect ratios become inconsistent.

---

## 10. Product Detail

Priority order:

1. Image/video gallery
2. Product title
3. Price
4. availability
5. variant selection
6. description
7. custom-order note
8. quantity
9. Add to Cart
10. WhatsApp contact
11. delivery information
12. related products

The gallery should feel premium and spacious.

---

## 11. Cart

Simple.

Show:

- image
- name
- selected variant
- quantity
- price
- subtotal
- delivery
- total
- proceed button

Avoid checkout bloat.

---

## 12. WhatsApp CTA

Use one consistent CTA style.

Examples:

- Order on WhatsApp
- Discuss Custom Order
- Ask on WhatsApp

Do not create fake "instant checkout" expectations.

---

## 13. Reviews

Use:

- restrained quotation mark
- review text
- customer display name
- optional verified indicator only if actually verified

Do not use fake five-star graphics unless the business has a meaningful basis.

---

## 14. Gallery

Use masonry/editorial layout.

Prefer:

- larger real images
- uneven composition
- natural cropping
- subtle captions

Avoid:

- 20 identical card boxes
- stock office/event images

---

## 15. Sale / Event UI

Sale should feel like a campaign, not a popup ad network.

Use:

- full-width banner
- campaign imagery
- concise copy
- one primary action

Popup should be delayed enough to avoid immediate interruption and should respect a "show once" or session-based setting.

---

## 16. Motion

Motion should be subtle:

- 150–300ms micro-interactions
- gentle opacity/translate
- restrained hover
- no constant floating elements
- no auto-rotating hero unless justified

Respect:

```css
@media (prefers-reduced-motion: reduce)
```

---

## 17. Icons

Use one coherent icon set.

Do not mix:

- Font Awesome
- Lucide
- random SVGs
- emoji icons

unless there is a deliberate reason.

Use SVG icons with accessible labels.

---

## 18. Images

Product photography rules:

- consistent aspect ratios
- correct crop
- compressed delivery format
- responsive `srcset`
- lazy-load below fold
- eager-load only hero/primary visual
- meaningful alt text

Never ship 5MB source images to every mobile user.

---

## 19. Empty States

Example:

> No pieces found in this collection.

Then provide:

- clear filters
- browse categories CTA

Never show a blank screen.

---

## 20. Loading States

Use subtle skeletons/placeholders.

Do not show five giant spinners.

---

## 21. Error States

Errors must be:

- clear
- human
- actionable
- visually quiet

Example:

> We couldn't load this collection. Please refresh or try again.

---

## 22. Form Design

Labels above controls.

Strong focus state.

Avoid placeholder-as-label.

Validation message adjacent to the field.

Do not overvalidate on every keystroke.

---

## 23. Footer

Include:

- brand
- short trust statement
- categories
- contact
- WhatsApp
- social links
- delivery information
- copyright
- basic legal links when required

---

## 24. Responsive Quality Gate

Test at least:

- 320px
- 375px
- 390px
- 414px
- 768px
- 1024px
- 1280px
- 1440px

The design should look intentionally composed at every breakpoint.

---

## 25. Premium Quality Gate

Before approval ask:

- Does the imagery feel real?
- Is the typography deliberate?
- Is there enough whitespace?
- Are gold accents restrained?
- Does navigation feel effortless?
- Does mobile look equally premium?
- Does the site rely on real content?
- Is any component obviously template-generated?

If any answer is poor, iterate before adding more features.

---

## 26. Anti-AI Design Constraints

Do not use:

- random gradients
- purple/blue AI-style palettes
- giant glassmorphism cards
- excessive neon
- fake 3D mockups
- generic stock luxury imagery
- unnecessary floating blobs
- huge rounded rectangles around every section
- repetitive "AI landing page" section patterns

The site should communicate craftsmanship through restraint.

