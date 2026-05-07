import { useEffect, useRef, useState } from "react";

export function AnimatedCounter({ value, suffix = "", duration = 1800 }: { value: number; suffix?: string; duration?: number }) {
  const [n, setN] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting && !started.current) {
          started.current = true;
          const start = performance.now();
          const tick = (now: number) => {
            const p = Math.min(1, (now - start) / duration);
            setN(Math.floor(value * (1 - Math.pow(1 - p, 3))));
            if (p < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      });
    }, { threshold: 0.3 });
    obs.observe(el);
    return () => obs.disconnect();
  }, [value, duration]);

  const formatted = n >= 1_000_000 ? `${(n / 1_000_000).toFixed(0)}M` : n >= 1000 ? `${(n / 1000).toFixed(0)}K` : `${n}`;
  return <span ref={ref}>{formatted}{suffix}</span>;
}
