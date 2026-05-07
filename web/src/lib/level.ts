export const RANKS = [
  { name: "Spark", min: 0, color: "from-sky-300 to-sky-400", emoji: "✨" },
  { name: "Glow", min: 500, color: "from-sky-400 to-blue-500", emoji: "🌟" },
  { name: "Beam", min: 1500, color: "from-blue-500 to-indigo-500", emoji: "💫" },
  { name: "Radiant", min: 3500, color: "from-indigo-500 to-purple-500", emoji: "🔮" },
  { name: "Luminary", min: 7500, color: "from-purple-500 to-pink-500", emoji: "👑" },
  { name: "Stellar", min: 15000, color: "from-amber-400 to-rose-500", emoji: "🚀" },
];

export function levelFromXp(xp: number) {
  // 100 xp per level, scaling
  return Math.floor(0.5 * (1 + Math.sqrt(1 + xp / 25)));
}

export function xpForLevel(level: number) {
  return 25 * level * (level - 1);
}

export function rankFromXp(xp: number) {
  let current = RANKS[0];
  for (const r of RANKS) if (xp >= r.min) current = r;
  return current;
}

export function progressToNextLevel(xp: number) {
  const lvl = levelFromXp(xp);
  const cur = xpForLevel(lvl);
  const next = xpForLevel(lvl + 1);
  return { level: lvl, current: xp - cur, needed: next - cur, percent: Math.min(100, ((xp - cur) / (next - cur)) * 100) };
}
