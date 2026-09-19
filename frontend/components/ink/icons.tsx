/* Thin Lucide-style line icons for the ink shell (17–19px). */

function base(props: { children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      {props.children}
    </svg>
  );
}

export const I = {
  home: () => base({ children: (<><path d="M3 10.5 12 3l9 7.5" /><path d="M5 9.5V21h14V9.5" /></>) }),
  briefcase: () => base({ children: (<><rect x="2.5" y="7" width="19" height="13" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M2.5 12.5h19" /></>) }),
  bolt: () => base({ children: <path d="M13 2 4.5 13.5H11L10 22l8.5-11.5H12L13 2z" /> }),
  target: () => base({ children: (<><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1" /></>) }),
  spark: () => base({ children: (<><path d="M12 3l1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3z" /><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15z" /></>) }),
  building: () => base({ children: (<><rect x="4" y="3" width="16" height="18" rx="1.5" /><path d="M9 21v-4h6v4M8 7.5h2M14 7.5h2M8 11h2M14 11h2M8 14.5h2M14 14.5h2" /></>) }),
  sliders: () => base({ children: (<><path d="M4 7h9M17 7h3M4 17h3M11 17h9" /><circle cx="15" cy="7" r="2.2" /><circle cx="9" cy="17" r="2.2" /></>) }),
  bell: () => base({ children: (<><path d="M18 9a6 6 0 1 0-12 0c0 6-2.5 7-2.5 7h17S18 15 18 9" /><path d="M10 20a2.2 2.2 0 0 0 4 0" /></>) }),
  card: () => base({ children: (<><rect x="2.5" y="5.5" width="19" height="13" rx="2" /><path d="M2.5 10h19M6 15h4" /></>) }),
  grid: () => base({ children: (<><rect x="3" y="3" width="8" height="8" rx="1.5" /><rect x="13" y="3" width="8" height="8" rx="1.5" /><rect x="3" y="13" width="8" height="8" rx="1.5" /><rect x="13" y="13" width="8" height="8" rx="1.5" /></>) }),
  users: () => base({ children: (<><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0" /><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M17.5 14.2a6.5 6.5 0 0 1 4 5.8" /></>) }),
  tag: () => base({ children: (<><path d="M20 12.5 12.5 20a1.5 1.5 0 0 1-2 0L3 12.5V3h9.5l7.5 7.5a1.5 1.5 0 0 1 0 2z" /><circle cx="8" cy="8" r="1.4" /></>) }),
  list: () => base({ children: (<><path d="M8 6h13M8 12h13M8 18h13" /><circle cx="4" cy="6" r="1" /><circle cx="4" cy="12" r="1" /><circle cx="4" cy="18" r="1" /></>) }),
  db: () => base({ children: (<><ellipse cx="12" cy="5.5" rx="8" ry="2.8" /><path d="M4 5.5v13c0 1.5 3.6 2.8 8 2.8s8-1.3 8-2.8v-13" /><path d="M4 12c0 1.5 3.6 2.8 8 2.8s8-1.3 8-2.8" /></>) }),
  clock: () => base({ children: (<><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3.5 2" /></>) }),
  play: () => base({ children: (<><circle cx="12" cy="12" r="9" /><path d="M10 8.5l6 3.5-6 3.5v-7z" /></>) }),
  gauge: () => base({ children: (<><path d="M4 14a8 8 0 1 1 16 0" /><path d="M12 14l4-4" /><path d="M4 18h16" /></>) }),
  gear: () => base({ children: (<><circle cx="12" cy="12" r="3" /><path d="M19 12a7 7 0 0 0-.15-1.4l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2.4-1.4L13.7 2h-3.4l-.45 2.6a7 7 0 0 0-2.4 1.4l-2.3-1-2 3.4 2 1.5a7 7 0 0 0 0 2.8l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2.4 1.4l.45 2.6h3.4l.45-2.6a7 7 0 0 0 2.4-1.4l2.3 1 2-3.4-2-1.5c.1-.45.15-.92.15-1.4z" /></>) }),
  logout: () => base({ children: (<><path d="M9 21H5a1.5 1.5 0 0 1-1.5-1.5v-15A1.5 1.5 0 0 1 5 3h4" /><path d="M15 16l4-4-4-4M19 12H9" /></>) }),
  search: () => base({ children: (<><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.8-3.8" /></>) }),
  calendar: () => base({ children: (<><rect x="3" y="4.5" width="18" height="17" rx="2" /><path d="M8 2.5v4M16 2.5v4M3 10h18" /></>) }),
  sun: () => base({ children: (<><circle cx="12" cy="12" r="4" /><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M19.1 4.9l-1.8 1.8M6.7 17.3l-1.8 1.8" /></>) }),
  pin: () => base({ children: (<><path d="M12 21s-6.5-5.4-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.6 12 21 12 21z" /><circle cx="12" cy="10.5" r="2.3" /></>) }),
  bookmark: () => base({ children: <path d="M6.5 3.5h11a1 1 0 0 1 1 1V21l-6.5-4-6.5 4V4.5a1 1 0 0 1 1-1z" /> }),
  check: () => base({ children: (<><rect x="3" y="3" width="18" height="18" rx="4" /><path d="M8 12.5l2.7 2.7L16.5 9" /></>) }),
  trend: () => base({ children: (<><path d="M3 17l6-6 4 4 8-8" /><path d="M15 7h6v6" /></>) }),
};
