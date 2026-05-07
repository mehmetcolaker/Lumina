import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/site/Reveal";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { progressToNextLevel, rankFromXp } from "@/lib/level";
import { COURSES } from "@/lib/courses";
import { Zap, Flame, Trophy, BookOpen, Target, TrendingUp } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
  head: () => ({ meta: [{ title: "Dashboard — Lumina" }] }),
});

function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<{ xp: number; level: number; streak_days: number; completed_courses: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) navigate({ to: "/login" });
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (!user) return;
    (async () => {
      const { data } = await supabase.from("user_stats").select("*").eq("id", user.id).maybeSingle();
      setStats(data ?? { xp: 0, level: 1, streak_days: 0, completed_courses: 0 });
      setLoading(false);
    })();
  }, [user]);

  if (authLoading || loading || !stats) return <Layout><div className="p-12 text-center text-muted-foreground">Loading…</div></Layout>;

  const prog = progressToNextLevel(stats.xp);
  const rank = rankFromXp(stats.xp);
  const recommended = COURSES.slice(0, 3);

  return (
    <Layout>
      <section className="relative overflow-hidden border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="absolute -top-20 -right-20 h-72 w-72 rounded-full bg-primary/30 blur-3xl animate-blob" />
        <div className="relative mx-auto max-w-6xl px-6 py-12">
          <Reveal>
            <p className="text-sm text-muted-foreground">Welcome back,</p>
            <h1 className="text-4xl font-bold">{user?.email?.split("@")[0]} 👋</h1>
          </Reveal>

          <Reveal delay={100}>
            <Card className="mt-8 p-6 hover-lift">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <Badge className={`bg-gradient-to-r ${rank.color} text-white border-0 text-sm`}>{rank.emoji} {rank.name}</Badge>
                  <div className="mt-2 text-3xl font-bold">Level {prog.level}</div>
                  <div className="text-sm text-muted-foreground">{stats.xp.toLocaleString()} XP total</div>
                </div>
                <div className="flex-1 min-w-[200px] max-w-md">
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>Level {prog.level}</span>
                    <span>{prog.current}/{prog.needed} XP</span>
                    <span>Level {prog.level + 1}</span>
                  </div>
                  <div className="h-3 w-full overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-[image:var(--gradient-primary)] transition-all duration-1000 animate-shimmer bg-gradient-to-r from-primary via-primary-foreground/30 to-primary"
                      style={{ width: `${prog.percent}%` }}
                    />
                  </div>
                </div>
              </div>
            </Card>
          </Reveal>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: Zap, label: "Total XP", value: stats.xp.toLocaleString(), color: "text-primary" },
              { icon: Flame, label: "Day streak", value: stats.streak_days, color: "text-orange-500" },
              { icon: BookOpen, label: "Courses done", value: stats.completed_courses, color: "text-emerald-500" },
              { icon: Trophy, label: "Rank", value: rank.name, color: "text-amber-500" },
            ].map((s, i) => (
              <Reveal key={s.label} delay={i * 80}>
                <Card className="p-5 hover-lift glow-on-hover">
                  <s.icon className={`h-6 w-6 ${s.color}`} />
                  <div className="mt-3 text-2xl font-bold">{s.value}</div>
                  <div className="text-xs text-muted-foreground">{s.label}</div>
                </Card>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-12">
        <Reveal>
          <h2 className="text-2xl font-bold flex items-center gap-2"><Target className="h-5 w-5 text-primary" /> Recommended for you</h2>
        </Reveal>
        <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {recommended.map((c, i) => (
            <Reveal key={c.slug} delay={i * 80}>
              <Link to="/courses/$slug" params={{ slug: c.slug }}>
                <Card className="p-6 hover-lift cursor-pointer group h-full">
                  <Badge variant="outline">{c.tag}</Badge>
                  <h3 className="mt-3 text-lg font-semibold group-hover:text-primary transition-colors">{c.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground line-clamp-2">{c.desc}</p>
                  <div className="mt-4 flex items-center gap-1 text-sm text-primary font-medium">
                    <TrendingUp className="h-4 w-4" /> +{c.xp} XP
                  </div>
                </Card>
              </Link>
            </Reveal>
          ))}
        </div>

        <Reveal delay={200}>
          <div className="mt-10 flex gap-3">
            <Button asChild className="bg-[image:var(--gradient-primary)] text-primary-foreground glow-on-hover">
              <Link to="/courses">Browse all courses</Link>
            </Button>
            <Button asChild variant="outline" className="hover-scale">
              <Link to="/leaderboard">View leaderboard</Link>
            </Button>
          </div>
        </Reveal>
      </section>
    </Layout>
  );
}
