import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { CoursePathResponse, CourseResponse, StepResponse } from "@/lib/api-types";
import { slugify, deriveLevel, totalCourseXp, estimateHours } from "@/lib/courses";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { useState, useEffect } from "react";
import {
  ArrowLeft, ArrowRight, BookOpen, CheckCircle2, CheckCircle, Clock,
  Code2, HelpCircle, PlayCircle, Trophy, Zap, ChevronRight,
  Lock, AlertCircle, RotateCcw,
} from "lucide-react";

export const Route = createFileRoute("/courses/$slug")({
  component: CourseDetail,
  head: () => ({ meta: [{ title: "Course — Lumina" }] }),
});

// ─────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────

const STEP_META: Record<string, { icon: typeof BookOpen; label: string; color: string; bg: string; border: string }> = {
  theory: { icon: BookOpen,   label: "Teori",     color: "text-blue-500",    bg: "bg-blue-500/10",    border: "border-blue-500/30" },
  quiz:   { icon: HelpCircle, label: "Quiz",      color: "text-amber-500",   bg: "bg-amber-500/10",   border: "border-amber-500/30" },
  code:   { icon: Code2,      label: "Kod Yaz",   color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30" },
};

const FREE_STEPS = 2; // Giriş yapmadan açık olan adım sayısı

// ─────────────────────────────────────────────────────
// Theory renderer
// ─────────────────────────────────────────────────────

function TheoryStep({ step }: { step: StepResponse }) {
  const md: string = (step.content_data?.body_markdown as string) ?? "";

  // Kodu inline'lardan ayrıştır
  const segments: Array<{ type: "text" | "code"; content: string; lang?: string }> = [];
  let buf = "";
  let inCode = false;
  let lang = "python";
  let codeBuf = "";
  for (const line of md.split("\n")) {
    if (line.startsWith("```")) {
      if (!inCode) {
        if (buf.trim()) segments.push({ type: "text", content: buf });
        buf = "";
        lang = line.slice(3).trim() || "python";
        codeBuf = "";
        inCode = true;
      } else {
        segments.push({ type: "code", content: codeBuf, lang });
        codeBuf = "";
        inCode = false;
      }
      continue;
    }
    if (inCode) { codeBuf += line + "\n"; }
    else { buf += line + "\n"; }
  }
  if (buf.trim()) segments.push({ type: "text", content: buf });

  const inline = (text: string) => {
    const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
    return parts.map((p, i) => {
      if (p.startsWith("`") && p.endsWith("`"))
        return <code key={i} className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono text-primary">{p.slice(1,-1)}</code>;
      if (p.startsWith("**") && p.endsWith("**"))
        return <strong key={i} className="font-semibold">{p.slice(2,-2)}</strong>;
      return p;
    });
  };

  const renderLine = (line: string, i: number) => {
    if (line.startsWith("# "))   return <h1 key={i} className="text-2xl font-bold mt-6 mb-3 text-foreground">{inline(line.slice(2))}</h1>;
    if (line.startsWith("## "))  return <h2 key={i} className="text-xl font-bold mt-5 mb-2 text-foreground">{inline(line.slice(3))}</h2>;
    if (line.startsWith("### ")) return <h3 key={i} className="text-lg font-semibold mt-4 mb-1 text-foreground">{inline(line.slice(4))}</h3>;
    if (line.startsWith("- "))   return <li key={i} className="ml-6 list-disc text-sm leading-7 text-muted-foreground">{inline(line.slice(2))}</li>;
    if (line.startsWith("> "))   return (
      <blockquote key={i} className="my-3 border-l-4 border-primary/50 pl-4 italic text-muted-foreground bg-primary/5 py-2 rounded-r-lg">
        {inline(line.slice(2))}
      </blockquote>
    );
    if (line.startsWith("| "))   return null; // tablo satırları atla
    if (line === "")             return <div key={i} className="h-3" />;
    return <p key={i} className="text-sm leading-7 text-foreground">{inline(line)}</p>;
  };

  return (
    <div className="space-y-1 max-w-none">
      {segments.map((seg, si) =>
        seg.type === "code" ? (
          <div key={si} className="my-5 rounded-xl overflow-hidden border border-border shadow-sm">
            <div className="flex items-center gap-2 bg-zinc-900 px-4 py-2.5 border-b border-zinc-700/50">
              <div className="flex gap-1.5">
                <div className="h-3 w-3 rounded-full bg-red-500/80" />
                <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
                <div className="h-3 w-3 rounded-full bg-green-500/80" />
              </div>
              <span className="ml-2 text-xs text-zinc-400 font-mono">{seg.lang}</span>
            </div>
            <pre className="bg-[#0d1117] p-5 overflow-x-auto text-sm font-mono leading-6">
              {seg.content.trimEnd().split("\n").map((line, li) => (
                <SyntaxLine key={li} line={line} lang={seg.lang ?? "python"} />
              ))}
            </pre>
          </div>
        ) : (
          <div key={si}>{seg.content.split("\n").map((l, i) => renderLine(l, i))}</div>
        )
      )}
    </div>
  );
}

function SyntaxLine({ line, lang }: { line: string; lang: string }) {
  const pyKw = ["def","return","if","elif","else","for","while","in","and","or","not","True","False","None","print","len","range","import","from","class","pass","break","continue","try","except","with","as","lambda","yield"];
  const jsKw = ["const","let","var","function","return","if","else","for","while","class","import","from","export","default","new","this","typeof","await","async","=>"];
  const sqlKw = ["SELECT","FROM","WHERE","AND","OR","ORDER","BY","BETWEEN","LIKE","IN","JOIN","LEFT","RIGHT","INNER","GROUP","HAVING","LIMIT","INSERT","UPDATE","DELETE","CREATE","DROP","TABLE","AS","ON","SET"];
  const keywords = lang === "sql" ? sqlKw : lang.startsWith("js") ? jsKw : pyKw;

  const parts = line.split(/(\s+|[()[\]{},.:=+\-*/!<>])/g);
  return (
    <div className="min-h-[1.5rem]">
      {parts.map((p, i) => {
        if (keywords.includes(p)) return <span key={i} className="text-purple-400 font-semibold">{p}</span>;
        if (/^["'`]/.test(p) && p.length > 1) return <span key={i} className="text-green-400">{p}</span>;
        if (/^-?\d+(\.\d+)?$/.test(p.trim()) && p.trim()) return <span key={i} className="text-amber-300">{p}</span>;
        if (p.startsWith("#") || p.startsWith("//")) return <span key={i} className="text-zinc-500 italic">{p}</span>;
        return <span key={i} className="text-zinc-200">{p}</span>;
      })}
    </div>
  );
}

// ─────────────────────────────────────────────────────
// Quiz step — çoktan seçmeli
// ─────────────────────────────────────────────────────

function QuizStep({ step, onCorrect }: { step: StepResponse; onCorrect: () => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const correct = step.content_data?.correct_option as string;
  const question = step.content_data?.question as string ?? "";
  const options = (step.content_data?.options as { id: string; label: string }[]) ?? [];
  const explanation = step.content_data?.explanation as string ?? "";
  const isRight = selected === correct;

  const reset = () => { setSelected(null); setSubmitted(false); };

  // Soruyu ve kod bloklarını ayır
  const qParts = question.split("```");

  return (
    <div className="space-y-5">
      {/* Soru */}
      <div className="space-y-3">
        {qParts.map((part, i) =>
          i % 2 === 0 ? (
            <p key={i} className="text-base leading-7 font-medium text-foreground whitespace-pre-line">{part.trim()}</p>
          ) : (
            <div key={i} className="rounded-xl overflow-hidden border border-border">
              <div className="bg-zinc-900 px-4 py-2 border-b border-zinc-700/50 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
                  <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/70" />
                  <div className="h-2.5 w-2.5 rounded-full bg-green-500/70" />
                </div>
                <span className="ml-2 text-xs text-zinc-400 font-mono">python</span>
              </div>
              <pre className="bg-[#0d1117] p-4 text-sm font-mono leading-6">
                {part.trim().split("\n").map((l, li) => <SyntaxLine key={li} line={l} lang="python" />)}
              </pre>
            </div>
          )
        )}
      </div>

      {/* Şıklar */}
      <div className="grid gap-3">
        {options.map((opt) => {
          let cls = "border-2 border-border bg-card hover:bg-accent/40 hover:border-primary/40 cursor-pointer";
          if (submitted && opt.id === correct)
            cls = "border-2 border-emerald-500 bg-emerald-500/10 cursor-default";
          else if (submitted && opt.id === selected && !isRight)
            cls = "border-2 border-red-500 bg-red-500/10 cursor-default";
          else if (!submitted && selected === opt.id)
            cls = "border-2 border-primary bg-primary/10 cursor-pointer";

          return (
            <button
              key={opt.id}
              disabled={submitted}
              onClick={() => setSelected(opt.id)}
              className={`w-full text-left px-5 py-4 rounded-xl transition-all flex items-center gap-4 ${cls}`}
            >
              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full font-bold text-xs uppercase border-2 transition-colors
                ${!submitted && selected === opt.id ? "border-primary bg-primary text-primary-foreground"
                  : submitted && opt.id === correct ? "border-emerald-500 bg-emerald-500 text-white"
                  : submitted && opt.id === selected && !isRight ? "border-red-500 bg-red-500 text-white"
                  : "border-muted-foreground/30 text-muted-foreground"}`}>
                {opt.id}
              </div>
              <span className="flex-1 text-sm font-medium">{opt.label}</span>
              {submitted && opt.id === correct && <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0" />}
              {submitted && opt.id === selected && !isRight && <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />}
            </button>
          );
        })}
      </div>

      {/* Aksiyon butonları */}
      {!submitted ? (
        <Button
          disabled={!selected}
          onClick={() => { setSubmitted(true); if (selected === correct) setTimeout(onCorrect, 1200); }}
          className="w-full h-12 text-base bg-[image:var(--gradient-primary)] text-primary-foreground disabled:opacity-40"
        >
          Cevabı Kontrol Et <ChevronRight className="ml-2 h-5 w-5" />
        </Button>
      ) : (
        <div className="space-y-3">
          {/* Sonuç */}
          <div className={`rounded-xl p-5 border ${isRight
            ? "bg-emerald-500/10 border-emerald-500/30"
            : "bg-red-500/10 border-red-500/30"}`}>
            <div className={`font-bold text-base mb-2 flex items-center gap-2 ${isRight ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
              {isRight ? <><CheckCircle className="h-5 w-5" /> Doğru cevap! 🎉</> : <><AlertCircle className="h-5 w-5" /> Yanlış cevap</>}
            </div>
            <p className="text-sm text-muted-foreground whitespace-pre-line leading-6">{explanation}</p>
          </div>
          {/* Devam / Tekrar */}
          <div className="flex gap-3">
            {!isRight && (
              <Button variant="outline" onClick={reset} className="flex-1">
                <RotateCcw className="mr-2 h-4 w-4" /> Tekrar Dene
              </Button>
            )}
            {isRight && (
              <Button onClick={onCorrect} className="flex-1 bg-[image:var(--gradient-primary)] text-primary-foreground">
                Sonraki Adım <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────
// Code step — yazılabilir editör
// ─────────────────────────────────────────────────────

function CodeStep({ step, onComplete }: { step: StepResponse; onComplete: () => void }) {
  const starter = (step.content_data?.starter_code as string) ?? "";
  const solution = (step.content_data?.solution as string) ?? "";
  const instruction = (step.content_data?.instruction as string) ?? "";
  const expected = (step.content_data?.expected_output as string) ?? "";

  const [code, setCode] = useState(starter);
  const [revealed, setRevealed] = useState(false);

  // Tab tuşu desteği
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const el = e.currentTarget;
      const start = el.selectionStart;
      const end = el.selectionEnd;
      const newCode = code.substring(0, start) + "    " + code.substring(end);
      setCode(newCode);
      setTimeout(() => el.setSelectionRange(start + 4, start + 4), 0);
    }
  };

  const revealSolution = () => { setCode(solution); setRevealed(true); };
  const reset = () => { setCode(starter); setRevealed(false); };

  return (
    <div className="space-y-5">
      {/* Görev açıklaması */}
      <div className="rounded-xl bg-amber-500/8 border border-amber-500/30 p-5">
        <h3 className="font-bold text-amber-700 dark:text-amber-400 mb-3 flex items-center gap-2 text-sm">
          <Code2 className="h-4 w-4" /> Görev
        </h3>
        <p className="text-sm leading-7 whitespace-pre-line text-foreground">{instruction}</p>
      </div>

      {/* Kod editörü */}
      <div className="rounded-xl overflow-hidden border border-border shadow-sm">
        {/* Editör header */}
        <div className="flex items-center justify-between bg-zinc-900 px-4 py-2.5 border-b border-zinc-700/50">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="h-3 w-3 rounded-full bg-red-500/80" />
              <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
              <div className="h-3 w-3 rounded-full bg-green-500/80" />
            </div>
            <span className="text-xs text-zinc-400 font-mono ml-1">main.py</span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={reset} className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-1">
              <RotateCcw className="h-3 w-3" /> Sıfırla
            </button>
            {!revealed && solution && (
              <button onClick={revealSolution} className="text-xs text-zinc-500 hover:text-amber-400 transition-colors">
                Çözümü Göster
              </button>
            )}
          </div>
        </div>
        {/* Kod alanı */}
        <div className="relative">
          {/* Satır numaraları */}
          <div className="absolute left-0 top-0 bottom-0 w-12 bg-[#0a0e16] flex flex-col pt-5 px-2 border-r border-zinc-700/30 select-none pointer-events-none">
            {code.split("\n").map((_, i) => (
              <div key={i} className="text-zinc-600 text-xs font-mono leading-6 text-right">{i + 1}</div>
            ))}
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full pl-14 pr-5 py-5 bg-[#0d1117] text-sm font-mono leading-6 text-zinc-200 resize-none outline-none min-h-[300px] caret-blue-400"
            spellCheck={false}
            autoCorrect="off"
            autoCapitalize="off"
            style={{ tabSize: 4 }}
            placeholder="# Kodunu buraya yaz..."
          />
        </div>
      </div>

      {/* Beklenen çıktı */}
      {expected && (
        <div className="rounded-xl overflow-hidden border border-border">
          <div className="bg-zinc-900/80 px-4 py-2.5 border-b border-zinc-700/30 flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-zinc-400 font-mono">Beklenen Çıktı</span>
          </div>
          <pre className="bg-[#0d1117] p-4 text-xs font-mono text-green-400 whitespace-pre-wrap leading-5">{expected}</pre>
        </div>
      )}

      {/* Tamamla */}
      <Button onClick={onComplete} className="w-full h-12 text-base bg-[image:var(--gradient-primary)] text-primary-foreground">
        <CheckCircle2 className="mr-2 h-5 w-5" />
        {revealed ? "Çözümü anladım, devam et" : "Tamamladım, devam et"}
      </Button>
    </div>
  );
}

// ─────────────────────────────────────────────────────
// Giriş gereksinimi — kilitli içerik
// ─────────────────────────────────────────────────────

function LockedContent() {
  return (
    <div className="rounded-2xl border-2 border-dashed border-border flex flex-col items-center justify-center py-16 px-8 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted mb-5">
        <Lock className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-xl font-bold text-foreground mb-2">Bu adım kilitli</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-sm">
        Devam edebilmek için ücretsiz hesap oluştur. Tüm kurslar, quiz'ler ve kod alıştırmaları seni bekliyor.
      </p>
      <div className="flex gap-3">
        <Button asChild className="bg-[image:var(--gradient-primary)] text-primary-foreground">
          <Link to="/signup">Ücretsiz Hesap Oluştur</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/login">Giriş Yap</Link>
        </Button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────
// Ana bileşen
// ─────────────────────────────────────────────────────

function CourseDetail() {
  const { slug } = useParams({ from: "/courses/$slug" });
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: courses, isLoading: listLoading } = useQuery<CourseResponse[]>({
    queryKey: ["courses"],
    queryFn: () => api.get<CourseResponse[]>("/courses/"),
    staleTime: 60_000,
  });

  const courseSummary = courses?.find((c) => slugify(c.title) === slug);

  const { data: course, isLoading: detailLoading, isError } = useQuery<CoursePathResponse>({
    queryKey: ["course-path", courseSummary?.id ?? slug],
    enabled: !!courseSummary?.id,
    staleTime: 60_000,
    queryFn: () => api.get<CoursePathResponse>(`/courses/${courseSummary!.id}/path`),
  });

  const allSteps = course?.sections.flatMap((s) => s.steps) ?? [];
  const [activeIdx, setActiveIdx] = useState(0);
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set());

  // Adım tamamla
  const completeStep = async (stepId: string) => {
    if (!user) return; // sessizce geç
    if (completedIds.has(stepId)) return;
    try {
      const res = await api.post<{ xp_earned: number }>(`/progress/steps/${stepId}/complete`);
      setCompletedIds((prev) => new Set([...prev, stepId]));
      toast.success(`+${res.xp_earned} XP kazandın! 🎉`);
      queryClient.invalidateQueries({ queryKey: ["leaderboard"] });
    } catch {
      // "already completed" sessizce handle et
      setCompletedIds((prev) => new Set([...prev, stepId]));
    }
  };

  // Sonraki adıma geç
  const goNext = () => {
    const step = allSteps[activeIdx];
    if (step) completeStep(step.id);
    if (activeIdx < allSteps.length - 1) setActiveIdx(activeIdx + 1);
  };

  // ── Loading/error states ──
  const courseNotFound = !listLoading && courses && !courseSummary;

  if (listLoading || (!!courseSummary?.id && detailLoading)) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <div className="h-10 w-10 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          <p className="text-muted-foreground">Kurs yükleniyor…</p>
        </div>
      </Layout>
    );
  }

  if (isError || !course || courseNotFound) {
    return (
      <Layout>
        <div className="mx-auto max-w-xl px-6 py-24 text-center">
          <h1 className="text-3xl font-bold mb-4">Kurs bulunamadı</h1>
          <Link to="/courses" className="text-primary story-link">← Tüm Kurslara Dön</Link>
        </div>
      </Layout>
    );
  }

  // ── Hesaplamalar ──
  const xpTotal = totalCourseXp(course);
  const hours = estimateHours(course);
  const level = deriveLevel(course);
  const completedCount = completedIds.size;
  const progressPct = allSteps.length > 0 ? Math.round((completedCount / allSteps.length) * 100) : 0;

  const activeStep = allSteps[activeIdx];
  const activeMeta = activeStep ? (STEP_META[activeStep.step_type] ?? STEP_META.theory) : STEP_META.theory;

  // Sidebar için section → adım eşleştirmesi
  let gIdx = 0;
  const sectionsWithIdx = course.sections.map((sec) => ({
    ...sec,
    startIdx: (() => { const s = gIdx; gIdx += sec.steps.length; return s; })(),
  }));

  // Bu adım kullanıcıya açık mı?
  const isUnlocked = (idx: number) => !!user || idx < FREE_STEPS;

  return (
    <Layout>

      {/* ═══ HERO ════════════════════════════════════════ */}
      <div className="border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <Link to="/courses" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-5 story-link">
            <ArrowLeft className="h-3.5 w-3.5" /> Tüm Kurslar
          </Link>

          <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge variant="outline">{level}</Badge>
                <Badge variant="secondary">{course.language}</Badge>
                <Badge className="bg-[image:var(--gradient-primary)] text-primary-foreground border-0">
                  <Zap className="mr-1 h-3 w-3" /> {xpTotal} XP
                </Badge>
              </div>
              <h1 className="text-3xl font-bold text-foreground leading-tight">{course.title}</h1>
              <p className="mt-2 text-muted-foreground max-w-xl leading-relaxed">{course.description}</p>
              <div className="mt-4 flex flex-wrap items-center gap-5 text-sm text-muted-foreground">
                <span className="flex items-center gap-1.5"><Clock className="h-4 w-4" /> {hours} saat</span>
                <span className="flex items-center gap-1.5"><BookOpen className="h-4 w-4" /> {allSteps.length} adım</span>
                <span className="flex items-center gap-1.5"><Trophy className="h-4 w-4" /> {course.sections.length} bölüm</span>
                {!user && (
                  <span className="text-amber-600 dark:text-amber-400 flex items-center gap-1.5 font-medium">
                    <Lock className="h-4 w-4" /> İlk {FREE_STEPS} adım ücretsiz
                  </span>
                )}
              </div>
            </div>

            {/* Progress kartı */}
            <Card className="p-6 min-w-[220px] text-center shrink-0">
              <div className="text-4xl font-bold text-primary mb-1">{progressPct}%</div>
              <div className="text-xs text-muted-foreground mb-3">tamamlandı</div>
              <Progress value={progressPct} className="h-2.5" />
              <div className="mt-2.5 text-xs text-muted-foreground">{completedCount}/{allSteps.length} adım</div>
            </Card>
          </div>
        </div>
      </div>

      {/* ═══ BODY ════════════════════════════════════════ */}
      <div className="mx-auto max-w-7xl px-4 lg:px-6 py-8">
        <div className="grid gap-6 lg:grid-cols-[300px_1fr] items-start">

          {/* ── SOL PANEL — adım listesi ── */}
          <aside className="lg:sticky lg:top-4 space-y-1 bg-card rounded-2xl border border-border p-3 shadow-sm">
            <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
              İçerik ({allSteps.length} adım)
            </div>
            {sectionsWithIdx.map((sec) => (
              <div key={sec.id} className="mb-1">
                <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground/60">
                  {sec.title}
                </div>
                <div className="space-y-0.5">
                  {sec.steps.map((step, i) => {
                    const globalIdx = sec.startIdx + i;
                    const meta = STEP_META[step.step_type] ?? STEP_META.theory;
                    const done = completedIds.has(step.id);
                    const active = globalIdx === activeIdx;
                    const locked = !isUnlocked(globalIdx);

                    return (
                      <button
                        key={step.id}
                        onClick={() => !locked && setActiveIdx(globalIdx)}
                        disabled={locked}
                        className={`w-full text-left rounded-xl px-3 py-2.5 flex items-center gap-3 text-sm transition-all
                          ${active
                            ? "bg-primary text-primary-foreground shadow-sm font-medium"
                            : done
                            ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-500/15"
                            : locked
                            ? "opacity-50 cursor-not-allowed text-muted-foreground"
                            : "hover:bg-accent text-muted-foreground hover:text-foreground"
                          }`}
                      >
                        {/* Adım ikonu */}
                        <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs
                          ${active ? "bg-white/20" : done ? "bg-emerald-500/20" : locked ? "bg-muted" : meta.bg}`}>
                          {done
                            ? <CheckCircle className={`h-4 w-4 ${active ? "text-white" : "text-emerald-500"}`} />
                            : locked
                            ? <Lock className="h-3 w-3 text-muted-foreground/50" />
                            : <meta.icon className={`h-3.5 w-3.5 ${active ? "text-white" : meta.color}`} />
                          }
                        </div>
                        <span className="flex-1 truncate text-sm">{step.title}</span>
                        <span className={`text-[11px] shrink-0 font-medium ${active ? "text-white/70" : "text-muted-foreground"}`}>
                          +{step.xp_reward}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </aside>

          {/* ── SAĞ PANEL — adım içeriği ── */}
          <div className="min-w-0">
            {!activeStep ? (
              /* Başlangıç */
              <Card className="p-12 text-center">
                <PlayCircle className="mx-auto h-14 w-14 text-primary mb-4 opacity-80" />
                <h3 className="text-2xl font-bold mb-2">Öğrenmeye Başla</h3>
                <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
                  Soldaki listeden bir adım seç veya aşağıdan başla.
                </p>
                <Button onClick={() => setActiveIdx(0)} size="lg"
                  className="bg-[image:var(--gradient-primary)] text-primary-foreground">
                  İlk Adımdan Başla <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Card>
            ) : !isUnlocked(activeIdx) ? (
              /* Kilitli */
              <LockedContent />
            ) : (
              /* Adım içeriği */
              <Card className="overflow-hidden">
                {/* Adım başlığı */}
                <div className={`px-6 md:px-8 py-5 border-b border-border ${activeMeta.bg}`}>
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <div className="flex items-center gap-3">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-xl border ${activeMeta.border} ${activeMeta.bg}`}>
                        <activeMeta.icon className={`h-5 w-5 ${activeMeta.color}`} />
                      </div>
                      <div>
                        <div className={`text-[11px] font-bold uppercase tracking-widest mb-0.5 ${activeMeta.color}`}>
                          {activeMeta.label} · Adım {activeIdx + 1}/{allSteps.length}
                        </div>
                        <h2 className="text-xl font-bold text-foreground">{activeStep.title}</h2>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-sm shrink-0">
                      <Zap className={`mr-1 h-3.5 w-3.5 ${activeMeta.color}`} />
                      +{activeStep.xp_reward} XP
                    </Badge>
                  </div>
                </div>

                {/* Adım gövdesi */}
                <div className="p-6 md:p-8">
                  {activeStep.step_type === "theory" && (
                    <TheoryStep step={activeStep} />
                  )}
                  {activeStep.step_type === "quiz" && (
                    <QuizStep step={activeStep} onCorrect={goNext} />
                  )}
                  {activeStep.step_type === "code" && (
                    <CodeStep step={activeStep} onComplete={goNext} />
                  )}

                  {/* Navigasyon — sadece theory için (quiz/code kendi butonlarını yönetiyor) */}
                  {activeStep.step_type === "theory" && (
                    <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
                      <Button variant="outline" disabled={activeIdx === 0}
                        onClick={() => setActiveIdx(activeIdx - 1)}>
                        <ArrowLeft className="mr-2 h-4 w-4" /> Önceki
                      </Button>
                      <Button onClick={goNext}
                        className="bg-[image:var(--gradient-primary)] text-primary-foreground">
                        {activeIdx === allSteps.length - 1
                          ? <><Trophy className="mr-2 h-4 w-4" /> Kursu Tamamla</>
                          : <>Anladım, Devam Et <ArrowRight className="ml-2 h-4 w-4" /></>
                        }
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            )}
          </div>

        </div>
      </div>
    </Layout>
  );
}
