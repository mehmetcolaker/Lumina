import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Layout } from "@/components/site/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { SubmissionStatusResponse, UserBadgesResponse } from "@/lib/api-types";
import {
  LogOut,
  Mail,
  Star,
  ShieldCheck,
  Terminal,
  History,
  CheckCircle,
  XCircle,
  Clock,
  Award,
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
  const [badges, setBadges] = useState<UserBadgesResponse | null>(null);

  useEffect(() => {
    if (!authLoading && !user) navigate({ to: "/login" });
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (!user) return;
    (async () => {
      try {
        const data = await api.get<SubmissionStatusResponse[]>(
          "/execution/all-submissions?limit=30",
        );
        setSubmissions(data);
      } catch {
        // empty
      } finally {
        setLoadingSubs(false);
      }
    })();
    (async () => {
      try {
        const b = await api.get<UserBadgesResponse>("/gamification/badges");
        setBadges(b);
      } catch {
        /* empty */
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
        <p className="mt-2 text-sm text-muted-foreground">Manage your Lumina account.</p>

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
                className={
                  user.is_premium
                    ? "bg-[image:var(--gradient-primary)] text-primary-foreground"
                    : ""
                }
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
              <span className="text-sm">{new Date(user.created_at).toLocaleDateString()}</span>
            </div>
          </div>

          {/* Badge vitrini */}
          {badges && (
            <div className="mt-8 border-t border-border pt-6">
              <h3 className="text-lg font-bold flex items-center gap-2 mb-4">
                <Award className="h-5 w-5 text-primary" /> Rozetler
                <span className="text-sm font-normal text-muted-foreground">
                  ({badges.owned.length}/{badges.owned.length + badges.locked.length})
                </span>
              </h3>
              <div className="flex flex-wrap gap-2">
                {badges.owned.map((b) => (
                  <div
                    key={b.badge_type}
                    className="flex items-center gap-2 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-600/10 border border-amber-500/30 px-3 py-2 text-sm"
                    title={b.description ?? ""}
                  >
                    <span className="text-lg">{getEmoji(b.emoji)}</span>
                    <span className="font-medium text-amber-700 dark:text-amber-300">
                      {b.title}
                    </span>
                  </div>
                ))}
                {/* Locked badges dimmed */}
                {badges.locked.slice(0, 6).map((b) => (
                  <div
                    key={b.badge_type}
                    className="flex items-center gap-2 rounded-xl bg-muted/30 border border-border px-3 py-2 text-sm opacity-40"
                    title={b.description ?? ""}
                  >
                    <span className="text-lg">?</span>
                    <span className="text-muted-foreground">{b.title}</span>
                  </div>
                ))}
                {badges.locked.length > 6 && (
                  <div className="flex items-center text-xs text-muted-foreground px-2">
                    +{badges.locked.length - 6} daha
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="mt-8 border-t border-border pt-6">
            <Button onClick={handleSignOut} variant="outline" className="w-full">
              <LogOut className="mr-2 h-4 w-4" /> Sign out
            </Button>
          </div>
        </Card>

        {/* Submission History */}
        <div className="mt-8">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
            <History className="h-5 w-5 text-primary" /> Kod Denemeleri
          </h2>
          <Card className="overflow-hidden">
            {loadingSubs && (
              <div className="p-6 text-center text-sm text-muted-foreground">Yukleniyor...</div>
            )}
            {!loadingSubs && submissions.length === 0 && (
              <div className="p-6 text-center text-sm text-muted-foreground">
                Henuz kod denemen yok.
              </div>
            )}
            {submissions.length > 0 && (
              <div className="divide-y divide-border">
                {submissions.map((s) => (
                  <div key={s.submission_id} className="p-4 hover:bg-accent/40 transition-colors">
                    <div className="flex items-center gap-3">...</div>
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

function getEmoji(key: string): string {
  const map: Record<string, string> = {
    star: "\u2B50",
    flame: "\uD83D\uDD25",
    crown: "\uD83D\uDC51",
    zap: "\u26A1",
    gem: "\uD83D\uDC8E",
    trophy: "\uD83C\uDFC6",
    target: "\uD83C\uDFAF",
    "graduation-cap": "\uD83C\uDF93",
    snake: "\uD83D\uDC0D",
    database: "\uD83D\uDCC1",
    code: "\uD83D\uDCBB",
    brain: "\uD83E\uDDE0",
    rocket: "\uD83D\uDE80",
  };
  return map[key] ?? "\uD83C\uDFC5";
}
