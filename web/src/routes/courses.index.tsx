import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Reveal } from "@/components/site/Reveal";
import { api } from "@/lib/api";
import type { LearningPathResponse, PathLevelResponse } from "@/lib/api-types";
import { slugify } from "@/lib/courses";
import { useAuth } from "@/hooks/useAuth";
import {
  Search, BookOpen, Code2, Database, Globe, Cpu, Lock, CheckCircle2,
  ChevronRight, ChevronDown, Zap, ArrowRight, MapIcon,
} from "lucide-react";

export const Route = createFileRoute("/courses/")({
  component: CoursesPage,
  head: () => ({
    meta: [
      { title: "Courses — Lumina" },
      { name: "description", content: "Browse Lumina's interactive coding courses." },
    ],
  }),
});

const LANG_META: Record<string, { gradient: string; textIcon: string }> = {
  Python:     { gradient: "from-blue-500 via-indigo-500 to-purple-600", textIcon: "PY" },
  JavaScript: { gradient: "from-yellow-400 via-amber-500 to-orange-600", textIcon: "JS" },
  SQL:        { gradient: "from-purple-500 via-pink-500 to-rose-600", textIcon: "SQL" },
  Go:         { gradient: "from-cyan-400 via-teal-500 to-emerald-600", textIcon: "GO" },
  Rust:       { gradient: "from-orange-600 via-red-500 to-pink-600", textIcon: "RS" },
};

const NODE_COLORS = [
  { bg: "from-emerald-500 to-emerald-600", border: "border-emerald-400", text: "text-emerald-100", glow: "shadow-emerald-500/30" },
  { bg: "from-sky-500 to-blue-600", border: "border-sky-400", text: "text-sky-100", glow: "shadow-blue-500/30" },
  { bg: "from-violet-500 to-purple-600", border: "border-violet-400", text: "text-violet-100", glow: "shadow-purple-500/30" },
  { bg: "from-amber-500 to-orange-600", border: "border-amber-400", text: "text-amber-100", glow: "shadow-amber-500/30" },
  { bg: "from-rose-500 to-pink-600", border: "border-rose-400", text: "text-rose-100", glow: "shadow-rose-500/30" },
  { bg: "from-teal-500 to-cyan-600", border: "border-teal-400", text: "text-teal-100", glow: "shadow-teal-500/30" },
  { bg: "from-indigo-500 to-violet-600", border: "border-indigo-400", text: "text-indigo-100", glow: "shadow-indigo-500/30" },
  { bg: "from-lime-500 to-green-600", border: "border-lime-400", text: "text-lime-100", glow: "shadow-lime-500/30" },
];

const defaultMeta = { gradient: "from-primary to-primary/70", textIcon: "?" };

function CoursesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selectedLang, setSelectedLang] = useState("Python");
  const [scrollY, setScrollY] = useState(0);

  const { data: paths, isLoading: pathsLoading } = useQuery<LearningPathResponse[]>({
    queryKey: ["paths"],
    queryFn: () => api.get<LearningPathResponse[]>("/paths/"),
  });

  const languages = useMemo(() => {
    const set = new Set<string>();
    paths?.forEach((p) => set.add(p.language));
    return Array.from(set).sort();
  }, [paths]);

  const selectedPath = paths?.find((p) => p.language === selectedLang);

  const { data: pathWithProgress } = useQuery<LearningPathResponse>({
    queryKey: ["path-progress", selectedPath?.id],
    queryFn: () => api.get<LearningPathResponse>(`/paths/${selectedPath!.id}`),
    enabled: !!selectedPath?.id && !!user,
    refetchInterval: 15_000,
  });

  useEffect(() => {
    const fn = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  const levels = pathWithProgress?.levels ?? selectedPath?.levels ?? [];

  // Zigzag layout: arrange into rows of 3
  const rows: PathLevelResponse[][] = [];
  for (let i = 0; i < levels.length; i += 3) {
    const row = levels.slice(i, i + 3);
    if (rows.length % 2 === 1) row.reverse(); // zigzag
    rows.push(row);
  }

  return (
    <Layout>
      {/* ── Hero ── */}
      <section className="relative overflow-hidden border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="absolute -top-32 -right-32 h-96 w-96 rounded-full bg-primary/20 blur-3xl animate-blob"
          style={{ transform: `translateY(${scrollY * 0.3}px)` }} />
        <div className="absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-accent/30 blur-3xl animate-blob"
          style={{ transform: `translateY(${scrollY * -0.2}px)`, animationDelay: "2s" }} />
        <div className="relative mx-auto max-w-7xl px-6 py-20 text-center">
          <Reveal>
            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight">
              Choose your{" "}
              <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">path</span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-lg text-muted-foreground">
              Each language has a structured roadmap. Complete each level to unlock the next.
            </p>
          </Reveal>
        </div>
      </section>

      {/* ── Language selector + Map ── */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 py-8">
        {/* Language pills */}
        <div className="mb-10 flex flex-wrap justify-center gap-3">
          {languages.map((lang) => {
            const meta = LANG_META[lang] ?? defaultMeta;
            return (
              <button
                key={lang}
                onClick={() => setSelectedLang(lang)}
                className={`px-6 py-3 rounded-xl font-bold text-sm transition-all hover:-translate-y-0.5 ${
                  selectedLang === lang
                    ? `bg-gradient-to-r ${meta.gradient} text-white shadow-lg`
                    : "bg-card border border-border text-muted-foreground hover:bg-accent"
                }`}
              >
                {meta.textIcon} {lang}
              </button>
            );
          })}
        </div>

        {pathsLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="h-8 w-8 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          </div>
        )}

        {!pathsLoading && levels.length === 0 && (
          <div className="py-20 text-center text-muted-foreground">
            No courses available for {selectedLang} yet.
          </div>
        )}

        {!pathsLoading && levels.length > 0 && (
          <div className="relative max-w-4xl mx-auto">
            {/* Map path */}
            <div className="space-y-2 md:space-y-4">
              {rows.map((row, rowIdx) => (
                <div key={rowIdx} className="flex items-center justify-center gap-3 md:gap-6">
                  {/* Connector from previous row */}
                  {rowIdx > 0 && (
                    <div className="hidden md:flex absolute left-1/2 -translate-x-1/2 -mt-6 mb-0">
                      <ChevronDown className="h-8 w-8 text-muted-foreground/40" />
                    </div>
                  )}
                  {row.map((level, colIdx) => {
                    const globalIdx = rowIdx * 3 + (rowIdx % 2 === 1 ? 2 - colIdx : colIdx);
                    const color = NODE_COLORS[globalIdx % NODE_COLORS.length];
                    const progressData = pathWithProgress?.levels?.[globalIdx];
                    const isUnlocked = progressData?.unlocked ?? (globalIdx === 0);
                    const progressPct = progressData?.progress_pct ?? 0;
                    const isComplete = progressPct >= 100;
                    const meta = LANG_META[selectedLang] ?? defaultMeta;

                    return (
                      <div key={level.id} className="flex-1 max-w-[280px] min-w-[140px]">
                        {/* Connector (previous to current) */}
                        {colIdx > 0 && (
                          <div className="hidden md:flex justify-center -mb-3">
                            <div className="h-0.5 w-12 bg-muted-foreground/20" />
                          </div>
                        )}

                        {/* Node card */}
                        <button
                          onClick={() => {
                            if (!isUnlocked) return;
                            if (!user) { navigate({ to: "/login" }); return; }
                            navigate({ to: `/courses/${slugify(level.course.title)}` });
                          }}
                          className={`w-full text-left transition-all duration-300 ${
                            isUnlocked ? "hover:-translate-y-1 hover:shadow-xl" : ""
                          }`}
                        >
                          <div
                            className={`relative rounded-2xl border-2 p-5 overflow-hidden transition-all duration-300
                              ${isComplete
                                ? "bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border-emerald-500/50 shadow-lg shadow-emerald-500/20"
                                : isUnlocked
                                ? `bg-gradient-to-br ${color.bg} ${color.border} shadow-lg ${color.glow} text-white`
                                : "bg-muted/40 border-border/30 opacity-50"
                              }`}
                          >
                            {/* Level number badge */}
                            <div className="flex items-center justify-between mb-3">
                              <div className={`flex h-10 w-10 items-center justify-center rounded-xl text-base font-bold
                                ${isComplete ? "bg-emerald-500/20 text-emerald-400"
                                  : isUnlocked ? "bg-white/20 text-white"
                                  : "bg-muted/50 text-muted-foreground"
                                }`}
                              >
                                {isComplete ? <CheckCircle2 className="h-5 w-5" />
                                  : !isUnlocked ? <Lock className="h-4 w-4" />
                                  : globalIdx + 1}
                              </div>

                              {/* Status badge */}
                              {isComplete && (
                                <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded-full">
                                  Complete
                                </span>
                              )}
                              {!isUnlocked && !isComplete && (
                                <span className="text-xs text-muted-foreground">
                                  {level.required_progress_pct}%
                                </span>
                              )}
                            </div>

                            {/* Level name */}
                            <div className={`text-[11px] font-bold uppercase tracking-wider mb-1
                              ${isComplete ? "text-emerald-400" : isUnlocked ? "text-white/80" : "text-muted-foreground"}`}
                            >
                              {level.level_name}
                            </div>

                            {/* Course title */}
                            <h3 className={`text-sm font-bold leading-tight mb-2
                              ${isComplete ? "text-emerald-700 dark:text-emerald-300"
                                : isUnlocked ? "text-white" : "text-muted-foreground"}`}
                            >
                              {level.course.title}
                            </h3>

                            {/* Stats */}
                            {isUnlocked && (
                              <div className="flex items-center gap-3 text-xs">
                                <span className={`flex items-center gap-1 ${isComplete ? "text-emerald-400" : "text-white/70"}`}>
                                  <BookOpen className="h-3 w-3" />
                                  {user ? `${progressPct}%` : "Start"}
                                </span>
                                <span className={`flex items-center gap-1 ${isComplete ? "text-emerald-400" : "text-white/70"}`}>
                                  <Zap className="h-3 w-3" />
                                  {level.order + 1}/{levels.length}
                                </span>
                              </div>
                            )}

                            {/* Progress bar */}
                            {user && isUnlocked && !isComplete && (
                              <div className="mt-3">
                                <Progress value={progressPct} className="h-1.5 bg-white/20" />
                              </div>
                            )}
                          </div>
                        </button>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Guide for non-users */}
        {!user && !pathsLoading && levels.length > 0 && (
          <div className="mt-12 text-center">
            <Card className="p-8 max-w-lg mx-auto">
              <MapIcon className="h-10 w-10 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">Track your progress</h3>
              <p className="text-sm text-muted-foreground mb-6">
                Sign in to save your progress, earn XP, and unlock the next levels.
                Your learning journey is saved forever.
              </p>
              <div className="flex gap-3 justify-center">
                <Button asChild className="bg-[image:var(--gradient-primary)] text-primary-foreground">
                  <Link to="/signup">Create free account</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to="/login">Sign in</Link>
                </Button>
              </div>
            </Card>
          </div>
        )}
      </section>
    </Layout>
  );
}
