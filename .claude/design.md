# Design System Document: Artisan Editorial

## 1. Overview & Creative North Star: "The Master’s Workbench"
This design system is built to evoke the atmosphere of a high-end atelier at dusk—where traditional craftsmanship meets the quiet precision of modern tools. The "Creative North Star" is **The Master’s Workbench**: every interface element should feel like an intentional object placed on a dark, polished surface.

We break the "template" look by avoiding rigid, boxed-in grids. Instead, we utilize **intentional asymmetry**, high-contrast editorial typography, and tonal depth. Elements do not sit *on* the screen; they are layered within a physical space, creating a sense of tactile luxury and professional heritage.

## 2. Colors & Materiality
The palette is rooted in deep walnut wood tones and charcoal, punctuated by a rustic crimson that feels like a maker’s mark or a wax seal.

### Surface Hierarchy & Nesting
To achieve a premium feel, we abandon the "flat" web. Depth is created through a series of nested physical layers using the `surface-container` tiers:
* **Base Layer:** `surface` (#131313) is the workbench itself.
* **Recessed Areas:** Use `surface-container-lowest` (#0e0e0e) for input fields or inset content zones to create a "carved" effect.
* **Raised Elements:** Use `surface-container-high` (#2a2a2a) for floating cards or primary content modules.

### The "No-Line" Rule
**Explicit Instruction:** 1px solid borders are prohibited for sectioning. Boundaries must be defined solely through background color shifts. For example, a `surface-container-low` section sitting against a `surface` background provides all the definition needed. This forces a cleaner, more sophisticated "editorial" layout.

### The "Glass & Gradient" Rule
To prevent the dark theme from feeling heavy or "muddy," use Glassmorphism for floating navigation or overlays. Use `surface` colors with a 70% opacity and a `20px` backdrop-blur.
* **Signature Textures:** Main CTAs should not be flat. Apply a subtle linear gradient from `primary` (#ffb3ae) to `primary-container` (#962d2d) at a 45-degree angle to give the crimson a "metallic" or "lacquered" depth.

## 3. Typography: The Artisan’s Script
The type system creates a dialogue between the "Handmade" (Noto Serif) and the "Technical" (Inter).

* **Display & Headlines (Noto Serif):** Used for storytelling and brand authority. The high-contrast scale (e.g., `display-lg` at 3.5rem) should be used with generous leading to feel like a premium lifestyle magazine.
* **UI & Data (Inter):** Used for functionality, labels, and body copy. It represents the "precision" side of the workshop—clean, legible, and unobtrusive.
* **Hierarchy Tip:** Use `label-md` in all-caps with `0.05rem` letter-spacing for sub-headers to create a "technical spec" look that complements the serif headlines.

## 4. Elevation & Depth
We convey importance through **Tonal Layering** rather than structural lines or harsh shadows.

* **The Layering Principle:** Stack `surface-container` tiers to create natural lift. A `surface-container-highest` (#353535) card on a `surface-container-low` (#1b1b1b) section creates a sophisticated "stacked paper" effect.
* **Ambient Shadows:** If a floating effect is required (e.g., a modal), use a shadow with a `32px` blur and `8%` opacity. The shadow color must be a tinted version of the walnut tones, not a neutral grey, to maintain the warmth of the environment.
* **The "Ghost Border" Fallback:** If a border is required for accessibility in input fields, use the `outline-variant` (#574240) at a **20% opacity**. It should be felt, not seen.

## 5. Components

### Buttons
* **Primary:** A gradient of `primary` to `primary-container`. `lg` (0.5rem) rounding. Text should be `on-primary` (#66070f) and bold Inter.
* **Secondary:** No background. A "Ghost Border" (outline-variant at 20%) with `on-surface` text.
* **Tertiary:** Purely typographic with a `primary` color `label-md` weight.

### Input Fields
* **Styling:** Use `surface-container-lowest` as the background to create an "etched" look.
* **States:** On focus, the "Ghost Border" increases to 50% opacity in `primary` crimson. Never use a high-contrast glow.

### Cards & Lists
* **The Divider Rule:** Forbid the use of horizontal rules (`
`). Separate list items using `1.4rem` (spacing-4) of vertical whitespace or a subtle toggle between `surface-container-low` and `surface-container-high`.

* **Artisan Chips:** Use `secondary-container` (#5d4037) with `on-secondary-container` (#d4aca0) text for tags. They should feel like small wood-burned labels.

### Custom Component: The "Provenance Toggle"
For selection patterns, use a custom segmented control where the selected state is a `surface-bright` (#393939) pill with a subtle inner shadow, making it look like a physical switch set into the wood.

## 6. Do's and Don'ts

### Do
* **Embrace Negative Space:** Use `spacing-12` (4rem) or `spacing-16` (5.5rem) between major sections to let the "Walnut" tones breathe.
* **Asymmetric Layouts:** Offset your serif headlines. Place a large `display-md` title on the left and a small `body-md` paragraph on the right, mimicking high-end editorial print.
* **Subtle Interaction:** Hover states should be a gentle shift in surface brightness (e.g., moving from `surface-container-high` to `surface-bright`), not a color flash.

### Don't
* **Don't Use Pure Black:** It kills the "Walnut" warmth. Always use the defined `surface` (#131313).
* **Don't Box Everything:** Avoid the "grid of boxes" look. Let images and text float in relationship to each other.
* **Don't Use Default Shadows:** Standard 0.15 opacity shadows will make the dark theme look "dirty." Stick to the tinted ambient shadow rules.