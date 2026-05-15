import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Reveal } from "@/components/site/Reveal";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { slugify } from "@/lib/courses";
import type { LearningPathResponse } from "@/lib/api-types";
import { Lock, ArrowRight, CheckCircle2 } from "lucide-react";
import { useState, useMemo } from "react";

export const Route = createFileRoute("/roadmap")({
  component: RoadmapPage,
  head: () => ({ meta: [{ title: "Roadmap — Lumina" }] }),
});

const LEVEL_COLORS = [
  { bg: "bg-emerald-500/10", border: "border-emerald-500/30", text: "text-emerald-400" },
  { bg: "bg-blue-500/10", border: "border-blue-500/30", text: "text-blue-400" },
  { bg: "bg-purple-500/10", border: "border-purple-500/30", text: "text-purple-400" },
  { bg: "bg-amber-500/10", border: "border-amber-500/30", text: "text-amber-400" },
  { bg: "bg-rose-500/10", border: "border-rose-500/30", text: "text-rose-400" },
  { bg: "bg-cyan-500/10", border: "border-cyan-500/30", text: "text-cyan-400" },
];

const LANG_ICONS: Record<string, string> = {
  Python: "PY",
  JavaScript: "JS",
  SQL: "SQL",
};

function RoadmapPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selectedLang, setSelectedLang] = useState<string>("Python");
  const { data: paths, isLoading } = useQuery<LearningPathResponse[]>({
    queryKey: ["paths"],
    queryFn: () => api.get<LearningPathResponse[]>("/paths/"),
  });

  // Group paths by language
  const languages = useMemo(() => {
    if (!paths) return ["Python"];
    return [...new Set(paths.map((p) => p.language))].sort();
  }, [paths]);

  const selectedPath = paths?.find((p) => p.language === selectedLang);

  // For authenticated user, fetch selected path with progress
  const { data: pathWithProgress } = useQuery<LearningPathResponse>({
    queryKey: ["path-progress", selectedPath?.id],
    queryFn: () => api.get<LearningPathResponse>(`/paths/${selectedPath!.id}`),
    enabled: !!selectedPath?.id && !!user,
    refetchInterval: 10_000,
  });

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="h-8 w-8 rounded-full border-4 border-primary border-t-transparent animate-spin" />
        </div>
      </Layout>
    );
  }

  const path = pathWithProgress || selectedPath;
  if (!path) {
    return (
      <Layout>
        <div className="mx-auto max-w-xl px-6 py-24 text-center">
          <h1 className="text-3xl font-bold mb-4">No roadmap found</h1>
          <p className="text-muted-foreground">No learning paths available yet.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Hero */}
      <div className="border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="mx-auto max-w-5xl px-6 py-16 text-center">
          <Reveal>
            <h1 className="text-4xl font-bold">Choose Your Path</h1>
            <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
              Select a programming language and follow a structured learning roadmap from beginner
              to advanced.
            </p>
          </Reveal>

          {/* Language selector */}
          <Reveal delay={100}>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              {languages.map((lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLang(lang)}
                  className={`px-6 py-3 rounded-xl font-bold text-sm transition-all hover:-translate-y-0.5 ${
                    selectedLang === lang
                      ? "bg-[image:var(--gradient-primary)] text-primary-foreground shadow-lg"
                      : "bg-card border border-border text-muted-foreground hover:bg-accent"
                  }`}
                >
                  <span className="mr-2">{LANG_ICONS[lang] ?? lang.slice(0, 2).toUpperCase()}</span>
                  {lang}
                </button>
              ))}
            </div>
          </Reveal>
        </div>
      </div>

      {/* Path detail */}
      <div className="mx-auto max-w-5xl px-6 py-12">
        <div className="text-center mb-10">
          <Reveal>
            <h2 className="text-2xl font-bold">{path.title}</h2>
            <p className="text-muted-foreground mt-2">{path.description}</p>
          </Reveal>
        </div>

        <div className="relative">
          <div className="absolute left-8 top-12 bottom-12 w-0.5 bg-border hidden md:block" />

          <div className="space-y-8">
            {path.levels?.map((level, idx) => {
              const col = LEVEL_COLORS[idx % LEVEL_COLORS.length];
              const progress = pathWithProgress?.levels?.[idx];
              const isUnlocked = progress?.unlocked ?? idx === 0;
              const progressPct = progress?.progress_pct ?? 0;

              return (
                <Reveal key={level.id} delay={idx * 80}>
                  <div
                    className={`relative flex flex-col md:flex-row gap-6 p-6 rounded-2xl border-2 transition-all
                      ${isUnlocked ? "bg-card hover:shadow-md hover:-translate-y-0.5 cursor-pointer" : "bg-muted/30 opacity-60 cursor-not-allowed"}
                    `}
                    onClick={() => {
                      if (!isUnlocked) return;
                      if (!user) {
                        navigate({ to: "/login" });
                        return;
                      }
                      navigate({ to: `/courses/${slugify(level.course.title)}` });
                    }}
                  >
                    <div
                      className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border-2 ${col.border} ${col.bg}`}
                    >
                      {progressPct >= 100 ? (
                        <CheckCircle2 className={`h-7 w-7 ${col.text}`} />
                      ) : !isUnlocked ? (
                        <Lock className="h-6 w-6 text-muted-foreground" />
                      ) : (
                        <span className={`text-2xl font-bold ${col.text}`}>{idx + 1}</span>
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="outline" className={col.text}>
                          {level.level_name}
                        </Badge>
                        {!isUnlocked && (
                          <Badge variant="outline" className="text-muted-foreground">
                            <Lock className="h-3 w-3 mr-1" /> {level.required_progress_pct}%
                            required
                          </Badge>
                        )}
                        {progressPct >= 100 && (
                          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                            <CheckCircle2 className="h-3 w-3 mr-1" /> Complete
                          </Badge>
                        )}
                      </div>
                      <h3 className="text-xl font-bold mt-2 text-foreground">
                        {level.course.title}
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {level.course.description}
                      </p>
                      {user && isUnlocked && (
                        <div className="mt-4 flex items-center gap-4">
                          <Progress value={progressPct} className="h-2 flex-1" />
                          <span className="text-xs text-muted-foreground shrink-0">
                            {progressPct}%
                          </span>
                        </div>
                      )}
                    </div>
                    {isUnlocked && (
                      <div className="hidden md:flex items-center shrink-0">
                        <ArrowRight className="h-5 w-5 text-muted-foreground" />
                      </div>
                    )}
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </div>
    </Layout>
  );
}
