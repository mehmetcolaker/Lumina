import { Link, useNavigate, useLocation } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import {
  Sparkles, Menu, X, Moon, Sun, User as UserIcon, LogOut,
  Trophy, BookOpen, LayoutDashboard, Info, Bell,
} from "lucide-react";
import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useTheme } from "@/hooks/useTheme";
import { api } from "@/lib/api";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import type { NotificationResponse } from "@/lib/api-types";

const links = [
  { to: "/courses", label: "Courses", icon: BookOpen },
  { to: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/about", label: "About", icon: Info },
] as const;

export function Navbar() {
  const [open, setOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const { user, signOut } = useAuth();
  const { theme, toggle } = useTheme();
  const navigate = useNavigate();
  const loc = useLocation();

  const { data: unread } = useQuery<{ count: number }>({
    queryKey: ["notif-count"],
    queryFn: () => api.get("/notifications/unread-count"),
    enabled: !!user,
    refetchInterval: 30_000,
  });

  const { data: notifications, refetch: refetchNotifs } = useQuery<NotificationResponse[]>({
    queryKey: ["notifications"],
    queryFn: () => api.get("/notifications/?limit=10"),
    enabled: !!user,
  });

  const markAllRead = async () => {
    await api.post("/notifications/read-all");
    refetchNotifs();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[image:var(--gradient-primary)] text-primary-foreground shadow-[var(--shadow-soft)] transition-transform duration-500 group-hover:rotate-[20deg] group-hover:scale-110">
            <Sparkles className="h-4 w-4 animate-pulse" />
          </div>
          <span className="text-xl font-bold tracking-tight text-foreground">Lumina</span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          {links.map((l) => {
            const active = loc.pathname.startsWith(l.to);
            return (
              <Link
                key={l.to}
                to={l.to}
                className={`story-link text-sm font-medium transition-colors ${active ? "text-foreground" : "text-muted-foreground hover:text-foreground"}`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme" className="hover-scale">
            {theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </Button>

          {user ? (
            <>
              {/* Notification bell */}
              <div className="relative">
                <Button variant="ghost" size="icon" onClick={() => setNotifOpen(!notifOpen)} className="hover-scale">
                  <Bell className="h-4 w-4" />
                  {(unread?.count ?? 0) > 0 && (
                    <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                      {unread!.count > 9 ? "9+" : unread!.count}
                    </span>
                  )}
                </Button>
                {/* Notification dropdown */}
                {notifOpen && (
                  <div className="absolute right-0 mt-2 w-80 rounded-xl border border-border bg-card shadow-lg animate-scale-in overflow-hidden z-50">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                      <span className="text-sm font-semibold">Bildirimler</span>
                      <button onClick={markAllRead} className="text-xs text-primary hover:underline">
                        Tümünü okundu işaretle
                      </button>
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                      {(!notifications || notifications.length === 0) && (
                        <div className="p-6 text-center text-xs text-muted-foreground">
                          Henüz bildirim yok.
                        </div>
                      )}
                      {notifications?.map((n) => (
                        <div
                          key={n.id}
                          className={`px-4 py-3 border-b border-border/50 hover:bg-accent/40 cursor-pointer text-sm ${
                            !n.is_read ? "bg-primary/5" : ""
                          }`}
                          onClick={() => {
                            api.post(`/notifications/${n.id}/read`).catch(() => {});
                            if (n.link) navigate({ to: n.link as any });
                            setNotifOpen(false);
                          }}
                        >
                          <div className="font-medium text-xs text-primary">{n.type}</div>
                          <div className="text-sm text-foreground">{n.title}</div>
                          {n.body && <div className="text-xs text-muted-foreground mt-0.5">{n.body}</div>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="gap-2 hover-scale">
                    <UserIcon className="h-4 w-4" /> <span className="hidden sm:inline">{user.email?.split("@")[0]}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="animate-scale-in">
                  <DropdownMenuItem onClick={() => navigate({ to: "/dashboard" })}>
                    <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate({ to: "/profile" })}>
                    <UserIcon className="mr-2 h-4 w-4" /> Profile
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => signOut()}>
                    <LogOut className="mr-2 h-4 w-4" /> Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" className="hidden sm:inline-flex" onClick={() => navigate({ to: "/login" })}>
                Log in
              </Button>
              <Button
                size="sm"
                onClick={() => navigate({ to: "/signup" })}
                className="bg-[image:var(--gradient-primary)] text-primary-foreground shadow-[var(--shadow-soft)] transition-all hover:opacity-90 hover:-translate-y-0.5 hover:shadow-lg glow-on-hover"
              >
                Sign up
              </Button>
            </>
          )}

          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setOpen(!open)} aria-label="Menu">
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {open && (
        <div className="border-t border-border bg-background md:hidden animate-fade-in">
          <nav className="flex flex-col gap-1 px-6 py-4">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground"
              >
                <l.icon className="h-4 w-4" /> {l.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
