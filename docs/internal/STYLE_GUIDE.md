# Consensus Agent - Style Guide

## Logo Design Concept

The "Consensus Agent" logo features a **neural weave** design representing multiple AI models (threads) converging at a central consensus point (node). The three curved paths symbolize different AI perspectives coming together.

## Color Palette

### Logo Elements

| Element | Color | Hex Values | Notes |
|---------|-------|------------|--------|
| Thread 1 | Gradient: Teal → Cyan | `#00C9A7` → `#00FFFF` | Left-most curved path |
| Thread 2 | Gradient: Blue → Azure | `#0057FF` → `#00BFFF` | Right-most curved path |
| Thread 3 | Gradient: Green → Blue | `#00FF88` → `#0077FF` | Bottom/center-weaving path |
| Central Node | Soft Glow: Light Blue | `#B0F6FF` with `#00FFFF` border | Outer glow (blur radius 8–12px) |

### Application Colors

| Usage | Color | Hex Value | Implementation |
|-------|-------|-----------|----------------|
| Primary Background (dark) | Dark Navy | `#0D1B2A` | Main app background |
| Secondary Background (dark) | Darker Navy | `#0B0F1A` | Cards, modals, sidebars |
| Primary Background (light) | Light Blue | `#F5F9FF` | Optional light mode |
| Secondary Background (light) | White | `#FFFFFF` | Light mode cards |
| Primary Accent | Teal | `#00C9A7` | Buttons, links, active states |
| Secondary Accent | Cyan | `#00FFFF` | Highlights, notifications |
| Tertiary Accent | Azure Blue | `#00BFFF` | Secondary buttons, borders |

### CSS Custom Properties

```css
:root {
  /* Primary gradient colors */
  --primary-teal: #00C9A7;
  --primary-cyan: #00FFFF;
  --primary-blue: #0057FF;
  --primary-azure: #00BFFF;
  --primary-green: #00FF88;
  --primary-light-blue: #0077FF;
  
  /* Central node colors */
  --accent-light-blue: #B0F6FF;
  --accent-cyan: #00FFFF;
  
  /* Background colors */
  --bg-dark: #0D1B2A;
  --bg-dark-secondary: #0B0F1A;
  --bg-light: #F5F9FF;
  --bg-light-secondary: #FFFFFF;
}
Typography

## Logo Typography & Lockups

**"Lockups"** refer to specific arrangements of the logo emblem and text. The Consensus Agent brand requires these three versions:

### Font Specifications
- **Font Family**: Tech-forward geometric sans-serif
- **Recommended**: Space Grotesk, Orbitron, Inter, or Aeonik Mono
- **Weight**: Medium to Bold
- **Letter spacing**: Tight but readable (kerning tuned for logo lockup)
- **Casing**: ALL CAPS for "CONSENSUS AGENT"

### Logo Lockup Variations

1. **Vertical (Stacked) Lockup**
   - Emblem positioned above text
   - Text placement: Directly below emblem, center-aligned
   - Use for: App icons, loading screens, headers

2. **Horizontal Lockup**
   - Emblem positioned left, text right
   - Text placement: Right-aligned to emblem
   - Use for: Navigation bars, footers, business cards

3. **Icon-Only Lockup**
   - Just the neural weave emblem without text
   - Use for: Favicons, app icons (32x32px), compact spaces

## Application Typography

### Recommended Font Stack
```css
font-family: 'Inter', 'Space Grotesk', 'Segoe UI', system-ui, sans-serif;
```

### Text Hierarchy

- **Headings**: Bold weight, increased letter-spacing
- **Body Text**: Regular to Medium weight
- **UI Elements**: Medium weight, tight letter-spacing
- **Code/Monospace**: 'JetBrains Mono', 'Fira Code', monospace

## Style Direction

### Visual Design Principles

**Visual Tone**: Minimal, elegant, sleek — no literal faces or human forms

**Mood**: Clean sophistication with sci-fi undertone

**Primary Theme**: Dark mode with the neural weave color palette

### What to Avoid

- Cluttered mesh patterns
- Robotic arms or mechanical imagery  
- Overlapping spirals
- Organic leaf-like tendrils
- Overly complex animations

### Design Recommendations

#### For Chat Interface

- **Background**: Use dark navy (`#0D1B2A`) as primary background
- **Message Bubbles**: Subtle gradients using thread colors
- **Active States**: Soft cyan glow (`#00FFFF`) for interactive elements
- **Typing Indicators**: Animated using the gradient colors

#### For Buttons & Interactive Elements

- **Primary Buttons**: Teal to cyan gradient (`#00C9A7` → `#00FFFF`)
- **Secondary Buttons**: Blue to azure gradient (`#0057FF` → `#00BFFF`)
- **Hover Effects**: Soft glow similar to central node
- **Focus States**: Cyan border with subtle shadow

#### Animation Guidelines (OPTIONAL ONLY IF TIME IS AVAILABLE IMPLEMENT LAST)

- **Subtle Only**: Threads could "weave" together or pulse toward center on hover/load
- **Performance**: Keep animations lightweight and optional
- **Accessibility**: Respect prefers-reduced-motion settings

## Implementation Guidelines

### Usability Requirements

**Scalability**: Icon must scale clearly to 32x32px (app icon, favicon)

**Contrast**: Central orb must remain visually distinct even at small sizes

**Accessibility**: Maintain WCAG AA contrast ratios with text

### Required Logo Deliverables

1. **Vertical (stacked)**: Logo lockup for headers and loading screens
2. **Horizontal (icon + text inline)**: Navigation and footer usage  
3. **Icon-only (for compact use)**: Favicon and app icon formats

### File Formats Needed

- **SVG**: Vector format for web (current)
- **PNG**: High-res versions (512x512, 256x256, 128x128, 64x64, 32x32)
- **ICO**: Windows favicon format
- **ICNS**: macOS app icon format
