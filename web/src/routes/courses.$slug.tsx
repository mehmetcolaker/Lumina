import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/site/Reveal";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { CoursePathResponse, CourseResponse } from "@/lib/api-types";
import { slugify, deriveLevel, totalCourseXp, estimateHours } from "@/lib/courses";
import { toast } from "sonner";
import { useState } from "react";
import {
  Clock,
  Zap,
  ArrowLeft,
  CheckCircle2,
  PlayCircle,
  Trophy,
  BookOpen,
} from "lucide-react";

export const Route = createFileRoute("/courses/$slug")({
  component: CourseDetail,
  head: () => ({
    meta: [{ title: "Course — Lumina" }],
  }),
});

function CourseDetail() {
  const { slug } = useParams({ from: "/courses/$slug" });
  const { user } = useAuth();

  // Step 1: list all courses to resolve slug → id
  const { data: courses, isLoading: listLoading } = useQuery<CourseResponse[]>({
    queryKey: ["courses"],
    queryFn: () => api.get<CourseResponse[]>("/courses/"),
  });

  const courseSummary = courses?.find((c) => slugify(c.title) === slug);

  // Step 2: fetch full hierarchical path for that course
  const {
    data: course,
    isLoading: detailLoading,
    isError,
  } = useQuery<CoursePathResponse>({
    queryKey: ["course-path", courseSummary?.id],
    enabled: !!courseSummary?.id,
    queryFn: () =>
      api.get<CoursePathResponse>(`/courses/${courseSummary!.id}/path`),
  });

  const [completing, setCompleting] = useState(false);

  if (listLoading || detailLoading) {
    return (
      <Layout>
        <div className="mx-auto max-w-3xl px-6 py-24 text-center">
          <p className="text-muted-foreground">Loading course…</p>
        </div>
      </Layout>
    );
  }

  if (isError || !courseSummary || !course) {
    return (
      <Layout>
        <div className="mx-auto max-w-3xl px-6 py-24 text-center">
          <h1 className="text-3xl font-bold">Course not found</h1>
          <Link to="/courses" className="mt-4 inline-block text-primary story-link">
            Back to courses
          </Link>
        </div>
      </Layout>
    );
  }

  const allSteps = course.sections.flatMap((s) => s.steps);
  const xpReward = totalCourseXp(course);
  const hours = estimateHours(course);
  const level = deriveLevel(course);

  // Mark the *first* incomplete step complete to demonstrate the API.
  const completeFirstStep = async () => {
    if (!user) {
      toast.error("Sign in to track progress");
      return;
    }
    if (allSteps.length === 0) {
      toast.error("This course has no steps yet");
      return;
    }
    setCompleting(true);
    try {
      const res = await api.post<{ xp_earned: number }>(
        `/progress/steps/${allSteps[0].id}/complete`,
      );
      toast.success(`+${res.xp_earned} XP earned! 🎉`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to record progress";
      toast.error(msg);
    } finally {
      setCompleting(false);
    }
  };

  return (
    <Layout>
      <section className="relative overflow-hidden bg-[image:var(--gradient-hero)] border-b border-border">
        <div className="absolute -top-20 right-10 h-72 w-72 rounded-full bg-primary/20 blur-3xl animate-blob" />
        <div className="relative mx-auto max-w-5xl px-6 py-16">
          <Link
            to="/courses"
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground story-link"
          >
            <ArrowLeft className="h-4 w-4" /> All courses
          </Link>
          <Reveal>
            <div className="mt-6 flex flex-wrap gap-2">
              <Badge variant="outline">{level}</Badge>
              <Badge variant="secondary">{course.language}</Badge>
              <Badge className="bg-[image:var(--gradient-primary)] text-primary-foreground">
                <Zap className="mr-1 h-3 w-3" />
                {xpReward} XP
              </Badge>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <h1 className="mt-4 text-4xl sm:text-5xl font-bold tracking-tight text-foreground">
              {course.title}
            </h1>
          </Reveal>
          <Reveal delay={200}>
            <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
              {course.description ?? "Interactive coding course."}
            </p>
          </Reveal>
          <Reveal delay={300}>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button
                size="lg"
                className="bg-[image:var(--gradient-primary)] text-primary-foreground glow-on-hover"
              >
                <PlayCircle className="mr-2 h-4 w-4" /> Start learning
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={completeFirstStep}
                disabled={completing || allSteps.length === 0}
                className="hover-scale"
              >
                <CheckCircle2 className="mr-2 h-4 w-4" /> Complete first step
              </Button>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-16 grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-8">
          {course.sections.map((section, sIdx) => (
            <div key={section.id}>
              <Reveal>
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-primary" />
                  {section.title}
                </h2>
              </Reveal>
              <div className="mt-4 space-y-3">
                {section.steps.map((step, i) => (
                  <Reveal key={step.id} delay={i * 50}>
                    <Card className="p-4 flex items-center gap-3 hover-lift cursor-pointer group">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary text-secondary-foreground font-semibold transition-all group-hover:bg-[image:var(--gradient-primary)] group-hover:text-primary-foreground group-hover:scale-110">
                        {sIdx * 100 + i + 1}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium">{step.title}</div>
                        <div className="text-xs text-muted-foreground capitalize">
                          {step.step_type}
                        </div>
                      </div>
                      <span className="flex items-center gap-1 text-sm text-primary font-medium">
                        <Zap className="h-3 w-3" />
                        {step.xp_reward} XP
                      </span>
                    </Card>
                  </Reveal>
                ))}
              </div>
            </div>
          ))}

          {course.sections.length === 0 && (
            <Card className="p-8 text-center text-muted-foreground">
              This course is being prepared. Check back soon!
            </Card>
          )}
        </div>

        <aside className="space-y-4">
          <Reveal>
            <Card className="p-6 sticky top-24 hover-lift">
              <h3 className="font-semibold flex items-center gap-2">
                <Trophy className="h-4 w-4 text-primary" /> Course rewards
              </h3>
              <div className="mt-4 space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total XP</span>
                  <span className="font-bold text-primary">+{xpReward}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Duration</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {hours}h
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sections</span>
                  <span>{course.sections.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Steps</span>
                  <span>{allSteps.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Level</span>
                  <span>{level}</span>
                </div>
              </div>
            </Card>
          </Reveal>
        </aside>
      </section>
    </Layout>
  );
}
