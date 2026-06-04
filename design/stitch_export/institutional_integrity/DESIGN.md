---
name: Institutional Integrity
colors:
  surface: '#f8faf8'
  surface-dim: '#d8dad9'
  surface-bright: '#f8faf8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f2'
  surface-container: '#eceeec'
  surface-container-high: '#e6e9e7'
  surface-container-highest: '#e1e3e1'
  on-surface: '#191c1b'
  on-surface-variant: '#3f4944'
  inverse-surface: '#2e3130'
  inverse-on-surface: '#eff1ef'
  outline: '#6f7974'
  outline-variant: '#bfc9c2'
  surface-tint: '#226a53'
  primary: '#004331'
  on-primary: '#ffffff'
  primary-container: '#0e5c46'
  on-primary-container: '#8cd2b6'
  inverse-primary: '#8fd5b8'
  secondary: '#8a5100'
  on-secondary: '#ffffff'
  secondary-container: '#feb15f'
  on-secondary-container: '#744300'
  tertiary: '#2a3e38'
  on-tertiary: '#ffffff'
  tertiary-container: '#41554f'
  on-tertiary-container: '#b2c9c1'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#aaf1d4'
  primary-fixed-dim: '#8fd5b8'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513c'
  secondary-fixed: '#ffdcbd'
  secondary-fixed-dim: '#ffb86f'
  on-secondary-fixed: '#2c1600'
  on-secondary-fixed-variant: '#693c00'
  tertiary-fixed: '#d1e8df'
  tertiary-fixed-dim: '#b5cbc3'
  on-tertiary-fixed: '#0b1f1a'
  on-tertiary-fixed-variant: '#374b45'
  background: '#f8faf8'
  on-background: '#191c1b'
  surface-variant: '#e1e3e1'
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 48px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is engineered to function as a digital court-of-record for Zambian civic oversight. It prioritizes **Institutional Trust**, **Cryptographic Transparency**, and **Administrative Authority**. The aesthetic moves away from ephemeral SaaS trends toward a "Digital Monument" style—grounded, permanent, and unassailable.

The target audience includes Zambian citizens, local auditors, and international transparency watchdogs. The emotional response must be one of absolute clarity and reliability.

**Design Style: Modern Institutional**
- **Symmetry & Structure:** Layouts are balanced and strictly aligned to convey order.
- **Data-First Credibility:** Information is presented with academic precision, using monospaced accents to signal "on-chain" or ledger-based veracity.
- **Editorial Weight:** Large, clean typography paired with generous whitespace suggests a high-value document rather than a cluttered dashboard.
- **Zero Decoration:** No gradients, no emojis, and no illustrative fluff. Every visual element must serve a functional or communicative purpose.

## Colors

The palette is derived from the national identity of Zambia, tuned for high-legibility digital interfaces.

- **Integrity Green (#0E5C46):** The primary color, used for headers, primary actions, and brand reinforcement. It symbolizes growth and government stability.
- **Eagle Copper (#B8762A):** Reserved for "Verification" moments, seals, and high-level highlights. It represents the wealth of the nation and the value of the audit.
- **Near-Black Ink (#0B1F1A):** Used for the sidebar and primary text. It provides a deeper contrast than standard grays, feeling more authoritative and permanent.
- **Risk Scale:** 
    - **Green (0-39):** Low risk, high transparency.
    - **Amber (40-69):** Cautionary, requires attention.
    - **Red (70-100):** High risk, immediate audit required.

## Typography

Typography establishes the hierarchy of truth. 

- **Space Grotesk** is used for all major headings. Its geometric, slightly technical character feels contemporary yet civic.
- **Inter** provides the backbone for the body copy, ensuring high legibility for long-form reports and project descriptions.
- **JetBrains Mono** is the signature font for data integrity. Use it for transaction IDs, ledger hashes, currency amounts, and technical metadata. This creates a visual "signature" of cryptographic trust.

## Layout & Spacing

This design system utilizes a **12-column fixed grid** for desktop, centered within the viewport to maintain an editorial feel. 

- **Sidebar:** A fixed-width 280px sidebar in "Near-Black Ink" anchors the navigation on the left.
- **Content Area:** Uses 48px padding on desktop to allow the data to "breathe."
- **Mobile Reflow:** On mobile devices, the 12-column grid collapses to a single-column stack with 16px horizontal margins. 
- **Rhythm:** Vertical spacing follows an 8px base unit. Section headers should be separated from content by 32px (`stack-lg`) to maintain clear thematic grouping.

## Elevation & Depth

To maintain an institutional feel, the system avoids dramatic shadows or floating effects.

- **Flat Surfaces:** The primary background is `#F6F8F6`.
- **Tonal Layering:** Main content containers are pure white cards with a subtle 1px border (#E2E8E2) instead of heavy shadows.
- **Soft Shadows:** Only used on active elements like open modals or dropdowns. Shadows should be ultra-diffused: `0 4px 20px rgba(11, 31, 26, 0.05)`.
- **Interactive Depth:** On hover, buttons and cards may shift slightly in background color (tonal shift) rather than "lifting" off the page.

## Shapes

The design system uses a consistent **12px (0.75rem)** corner radius for all primary UI components (cards, buttons, input fields). This "Rounded" setting balances the coldness of monospaced data with an approachable, modern civic feel.

- **Small elements** (chips, checkboxes): 4px radius.
- **Large containers** (main cards): 12px radius.
- **Special Case:** The "Verification Seal" is always a perfect circle.

## Components

### Verification Seal (Signature Component)
A circular emblem with a thin Copper (#B8762A) border.
- **Center:** The Zambian Coat of Arms (simplified/monochrome copper).
- **Outer Ring:** Text "VERIFIED ON LEDGER • REPUBLIC OF ZAMBIA" in 10px Inter Bold Caps.
- **Bottom/Detail:** A small JetBrains Mono string showing the last 8 characters of the block hash.

### Buttons
- **Primary:** Solid Integrity Green (#0E5C46) with white text. 12px radius.
- **Secondary:** Transparent with 1px Copper border and Copper text.
- **Ghost:** Near-Black Ink text, no border, used for utility actions.

### Cards & Lists
- **Audit Cards:** White background, 12px radius, 1px border. 
- **Project Lists:** Zebra-striping using the background color (#F6F8F6) for even rows to maintain readability in high-density data views.

### Input Fields
- **Style:** 1px border (#0B1F1A at 20% opacity), white background.
- **Focus:** 2px solid Integrity Green border.
- **Labels:** Always external, never use placeholder-only labels.

### Risk Indicators
- Use a **Progress Bar** or **Gauge** component.
- The bar color must dynamically shift based on the 0-100 scale (Green -> Amber -> Red).
- Always accompany the color with the numerical score in JetBrains Mono to ensure accessibility.