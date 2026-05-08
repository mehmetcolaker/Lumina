import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/site/Reveal";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { CourseResponse, LeaderboardResponse, SubmissionStatusResponse } from "@/lib/api-types";
import { progressToNextLevel, rankFromXp } from "@/lib/level";
import { slugify } from "@/lib/courses";
import { Zap, Flame, Trophy, BookOpen, Target, TrendingUp, History, Terminal, CheckCircle, XCircle, Clock } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
  head: () => ({ meta: [{ title: "Dashboard — Lumina" }] }),
});

function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!authLoading && !user) navigate({ to: "/login" });
  }, [user, authLoading, navigate]);

  // Pull XP/rank from the public leaderboard (which already aggregates UserStats)
  const { data: leaderboard } = useQuery<LeaderboardResponse>({
    queryKey: ["leaderboard", "dashboard"],
    queryFn: () => api.get<LeaderboardResponse>("/gamification/leaderboard?limit=100"),
    enabled: !!user,
  });

  // Recommended courses
  const { data: courses } = useQuery<CourseResponse[]>({
    queryKey: ["courses"],
    queryFn: () => api.get<CourseResponse[]>("/courses/"),
    enabled: !!user,
  });

  // Recent submissions
  const { data: recentSubs } = useQuery<SubmissionStatusResponse[]>({
    queryKey: ["recent-submissions"],
    queryFn: () => api.get<SubmissionStatusResponse[]>("/execution/all-submissions?limit=5"),
    enabled: !!user,
    refetchInterval: 30_000,
  });

  if (authLoading) {
    return (
      <Layout>
        <div className="p-12 text-center text-muted-foreground">Loading…</div>
      </Layout>
    );
  }
  if (!user) return null;

  const myEntry = leaderboard?.entries.find((e) => e.user_id === user.id);
  const xp = myEntry?.total_xp ?? 0;
  const myRank = myEntry?.rank ?? null;

  const prog = progressToNextLevel(xp);
  const rank = rankFromXp(xp);
  const recommended = (courses ?? []).slice(0, 3);

  return (
    <Layout>
      <section className="relative overflow-hidden border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="absolute -top-20 -right-20 h-72 w-72 rounded-full bg-primary/30 blur-3xl animate-blob" />
        <div className="relative mx-auto max-w-6xl px-6 py-12">
          <Reveal>
            <p className="text-sm text-muted-foreground">Welcome back,</p>
            <h1 className="text-4xl font-bold">{user.email.split("@")[0]} 👋</h1>
          </Reveal>

          <Reveal delay={100}>
            <Card className="mt-8 p-6 hover-lift">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <Badge
                    className={`bg-gradient-to-r ${rank.color} text-white border-0 text-sm`}
                  >
                    {rank.emoji} {rank.name}
                  </Badge>
                  <div className="mt-2 text-3xl font-bold">Level {prog.level}</div>
                  <div className="text-sm text-muted-foreground">
                    {xp.toLocaleString()} XP total
                  </div>
                </div>
                <div className="flex-1 min-w-[200px] max-w-md">
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>Level {prog.level}</span>
                    <span>
                      {prog.current}/{prog.needed} XP
                    </span>
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
              {
                icon: Zap,
                label: "Total XP",
                value: xp.toLocaleString(),
                color: "text-primary",
              },
              {
                icon: Flame,
                label: "Leaderboard rank",
                value: myRank ? `#${myRank}` : "—",
                color: "text-orange-500",
              },
              {
                icon: BookOpen,
                label: "Courses available",
                value: courses?.length ?? 0,
                color: "text-emerald-500",
              },
              {
                icon: Trophy,
                label: "Rank",
                value: rank.name,
                color: "text-amber-500",
              },
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
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" /> Recommended for you
          </h2>
        </Reveal>
        <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {recommended.map((c, i) => (
            <Reveal key={c.id} delay={i * 80}>
              <Link to="/courses/$slug" params={{ slug: slugify(c.title) }}>
                <Card className="p-6 hover-lift cursor-pointer group h-full">
                  <Badge variant="outline">{c.language}</Badge>
                  <h3 className="mt-3 text-lg font-semibold group-hover:text-primary transition-colors">
                    {c.title}
                  </h3>
                  <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                    {c.description ?? "Interactive coding course."}
                  </p>
                  <div className="mt-4 flex items-center gap-1 text-sm text-primary font-medium">
                    <TrendingUp className="h-4 w-4" /> Start now
                  </div>
                </Card>
              </Link>
            </Reveal>
          ))}
          {recommended.length === 0 && (
            <Card className="p-6 text-muted-foreground sm:col-span-2 lg:col-span-3">
              No courses available yet.
            </Card>
          )}
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

      {/* Recent Activity */}
      {recentSubs && recentSubs.length > 0 && (
        <section className="mx-auto max-w-6xl px-6 pb-12">
          <Reveal>
            <h2 className="text-2xl font-bold flex items-center gap-2 mb-6">
              <History className="h-5 w-5 text-primary" /> Son Aktivite
            </h2>
          </Reveal>
          <Card className="divide-y divide-border overflow-hidden">
            {recentSubs.slice(0, 5).map((s, i) => (
              <Reveal key={s.submission_id} delay={i * 50}>
                <div className="flex items-center gap-3 p-4 hover:bg-accent/40 transition-colors">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                    s.verdict === "pass" ? "bg-emerald-500/10 text-emerald-400"
                      : s.verdict === "wrong_answer" ? "bg-red-500/10 text-red-400"
                      : "bg-zinc-500/10 text-zinc-400"
                  }`}>
                    {s.verdict === "pass" ? <CheckCircle className="h-4 w-4" />
                      : s.verdict === "wrong_answer" ? <XCircle className="h-4 w-4" />
                      : <Terminal className="h-4 w-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                        {s.verdict ?? "—"}
                      </Badge>
                      {s.runtime_ms != null && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" /> {s.runtime_ms}ms
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5 truncate font-mono">{s.code?.slice(0, 80)}</p>
                  </div>
                  {s.created_at && (
                    <span className="text-xs text-muted-foreground shrink-0">
                      {new Date(s.created_at).toLocaleDateString("tr-TR")}
                    </span>
                  )}
                </div>
              </Reveal>
            ))}
          </Card>
        </section>
      )}
    </Layout>
  );
}
