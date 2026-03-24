'use client';

const SORT_OPTIONS = [
  { value: 'recent', label: 'All' },
  { value: 'hot', label: 'Hot debates' },
  { value: 'endorsed', label: 'Most endorsed' },
];

export function LensFilter({ communities, activeSort, activeLens, onSortChange, onLensChange }: {
  communities: { name: string; displayName: string }[];
  activeSort: string; activeLens: string | null;
  onSortChange: (sort: string) => void; onLensChange: (lens: string | null) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2 mb-6">
      {SORT_OPTIONS.map(opt => (
        <button key={opt.value} onClick={() => { onSortChange(opt.value); onLensChange(null); }}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            activeSort === opt.value && !activeLens ? 'bg-orange-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}>{opt.label}</button>
      ))}
      <span className="text-slate-600 text-xs">|</span>
      {communities.filter(c => c.name !== 'sos-design').map(c => (
        <button key={c.name} onClick={() => { onLensChange(c.name); onSortChange('recent'); }}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            activeLens === c.name ? 'bg-orange-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}>{c.displayName}</button>
      ))}
    </div>
  );
}
