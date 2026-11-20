type Props = { name: string; size?: number };
const paths: Record<string, string> = {
  grid: 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z',
  file: 'M6 3h8l4 4v14H6zM14 3v5h5M9 13h6M9 17h5',
  upload: 'M12 16V4m0 0L8 8m4-4 4 4M5 15v4h14v-4',
  shield: 'M12 3 20 6v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6zM9 12l2 2 4-4',
  scale: 'M12 4v16M5 7h14M5 7l-3 6a3 3 0 0 0 6 0zm14 0-3 6a3 3 0 0 0 6 0zM8 20h8',
  chat: 'M5 5h14v10H9l-4 4zM8 9h8M8 12h5',
  check: 'm5 12 4 4L19 6',
  users: 'M16 20v-1a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v1M9.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm7-7a4 4 0 0 1 0 7.7M21 20v-1a4 4 0 0 0-3-3.9',
  bell: 'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4',
  search: 'm21 21-4.4-4.4M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15z',
  arrow: 'M5 12h14m-6-6 6 6-6 6',
  dots: 'M6 12h.01M12 12h.01M18 12h.01',
  calendar: 'M5 4h14v16H5zM8 2v4m8-4v4M5 9h14',
};
export default function Icon({ name, size = 18 }: Props) { return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name] ?? paths.file} /></svg>; }
