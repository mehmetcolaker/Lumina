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
import { BookOpen, Lock, ArrowRight, CheckCircle2 } from "lucide-react";
import { useState } from "react";

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

function RoadmapPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const { data: paths, isLoading } = useQuery<LearningPathResponse[]>({
    queryKey: ["paths"],
    queryFn: () => api.get<LearningPathResponse[]>("/paths/"),
  });

  // For authenticated user, fetch the first path with progress
  const pathId = paths?.[0]?.id;
  const { data: pathWithProgress } = useQuery<LearningPathResponse>({
    queryKey: ["path-progress", pathId],
    queryFn: () => api.get<LearningPathResponse>(`/paths/${pathId}`),
    enabled: !!pathId && !!user,
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

  const path = pathWithProgress || paths?.[0];
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
      <div className="border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="mx-auto max-w-5xl px-6 py-16 text-center">
          <Reveal>
            <div className="flex items-center justify-center gap-2 text-4xl mb-4">{path.icon ?? "\uD83D\uDCCD"}</div>
            <h1 className="text-4xl font-bold">{path.title}</h1>
            <p className="mt-3 text-muted-foreground max-w-xl mx-auto">{path.description}</p>
          </Reveal>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-6 py-12">
        <div className="relative">
          {/* Vertical timeline line */}
          <div className="absolute left-8 top-12 bottom-12 w-0.5 bg-border hidden md:block" />

          <div className="space-y-8">
            {path.levels?.map((level, idx) => {
              const col = LEVEL_COLORS[idx % LEVEL_COLORS.length];
              const progress = pathWithProgress?.levels?.[idx];
              const isUnlocked = progress?.unlocked ?? (idx === 0);
              const progressPct = progress?.progress_pct ?? 0;

              return (
                <Reveal key={level.id} delay={idx * 80}>
                  <div
                    className={`relative flex flex-col md:flex-row gap-6 p-6 rounded-2xl border-2 transition-all
                      ${isUnlocked ? "bg-card hover-lift cursor-pointer" : "bg-muted/30 opacity-60 cursor-not-allowed"}
                      ${idx === 0 ? "border-primary/40" : level.unlocked ? "border-border" : "border-border/50"}
                    `}
                    onClick={() => {
                      if (!isUnlocked) return;
                      if (!user) { navigate({ to: "/login" }); return; }
                      navigate({ to: `/courses/${slugify(level.course.title)}` });
                    }}
                  >
                    {/* Level number badge */}
                    <div className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border-2 ${col.border} ${col.bg}`}>
                      {progressPct >= 100 ? (
                        <CheckCircle2 className={`h-7 w-7 ${col.text}`} />
                      ) : !isUnlocked ? (
                        <Lock className="h-6 w-6 text-muted-foreground" />
                      ) : (
                        <span className={`text-2xl font-bold ${col.text}`}>{idx + 1}</span>
                      )}
                    </div>

                    {/* Level info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="outline" className={col.text}>
                          {level.level_name}
                        </Badge>
                        {!isUnlocked && (
                          <Badge variant="outline" className="text-muted-foreground">
                            <Lock className="h-3 w-3 mr-1" /> {level.required_progress_pct}% required
                          </Badge>
                        )}
                        {progressPct >= 100 && (
                          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                            <CheckCircle2 className="h-3 w-3 mr-1" /> Complete
                          </Badge>
                        )}
                      </div>

                      <h3 className="text-xl font-bold mt-2 text-foreground">{level.course.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{level.course.description}</p>

                      {/* Progress bar */}
                      {user && isUnlocked && (
                        <div className="mt-4 flex items-center gap-4">
                          <Progress value={progressPct} className="h-2 flex-1" />
                          <span className="text-xs text-muted-foreground shrink-0">{progressPct}%</span>
                        </div>
                      )}
                    </div>

                    {/* Arrow */}
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
