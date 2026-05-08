import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Layout } from "@/components/site/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { SubmissionStatusResponse } from "@/lib/api-types";
import {
  LogOut, Mail, Star, ShieldCheck, Terminal, History,
  CheckCircle, XCircle, Clock,
} from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/profile")({
  component: ProfilePage,
  head: () => ({ meta: [{ title: "Profile — Lumina" }] }),
});

function ProfilePage() {
  const { user, loading: authLoading, signOut } = useAuth();
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState<SubmissionStatusResponse[]>([]);
  const [loadingSubs, setLoadingSubs] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) navigate({ to: "/login" });
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (!user) return;
    (async () => {
      try {
        const data = await api.get<SubmissionStatusResponse[]>(
          "/execution/all-submissions?limit=30"
        );
        setSubmissions(data);
      } catch {
        // submissions tablosu bos olabilir
      } finally {
        setLoadingSubs(false);
      }
    })();
  }, [user]);

  const handleSignOut = async () => {
    await signOut();
    toast.success("Signed out");
    navigate({ to: "/" });
  };

  if (authLoading) {
    return (
      <Layout>
        <div className="p-12 text-center text-muted-foreground">Loading…</div>
      </Layout>
    );
  }

  if (!user) return null;

  return (
    <Layout>
      <div className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-3xl font-bold text-foreground">Your profile</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Manage your Lumina account.
        </p>

        {/* Info card */}
        <Card className="mt-8 p-8 animate-fade-in-up">
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-2xl font-bold text-primary-foreground">
              {user.email.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-lg font-semibold text-foreground">
                {user.email.split("@")[0]}
              </div>
              <div className="text-sm text-muted-foreground flex items-center gap-1">
                <Mail className="h-3 w-3" /> {user.email}
              </div>
            </div>
          </div>

          <div className="mt-8 space-y-3">
            <div className="flex items-center justify-between border-t border-border pt-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                <span className="text-sm text-muted-foreground">Account status</span>
              </div>
              <Badge variant={user.is_active ? "secondary" : "outline"}>
                {user.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            <div className="flex items-center justify-between border-t border-border pt-4">
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-amber-500" />
                <span className="text-sm text-muted-foreground">Subscription</span>
              </div>
              <Badge
                className={user.is_premium ? "bg-[image:var(--gradient-primary)] text-primary-foreground" : ""}
                variant={user.is_premium ? "default" : "outline"}
              >
                {user.is_premium ? "Premium" : "Free"}
              </Badge>
            </div>
            {user.is_superuser && (
              <div className="flex items-center justify-between border-t border-border pt-4">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-primary" />
                  <span className="text-sm text-muted-foreground">Role</span>
                </div>
                <Badge variant="default">Admin</Badge>
              </div>
            )}
            <div className="flex items-center justify-between border-t border-border pt-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Joined</span>
              </div>
              <span className="text-sm">
                {new Date(user.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div className="mt-8 border-t border-border pt-6">
            <Button onClick={handleSignOut} variant="outline" className="w-full">
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </Button>
          </div>
        </Card>

        {/* Submission History */}
        <div className="mt-8">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
            <History className="h-5 w-5 text-primary" /> Kod Denemeleri
          </h2>
          <Card className="overflow-hidden">
            {loadingSubs && <div className="p-6 text-center text-sm text-muted-foreground">Yükleniyor...</div>}
            {!loadingSubs && submissions.length === 0 && (
              <div className="p-6 text-center text-sm text-muted-foreground">
                Henüz kod denemen yok. Bir kursa git ve kod yazmaya başla!
              </div>
            )}
            {submissions.length > 0 && (
              <div className="divide-y divide-border">
                {submissions.map((s) => (
                  <div key={s.submission_id} className="p-4 hover:bg-accent/40 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                        s.verdict === "pass" ? "bg-emerald-500/10 text-emerald-400"
                          : s.verdict === "wrong_answer" ? "bg-red-500/10 text-red-400"
                          : s.verdict === "runtime_error" || s.verdict === "timeout" ? "bg-red-500/10 text-red-400"
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
                        <p className="text-xs text-muted-foreground mt-0.5 truncate font-mono">
                          {s.code?.slice(0, 100)}
                        </p>
                      </div>
                      {s.created_at && (
                        <span className="text-xs text-muted-foreground shrink-0">
                          {new Date(s.created_at).toLocaleTimeString("tr-TR", {
                            hour: "2-digit", minute: "2-digit",
                          })}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </Layout>
  );
}
