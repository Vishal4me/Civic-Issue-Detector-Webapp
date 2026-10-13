/*
 * NagarMitra icon set.
 * The four issue-category pictograms are full-color (fixed palette, not
 * currentColor) so they stay colorful and distinct everywhere they're
 * used — on a dark hero sign, inside a gradient chip, or on their own.
 * The remaining UI/chrome icons stay as simple currentColor outlines so
 * they always match surrounding text.
 *
 * Usage: icon('pothole', 'icon icon--lg')  -> returns an <svg>...</svg> string
 */

const ICON_PATHS = {
  pothole: `
    <ellipse cx="12" cy="14.5" rx="9" ry="3.6" fill="none" stroke="#FF7A59" stroke-width="1.4" stroke-dasharray="2.2 2.4"/>
    <ellipse cx="12" cy="14.5" rx="7.4" ry="3.4" fill="#2b2b2f" stroke="#B8231A" stroke-width="1.2"/>
    <ellipse cx="10.4" cy="13.4" rx="2.4" ry="1.1" fill="#45454c"/>
    <path d="M8 13.6l1.8-1.6M11.2 11.1l1.1-1.6M13.6 12.7l1.8-0.9" stroke="#FFB300" stroke-width="1.1" fill="none" stroke-linecap="round"/>
    <path d="M18 5.2l1.2 2.4h2.5l-2 1.7.8 2.5-2.5-1.5-2.5 1.5.8-2.5-2-1.7h2.5z" fill="#FFB300"/>
  `,
  garbage: `
    <path d="M5 8h14l-1.2 12.5a2 2 0 0 1-2 1.8H8.2a2 2 0 0 1-2-1.8L5 8z" fill="#2FAE4E" stroke="#1B7A37" stroke-width="1.2"/>
    <path d="M9 8V5.6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2V8" fill="none" stroke="#1B7A37" stroke-width="1.4"/>
    <path d="M3 8h18" stroke="#1B7A37" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M10 12v6.5M14 12v6.5" stroke="#DFF6E2" stroke-width="1.3" stroke-linecap="round"/>
    <circle cx="8.6" cy="5.3" r="1.7" fill="#E8402F"/>
    <rect x="13" y="3.6" width="3.2" height="2.6" rx="0.5" transform="rotate(10 14.6 4.9)" fill="#FFD54F"/>
    <path d="M10.3 5.6l2.2-2.6 2 1.4-1.8 2.8z" fill="#1E88E5"/>
  `,
  streetlight: `
    <path d="M12 22V9.6" stroke="#6b6f76" stroke-width="2.1" stroke-linecap="round"/>
    <path d="M8.2 22h7.6" stroke="#6b6f76" stroke-width="2.1" stroke-linecap="round"/>
    <circle cx="12" cy="5.6" r="5.4" fill="#FFD54F" opacity="0.35"/>
    <path d="M12 9.6c-2.8 0-5-1.5-5-3.8S9.2 1.4 12 1.4s5 1.6 5 3.6" fill="none" stroke="#424242" stroke-width="1.8" stroke-linecap="round"/>
    <circle cx="12" cy="5.4" r="2.5" fill="#FFC107" stroke="#E6690C" stroke-width="0.6"/>
    <path d="M12 0.4v1.4M16.8 2.3l-1 1.2M7.2 2.3l1 1.2M18.4 5.6h-1.5M5.6 5.6h1.5" stroke="#FFC107" stroke-width="1.1" stroke-linecap="round"/>
  `,
  water: `
    <path d="M5.5 5h7l1.7 2.6H18v2.8h-2.3" fill="none" stroke="#90A4AE" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="16.2" cy="9.6" r="1.15" fill="#4FC3F7"/>
    <path d="M12 10.6s-4 4.9-4 7.8a4 4 0 0 0 8 0c0-2.9-4-7.8-4-7.8z" fill="#1E88E5" stroke="#0D5FA8" stroke-width="1"/>
    <ellipse cx="10.3" cy="16.4" rx="1" ry="1.9" fill="#8BD4FF" opacity="0.85"/>
    <circle cx="12.5" cy="21.2" r="0.9" fill="#6EC6FF" opacity="0.8"/>
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
