import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Reveal } from "@/components/site/Reveal";
import { api } from "@/lib/api";
import type { CourseResponse } from "@/lib/api-types";
import { slugify } from "@/lib/courses";
import { Search, BookOpen, ArrowRight } from "lucide-react";

export const Route = createFileRoute("/courses")({
  component: CoursesPage,
  head: () => ({
    meta: [
      { title: "Courses — Lumina" },
      {
        name: "description",
        content: "Browse Lumina's full catalog of interactive coding courses.",
      },
      { property: "og:title", content: "Courses — Lumina" },
    ],
  }),
});

function CoursesPage() {
  const [q, setQ] = useState("");
  const [language, setLanguage] = useState<string>("All");
  const [scrollY, setScrollY] = useState(0);

  const {
    data: courses,
    isLoading,
    isError,
    error,
  } = useQuery<CourseResponse[]>({
    queryKey: ["courses"],
    queryFn: () => api.get<CourseResponse[]>("/courses/"),
  });

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const languages = useMemo(() => {
    const set = new Set<string>(["All"]);
    courses?.forEach((c) => set.add(c.language));
    return Array.from(set);
  }, [courses]);

  const filtered = useMemo(() => {
    if (!courses) return [];
    return courses.filter((c) => {
      const m1 = language === "All" || c.language === language;
      const m2 =
        !q ||
        c.title.toLowerCase().includes(q.toLowerCase()) ||
        (c.description ?? "").toLowerCase().includes(q.toLowerCase());
      return m1 && m2;
    });
  }, [courses, q, language]);

  return (
    <Layout>
      <section className="relative overflow-hidden border-b border-border bg-[image:var(--gradient-hero)]">
        <div
          className="absolute -top-32 -right-32 h-96 w-96 rounded-full bg-primary/30 blur-3xl animate-blob"
          style={{ transform: `translateY(${scrollY * 0.3}px)` }}
        />
        <div
          className="absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-accent/40 blur-3xl animate-blob"
          style={{ transform: `translateY(${scrollY * -0.2}px)`, animationDelay: "2s" }}
        />
        <div className="relative mx-auto max-w-7xl px-6 py-20 text-center">
          <Reveal>
            <Badge variant="secondary" className="mb-4 animate-fade-in">
              <BookOpen className="mr-1 h-3 w-3" /> {courses?.length ?? 0} courses
            </Badge>
          </Reveal>
          <Reveal delay={100}>
            <h1 className="text-5xl font-bold tracking-tight text-foreground sm:text-6xl">
              Find your{" "}
              <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">
                next skill
              </span>
            </h1>
          </Reveal>
          <Reveal delay={200}>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
              Hands-on courses, projects and quizzes to take you from zero to hero.
            </p>
          </Reveal>
          <Reveal delay={300}>
            <div className="relative mx-auto mt-8 max-w-xl">
              <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search courses…"
                className="h-12 pl-11 rounded-full shadow-[var(--shadow-card)] focus:scale-[1.02] transition-transform"
              />
            </div>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="mb-8 flex flex-wrap gap-2">
          {languages.map((lang) => (
            <button
              key={lang}
              onClick={() => setLanguage(lang)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition-all hover:-translate-y-0.5 ${
                language === lang
                  ? "bg-[image:var(--gradient-primary)] text-primary-foreground shadow-[var(--shadow-soft)]"
                  : "bg-secondary text-secondary-foreground hover:bg-accent"
              }`}
            >
              {lang}
            </button>
          ))}
        </div>

        {isLoading && (
          <div className="py-20 text-center text-muted-foreground">Loading courses…</div>
        )}

        {isError && (
          <div className="py-20 text-center text-destructive">
            Failed to load courses: {(error as Error)?.message ?? "Unknown error"}
          </div>
        )}

        {!isLoading && !isError && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((c, i) => (
              <Reveal key={c.id} delay={i * 60}>
                <Link to="/courses/$slug" params={{ slug: slugify(c.title) }}>
                  <Card className="group h-full overflow-hidden p-6 hover-lift cursor-pointer border-border/60">
                    <div className="mb-4 flex h-32 items-center justify-center rounded-lg bg-[image:var(--gradient-hero)] transition-transform duration-500 group-hover:scale-105">
                      <span className="text-4xl font-bold text-primary/40 transition-transform group-hover:scale-125">
                        {c.language.slice(0, 2).toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="outline">{c.language}</Badge>
                    </div>
                    <h3 className="mt-3 text-lg font-semibold text-foreground transition-colors group-hover:text-primary">
                      {c.title}
                    </h3>
                    <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">
                      {c.description ?? "Interactive coding course."}
                    </p>
                    <div className="mt-4 flex items-center text-sm font-medium text-primary opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0">
                      Start course <ArrowRight className="ml-1 h-4 w-4" />
                    </div>
                  </Card>
                </Link>
              </Reveal>
            ))}
          </div>
        )}

        {!isLoading && !isError && filtered.length === 0 && (
          <div className="py-20 text-center text-muted-foreground animate-fade-in">
            No courses match your filters.
          </div>
        )}
      </section>
    </Layout>
  );
}
