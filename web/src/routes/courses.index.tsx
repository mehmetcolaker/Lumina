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
import { Search, BookOpen, ArrowRight, Code2, Database, Globe, Cpu } from "lucide-react";

export const Route = createFileRoute("/courses/")({
  component: CoursesPage,
  head: () => ({
    meta: [
      { title: "Courses — Lumina" },
      { name: "description", content: "Browse Lumina's full catalog of interactive coding courses." },
    ],
  }),
});

// Language meta — ikon ve renk eşlemesi
const LANG_META: Record<string, { icon: typeof Code2; gradient: string; textIcon: string }> = {
  Python:     { icon: Code2,     gradient: "from-blue-500 to-indigo-600",   textIcon: "🐍" },
  JavaScript: { icon: Globe,     gradient: "from-yellow-400 to-orange-500", textIcon: "⚡" },
  SQL:        { icon: Database,  gradient: "from-purple-500 to-pink-500",   textIcon: "🗄" },
  Go:         { icon: Cpu,       gradient: "from-cyan-500 to-teal-500",     textIcon: "🔷" },
};

const defaultMeta = { icon: Code2, gradient: "from-primary to-primary/70", textIcon: "📘" };

function CoursesPage() {
  const [q, setQ] = useState("");
  const [lang, setLang] = useState("All");
  const [scrollY, setScrollY] = useState(0);

  const { data: courses, isLoading, isError } = useQuery<CourseResponse[]>({
    queryKey: ["courses"],
    queryFn: () => api.get<CourseResponse[]>("/courses/"),
  });

  useEffect(() => {
    const fn = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  const languages = useMemo(() => {
    const set = new Set<string>(["All"]);
    courses?.forEach((c) => set.add(c.language));
    return Array.from(set);
  }, [courses]);

  const filtered = useMemo(() => {
    if (!courses) return [];
    return courses.filter((c) => {
      const m1 = lang === "All" || c.language === lang;
      const m2 = !q || c.title.toLowerCase().includes(q.toLowerCase()) || (c.description ?? "").toLowerCase().includes(q.toLowerCase());
      return m1 && m2;
    });
  }, [courses, q, lang]);

  return (
    <Layout>
      {/* ── Hero ── */}
      <section className="relative overflow-hidden border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="absolute -top-32 -right-32 h-96 w-96 rounded-full bg-primary/20 blur-3xl animate-blob"
          style={{ transform: `translateY(${scrollY * 0.3}px)` }} />
        <div className="absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-accent/30 blur-3xl animate-blob"
          style={{ transform: `translateY(${scrollY * -0.2}px)`, animationDelay: "2s" }} />

        <div className="relative mx-auto max-w-7xl px-6 py-24 text-center">
          <Reveal>
            <Badge variant="secondary" className="mb-4">
              <BookOpen className="mr-1 h-3 w-3" /> {courses?.length ?? 0} interaktif kurs
            </Badge>
          </Reveal>
          <Reveal delay={100}>
            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight">
              Bir sonraki{" "}
              <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">
                becerini keşfet
              </span>
            </h1>
          </Reveal>
          <Reveal delay={200}>
            <p className="mx-auto mt-5 max-w-2xl text-lg text-muted-foreground">
              Her adımda gerçek kod yaz, quiz çöz ve XP kazan. Sıfırdan uzmana.
            </p>
          </Reveal>
          <Reveal delay={300}>
            <div className="relative mx-auto mt-8 max-w-xl">
              <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Kurs ara… (Python, SQL, JavaScript…)"
                className="h-13 pl-11 rounded-full text-base shadow-[var(--shadow-card)]"
              />
            </div>
          </Reveal>
        </div>
      </section>

      {/* ── Course grid ── */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        {/* Language filter pills */}
        <div className="mb-10 flex flex-wrap gap-2">
          {languages.map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={`rounded-full px-5 py-2 text-sm font-medium transition-all hover:-translate-y-0.5 ${
                lang === l
                  ? "bg-[image:var(--gradient-primary)] text-primary-foreground shadow-md"
                  : "bg-secondary text-secondary-foreground hover:bg-accent"
              }`}
            >
              {l === "All" ? "🌍 Tümü" : `${LANG_META[l]?.textIcon ?? "📘"} ${l}`}
            </button>
          ))}
        </div>

        {isLoading && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-72 rounded-2xl bg-muted animate-pulse" />
            ))}
          </div>
        )}

        {isError && (
          <div className="py-20 text-center text-destructive">
            Backend bağlantısı kurulamadı. Backend çalışıyor mu?
          </div>
        )}

        {!isLoading && !isError && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((c, i) => {
              const meta = LANG_META[c.language] ?? defaultMeta;
              return (
                <Reveal key={c.id} delay={i * 60}>
                  <Link to="/courses/$slug" params={{ slug: slugify(c.title) }} className="group block h-full">
                    <Card className="h-full overflow-hidden hover-lift border-border/60 transition-all duration-300">
                      {/* Card thumbnail */}
                      <div className={`relative h-36 bg-gradient-to-br ${meta.gradient} flex items-center justify-center overflow-hidden`}>
                        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_30%_70%,white,transparent)]" />
                        <span className="text-6xl select-none">{meta.textIcon}</span>
                        <div className="absolute right-4 top-4">
                          <Badge className="bg-white/20 text-white border-0 backdrop-blur-sm text-xs">
                            {c.language}
                          </Badge>
                        </div>
                      </div>

                      {/* Card body */}
                      <div className="p-5">
                        <h3 className="font-bold text-lg text-foreground group-hover:text-primary transition-colors leading-tight">
                          {c.title}
                        </h3>
                        <p className="mt-2 text-sm text-muted-foreground line-clamp-2 leading-6">
                          {c.description ?? "İnteraktif kodlama kursu."}
                        </p>

                        <div className="mt-5 flex items-center justify-between">
                          <div className="flex gap-3 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <BookOpen className="h-3 w-3" /> Başlangıç
                            </span>
                          </div>
                          <span className="flex items-center gap-1 text-sm font-semibold text-primary opacity-0 translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                            Başla <ArrowRight className="h-4 w-4" />
                          </span>
                        </div>
                      </div>
                    </Card>
                  </Link>
                </Reveal>
              );
            })}
          </div>
        )}

        {!isLoading && !isError && filtered.length === 0 && (
          <div className="py-24 text-center">
            <p className="text-muted-foreground">Arama sonucu bulunamadı.</p>
            <button onClick={() => { setQ(""); setLang("All"); }} className="mt-3 text-primary text-sm story-link">
              Filtreleri temizle
            </button>
          </div>
        )}
      </section>
    </Layout>
  );
}
