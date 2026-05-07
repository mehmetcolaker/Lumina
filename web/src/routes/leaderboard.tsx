import { createFileRoute } from "@tanstack/react-router";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Reveal } from "@/components/site/Reveal";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { rankFromXp, RANKS } from "@/lib/level";
import { Trophy, Crown, Medal, Flame, Zap } from "lucide-react";

type Row = {
  id: string;
  xp: number;
  level: number;
  streak_days: number;
  completed_courses: number;
  profiles: { display_name: string | null; username: string | null; avatar_url: string | null } | null;
};

export const Route = createFileRoute("/leaderboard")({
  component: Leaderboard,
  head: () => ({
    meta: [
      { title: "Leaderboard — Lumina" },
      { name: "description", content: "See the top Lumina learners ranked by XP." },
      { property: "og:title", content: "Leaderboard — Lumina" },
    ],
  }),
});

function Leaderboard() {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const { data } = await supabase
        .from("user_stats")
        .select("id, xp, level, streak_days, completed_courses, profiles(display_name, username, avatar_url)")
        .order("xp", { ascending: false })
        .limit(50);
      setRows((data as any) ?? []);
      setLoading(false);
    })();
  }, []);

  return (
    <Layout>
      <section className="relative overflow-hidden border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="absolute -top-20 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-primary/30 blur-3xl animate-blob" />
        <div className="relative mx-auto max-w-5xl px-6 py-20 text-center">
          <Reveal><Trophy className="mx-auto h-12 w-12 text-primary animate-float" /></Reveal>
          <Reveal delay={100}>
            <h1 className="mt-4 text-5xl font-bold tracking-tight">
              <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">Leaderboard</span>
            </h1>
          </Reveal>
          <Reveal delay={200}>
            <p className="mt-3 text-lg text-muted-foreground">The brightest learners on Lumina this season.</p>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-12">
        {/* Rank tiers */}
        <Reveal>
          <h2 className="mb-6 text-xl font-bold">Ranks</h2>
          <div className="mb-12 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {RANKS.map((r, i) => (
              <Reveal key={r.name} delay={i * 60}>
                <Card className={`p-4 hover-lift bg-gradient-to-br ${r.color} text-white border-0`}>
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{r.emoji}</span>
                    <div>
                      <div className="font-bold text-lg">{r.name}</div>
                      <div className="text-xs opacity-90">{r.min.toLocaleString()}+ XP</div>
                    </div>
                  </div>
                </Card>
              </Reveal>
            ))}
          </div>
        </Reveal>

        {/* Top 3 podium */}
        {!loading && rows.length >= 3 && (
          <div className="mb-10 grid grid-cols-3 gap-4 items-end">
            {[1, 0, 2].map((idx) => {
              const r = rows[idx];
              const heights = ["h-32", "h-44", "h-24"];
              const icons = [<Medal className="h-6 w-6" />, <Crown className="h-7 w-7" />, <Medal className="h-6 w-6" />];
              const iconColors = ["text-slate-400", "text-amber-400", "text-orange-400"];
              const pos = [2, 1, 3];
              const arrIdx = idx === 1 ? 0 : idx === 0 ? 1 : 2;
              return (
                <Reveal key={r.id} delay={idx * 150}>
                  <div className="flex flex-col items-center">
                    <div className={`${iconColors[arrIdx]} animate-float`} style={{ animationDelay: `${idx * 0.3}s` }}>{icons[arrIdx]}</div>
                    <div className="mt-2 flex h-16 w-16 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-xl font-bold text-primary-foreground overflow-hidden hover-scale">
                      {r.profiles?.avatar_url ? <img src={r.profiles.avatar_url} alt="" className="h-full w-full object-cover" /> : (r.profiles?.display_name ?? "?").charAt(0).toUpperCase()}
                    </div>
                    <div className="mt-2 text-center text-sm font-semibold truncate max-w-full">{r.profiles?.display_name ?? "Anon"}</div>
                    <div className="text-xs text-primary font-bold">{r.xp.toLocaleString()} XP</div>
                    <div className={`mt-3 w-full ${heights[arrIdx]} rounded-t-lg bg-[image:var(--gradient-primary)] flex items-start justify-center pt-2 text-primary-foreground font-bold text-xl shadow-[var(--shadow-soft)]`}>
                      #{pos[arrIdx]}
                    </div>
                  </div>
                </Reveal>
              );
            })}
          </div>
        )}

        <Card className="overflow-hidden">
          <div className="divide-y divide-border">
            {loading && <div className="p-8 text-center text-muted-foreground">Loading…</div>}
            {!loading && rows.length === 0 && <div className="p-8 text-center text-muted-foreground">No learners yet — be the first!</div>}
            {rows.map((r, i) => {
              const rank = rankFromXp(r.xp);
              return (
                <Reveal key={r.id} delay={i * 30}>
                  <div className="flex items-center gap-4 p-4 transition-all hover:bg-accent/40 hover:translate-x-1">
                    <div className="w-8 text-center font-bold text-muted-foreground">{i + 1}</div>
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-sm font-bold text-primary-foreground overflow-hidden">
                      {r.profiles?.avatar_url ? <img src={r.profiles.avatar_url} alt="" className="h-full w-full object-cover" /> : (r.profiles?.display_name ?? "?").charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold truncate">{r.profiles?.display_name ?? "Anonymous learner"}</div>
                      {r.profiles?.username && <div className="text-xs text-muted-foreground">@{r.profiles.username}</div>}
                    </div>
                    <Badge className={`bg-gradient-to-r ${rank.color} text-white border-0`}>{rank.emoji} {rank.name}</Badge>
                    <div className="hidden sm:flex items-center gap-1 text-sm text-muted-foreground"><Flame className="h-4 w-4 text-orange-500" /> {r.streak_days}</div>
                    <div className="flex items-center gap-1 font-bold text-primary"><Zap className="h-4 w-4" /> {r.xp.toLocaleString()}</div>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </Card>
      </section>
    </Layout>
  );
}
