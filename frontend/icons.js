/*
 * Streetline icon set.
 * Hand-drawn pictograms in a road-sign/stencil style: thick strokes, no fill
 * except small accents, rounded joins. Deliberately simple geometry (mostly
 * circles, rects and straight segments) so every icon renders reliably at
 * small sizes without relying on fragile hand-tuned bezier curves.
 *
 * Usage: icon('pothole', 'icon icon--lg')  -> returns an <svg>...</svg> string
 */

const ICON_PATHS = {
  pothole: `
    <ellipse cx="12" cy="13" rx="7" ry="4"/>
    <path d="M7.5 12.5l2-1.8M11.5 9.8l1.3-1.8M14.5 11.5l2-1"/>
    <path d="M2.5 19.5c3.5-1.4 15.5-1.4 19 0" stroke-dasharray="1 3"/>
  `,
  garbage: `
    <path d="M5 7h14l-1.2 13a2 2 0 0 1-2 1.8H8.2a2 2 0 0 1-2-1.8L5 7z"/>
    <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>
    <path d="M3 7h18"/>
    <path d="M10 11v7M14 11v7"/>
  `,
  streetlight: `
    <path d="M12 22V9.2"/>
    <path d="M8 22h8"/>
    <path d="M12 9.2c-3 0-5.3-1.7-5.3-4.3C6.7 2.6 9.1 1 12 1s5.3 1.6 5.3 3.9"/>
    <path d="M8.8 4l2 2-1.3 1.8 2.3-1"/>
  `,
  water: `
    <path d="M6 4.5h7.5l2 3H18v3h-2.5"/>
    <path d="M12 10.3s-3.3 4.3-3.3 7a3.3 3.3 0 0 0 6.6 0c0-2.7-3.3-7-3.3-7z"/>
  `,
  camera: `
    <path d="M4 8h3l2-2h6l2 2h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/>
    <circle cx="12" cy="13" r="3.4"/>
  `,
  pin: `
    <path d="M12 21s-7-7.1-7-12a7 7 0 0 1 14 0c0 4.9-7 12-7 12z"/>
    <circle cx="12" cy="9" r="2.3"/>
  `,
  mail: `
    <rect x="3" y="5" width="18" height="14" rx="1.5"/>
    <path d="M3 6.5l9 6.5 9-6.5"/>
  `,
  check: `
    <circle cx="12" cy="12" r="9"/>
    <path d="M8 12.4l2.6 2.6L16 9.4"/>
  `,
  flag: `
    <path d="M5 21V4"/>
    <path d="M5 4h13l-3 4 3 4H5"/>
  `,
  clipboard: `
    <rect x="5" y="4" width="14" height="17" rx="1.5"/>
    <rect x="9" y="2.3" width="6" height="3.2" rx="1"/>
    <path d="M8.5 11.5h7M8.5 15.3h7"/>
  `,
  wrench: `
    <path d="M14.7 6.3a4 4 0 0 0-5.4 5l-6 6 2.4 2.4 6-6a4 4 0 0 0 5-5.4l-2.6 2.6-2-2z"/>
  `,
  warning: `
    <path d="M12 3l10 18H2L12 3z"/>
    <path d="M12 10v4"/>
    <circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="none"/>
  `,
  map: `
    <path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/>
    <path d="M9 4v14M15 6v14"/>
  `,
  chart: `
    <path d="M4 20V11"/>
    <path d="M12 20V4"/>
    <path d="M20 20v-7"/>
    <path d="M2 20h20"/>
  `,
  refresh: `
    <path d="M20 11A8 8 0 1 0 19 15"/>
    <path d="M20 5v6h-6"/>
  `,
  upload: `
    <path d="M12 16V5"/>
    <path d="M7.5 9.5L12 5l4.5 4.5"/>
    <path d="M4 16.5v2A2.5 2.5 0 0 0 6.5 21h11a2.5 2.5 0 0 0 2.5-2.5v-2"/>
  `,
};

function icon(name, className) {
  const body = ICON_PATHS[name] || '';
  const cls = className ? ` class="${className}"` : '';
  return `<svg${cls} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;
}

// Fill every <span data-icon="name" data-icon-class="..."></span> on the page.
function hydrateIcons(root) {
  (root || document).querySelectorAll('[data-icon]').forEach((el) => {
    const name = el.getAttribute('data-icon');
    const cls = el.getAttribute('data-icon-class') || 'icon';
    el.innerHTML = icon(name, cls);
  });
}

document.addEventListener('DOMContentLoaded', () => hydrateIcons(document));
