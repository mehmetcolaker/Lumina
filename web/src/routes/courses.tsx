import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { COURSES } from "@/lib/courses";
import { Reveal } from "@/components/site/Reveal";
import { Search, Clock, Zap, BookOpen, ArrowRight } from "lucide-react";

export const Route = createFileRoute("/courses")({
  component: CoursesPage,
  head: () => ({
    meta: [
      { title: "Courses — Lumina" },
      { name: "description", content: "Browse Lumina's full catalog of interactive coding courses." },
      { property: "og:title", content: "Courses — Lumina" },
    ],
  }),
});

const CATS = ["All", "Web Dev", "Data", "AI", "Backend", "Mobile", "Security", "Design", "Python", "JavaScript"];

function CoursesPage() {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("All");
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const filtered = useMemo(() => {
    return COURSES.filter((c) => {
      const m1 = cat === "All" || c.tag === cat;
      const m2 = !q || c.title.toLowerCase().includes(q.toLowerCase()) || c.desc.toLowerCase().includes(q.toLowerCase());
      return m1 && m2;
    });
  }, [q, cat]);

  return (
    <Layout>
      {/* Parallax hero */}
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
              <BookOpen className="mr-1 h-3 w-3" /> {COURSES.length} courses
            </Badge>
          </Reveal>
          <Reveal delay={100}>
            <h1 className="text-5xl font-bold tracking-tight text-foreground sm:text-6xl">
              Find your <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">next skill</span>
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
          {CATS.map((c) => (
            <button
              key={c}
              onClick={() => setCat(c)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition-all hover:-translate-y-0.5 ${
                cat === c
                  ? "bg-[image:var(--gradient-primary)] text-primary-foreground shadow-[var(--shadow-soft)]"
                  : "bg-secondary text-secondary-foreground hover:bg-accent"
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((c, i) => (
            <Reveal key={c.slug} delay={i * 60}>
              <Link to="/courses/$slug" params={{ slug: c.slug }}>
                <Card className="group h-full overflow-hidden p-6 hover-lift cursor-pointer border-border/60">
                  <div className="mb-4 flex h-32 items-center justify-center rounded-lg bg-[image:var(--gradient-hero)] transition-transform duration-500 group-hover:scale-105">
                    <span className="text-4xl font-bold text-primary/40 transition-transform group-hover:scale-125">
                      {c.tag.slice(0, 2).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Badge variant="outline">{c.level}</Badge>
                    <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {c.hours}h</span>
                    <span className="flex items-center gap-1 text-primary"><Zap className="h-3 w-3" /> {c.xp} XP</span>
                  </div>
                  <h3 className="mt-3 text-lg font-semibold text-foreground transition-colors group-hover:text-primary">
                    {c.title}
                  </h3>
                  <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{c.desc}</p>
                  <div className="mt-4 flex items-center text-sm font-medium text-primary opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0">
                    Start course <ArrowRight className="ml-1 h-4 w-4" />
                  </div>
                </Card>
              </Link>
            </Reveal>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="py-20 text-center text-muted-foreground animate-fade-in">No courses match your filters.</div>
        )}
      </section>
    </Layout>
  );
}
