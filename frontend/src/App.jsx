import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import {
  Activity,
  ArrowUpRight,
  CalendarCheck,
  CheckCircle2,
  Clock3,
  MinusCircle,
  Sparkles,
  TriangleAlert,
  Trophy
} from "lucide-react";

import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";

const cardMotion = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 }
};
const THEME_STORAGE_KEY = "student_dashboard_theme";

function ThemeSwitch({ checked, onChange }) {
  return (
    <label className="theme-switch" aria-label="Toggle dark mode">
      <input type="checkbox" className="theme-switch__checkbox" checked={checked} onChange={onChange} />
      <div className="theme-switch__container">
        <div className="theme-switch__clouds" />
        <div className="theme-switch__stars-container">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144 55" fill="none">
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M135.831 3.00688C135.055 3.85027 134.111 4.29946 133 4.35447C134.111 4.40947 135.055 4.85867 135.831 5.71123C136.607 6.55462 136.996 7.56303 136.996 8.72727C136.996 7.95722 137.172 7.25134 137.525 6.59129C137.886 5.93124 138.372 5.39954 138.98 5.00535C139.598 4.60199 140.268 4.39114 141 4.35447C139.88 4.2903 138.936 3.85027 138.16 3.00688C137.384 2.16348 136.996 1.16425 136.996 0C136.996 1.16425 136.607 2.16348 135.831 3.00688ZM31 23.3545C32.1114 23.2995 33.0551 22.8503 33.8313 22.0069C34.6075 21.1635 34.9956 20.1642 34.9956 19C34.9956 20.1642 35.3837 21.1635 36.1599 22.0069C36.9361 22.8503 37.8798 23.2903 39 23.3545C38.2679 23.3911 37.5976 23.602 36.9802 24.0053C36.3716 24.3995 35.8864 24.9312 35.5248 25.5913C35.172 26.2513 34.9956 26.9572 34.9956 27.7273C34.9956 26.563 34.6075 25.5546 33.8313 24.7112C33.0551 23.8587 32.1114 23.4095 31 23.3545ZM0 36.3545C1.11136 36.2995 2.05513 35.8503 2.83131 35.0069C3.6075 34.1635 3.99559 33.1642 3.99559 32C3.99559 33.1642 4.38368 34.1635 5.15987 35.0069C5.93605 35.8503 6.87982 36.2903 8 36.3545C7.26792 36.3911 6.59757 36.602 5.98015 37.0053C5.37155 37.3995 4.88644 37.9312 4.52481 38.5913C4.172 39.2513 3.99559 39.9572 3.99559 40.7273C3.99559 39.563 3.6075 38.5546 2.83131 37.7112C2.05513 36.8587 1.11136 36.4095 0 36.3545ZM56.8313 24.0069C56.0551 24.8503 55.1114 25.2995 54 25.3545C55.1114 25.4095 56.0551 25.8587 56.8313 26.7112C57.6075 27.5546 57.9956 28.563 57.9956 29.7273C57.9956 28.9572 58.172 28.2513 58.5248 27.5913C58.8864 26.9312 59.3716 26.3995 59.9802 26.0053C60.5976 25.602 61.2679 25.3911 62 25.3545C60.8798 25.2903 59.9361 24.8503 59.1599 24.0069C58.3837 23.1635 57.9956 22.1642 57.9956 21C57.9956 22.1642 57.6075 23.1635 56.8313 24.0069ZM81 25.3545C82.1114 25.2995 83.0551 24.8503 83.8313 24.0069C84.6075 23.1635 84.9956 22.1642 84.9956 21C84.9956 22.1642 85.3837 23.1635 86.1599 24.0069C86.9361 24.8503 87.8798 25.2903 89 25.3545C88.2679 25.3911 87.5976 25.602 86.9802 26.0053C86.3716 26.3995 85.8864 26.9312 85.5248 27.5913C85.172 28.2513 84.9956 28.9572 84.9956 29.7273C84.9956 28.563 84.6075 27.5546 83.8313 26.7112C83.0551 25.8587 82.1114 25.4095 81 25.3545ZM136 36.3545C137.111 36.2995 138.055 35.8503 138.831 35.0069C139.607 34.1635 139.996 33.1642 139.996 32C139.996 33.1642 140.384 34.1635 141.16 35.0069C141.936 35.8503 142.88 36.2903 144 36.3545C143.268 36.3911 142.598 36.602 141.98 37.0053C141.372 37.3995 140.886 37.9312 140.525 38.5913C140.172 39.2513 139.996 39.9572 139.996 40.7273C139.996 39.563 139.607 38.5546 138.831 37.7112C138.055 36.8587 137.111 36.4095 136 36.3545ZM101.831 49.0069C101.055 49.8503 100.111 50.2995 99 50.3545C100.111 50.4095 101.055 50.8587 101.831 51.7112C102.607 52.5546 102.996 53.563 102.996 54.7273C102.996 53.9572 103.172 53.2513 103.525 52.5913C103.886 51.9312 104.372 51.3995 104.98 51.0053C105.598 50.602 106.268 50.3911 107 50.3545C105.88 50.2903 104.936 49.8503 104.16 49.0069C103.384 48.1635 102.996 47.1642 102.996 46C102.996 47.1642 102.607 48.1635 101.831 49.0069Z"
              fill="currentColor"
            />
          </svg>
        </div>
        <div className="theme-switch__circle-container">
          <div className="theme-switch__sun-moon-container">
            <div className="theme-switch__moon">
              <div className="theme-switch__spot" />
              <div className="theme-switch__spot" />
              <div className="theme-switch__spot" />
            </div>
          </div>
        </div>
      </div>
    </label>
  );
}

function shortDate(dateStr) {
  if (!dateStr) {
    return "-";
  }
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) {
    return dateStr;
  }
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function statusMeta(label) {
  if (label === "Good") {
    return {
      icon: CheckCircle2,
      tone: "text-emerald-700 bg-emerald-50 border-emerald-200",
      chip: "text-emerald-700 bg-emerald-100"
    };
  }
  if (label === "Average") {
    return {
      icon: MinusCircle,
      tone: "text-amber-700 bg-amber-50 border-amber-200",
      chip: "text-amber-700 bg-amber-100"
    };
  }
  return {
    icon: TriangleAlert,
    tone: "text-rose-700 bg-rose-50 border-rose-200",
    chip: "text-rose-700 bg-rose-100"
  };
}

function SkeletonBlock({ className = "" }) {
  return <div className={`animate-pulseSoft rounded-2xl bg-white/70 ${className}`} />;
}

function FloatingInput({ id, label, defaultValue, ...props }) {
  return (
    <div className="relative">
      <Input
        id={id}
        defaultValue={defaultValue}
        placeholder=" "
        className="themed-field peer border-cyan-500/45 bg-gradient-to-r from-cyan-50 via-teal-50 to-orange-50 pt-5 text-cyan-900 shadow-[0_8px_18px_rgba(13,148,136,0.14)] focus-visible:border-teal-500 focus-visible:ring-teal-500"
        {...props}
      />
      <Label
        htmlFor={id}
        className="themed-label pointer-events-none absolute left-3 top-2 -translate-y-0 bg-white/60 px-1 text-[10px] font-semibold uppercase tracking-wide text-cyan-700 transition-all peer-placeholder-shown:top-1/2 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:text-xs peer-focus:top-2 peer-focus:translate-y-0 peer-focus:text-[10px] peer-focus:text-teal-700"
      >
        {label}
      </Label>
    </div>
  );
}

function FloatingSelect({ label, value, onValueChange, options }) {
  return (
    <div className="relative">
      <div className="themed-label pointer-events-none absolute left-3 top-2 z-20 bg-white/80 px-1 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="themed-field h-12 border-cyan-500/45 bg-gradient-to-r from-cyan-50 via-teal-50 to-orange-50 pt-4 text-cyan-900 shadow-[0_8px_18px_rgba(13,148,136,0.14)] focus:border-teal-500 focus:ring-teal-500 data-[placeholder]:text-cyan-700/70">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function TrendTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) {
    return null;
  }
  return (
    <div className="rounded-xl border border-white/60 bg-slate-900 px-3 py-2 text-xs text-white shadow-lg">
      <p className="mb-1 font-semibold">{label}</p>
      <p>Predicted Score: {payload[0].value}%</p>
    </div>
  );
}

export default function App({ payload }) {
  const [ready, setReady] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }
    const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (saved) {
      return saved === "dark";
    }
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  });
  const [selects, setSelects] = useState({
    gender: payload.defaults.gender,
    extracurricular: payload.defaults.extracurricular,
    internet_access: payload.defaults.internet_access,
    parental_education: payload.defaults.parental_education
  });

  useEffect(() => {
    const timer = window.setTimeout(() => setReady(true), 420);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(THEME_STORAGE_KEY, isDark ? "dark" : "light");
    }
  }, [isDark]);

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    document.documentElement.classList.toggle("site-dark-mode", isDark);
    document.body.classList.toggle("site-dark-mode", isDark);
  }, [isDark]);

  const chartPoints = useMemo(() => {
    return (payload.allPredictions || []).map((item) => ({
      date: shortDate(item.date),
      score: Number(item.score || 0)
    }));
  }, [payload.allPredictions]);

  const stats = useMemo(
    () => [
      {
        label: "Total Predictions",
        value: payload.stats.totalPredictions,
        Icon: Activity,
        chip: "bg-cyan-500/15 text-cyan-700",
        bg: "from-cyan-400 to-teal-600"
      },
      {
        label: "Latest Score",
        value: payload.stats.latestScore,
        suffix: "%",
        Icon: Trophy,
        chip: "bg-orange-500/15 text-orange-700",
        bg: "from-orange-400 to-rose-500"
      },
      {
        label: "Attendance",
        value: payload.stats.attendance,
        suffix: "%",
        Icon: CalendarCheck,
        chip: "bg-emerald-500/15 text-emerald-700",
        bg: "from-emerald-400 to-green-600"
      },
      {
        label: "Study Hours",
        value: payload.stats.studyHours,
        suffix: "h",
        Icon: Clock3,
        chip: "bg-blue-500/15 text-blue-700",
        bg: "from-blue-400 to-indigo-600"
      }
    ],
    [payload.stats]
  );

  const chartStroke = isDark ? "#22d3ee" : "#0f8b8d";
  const chartFill = isDark ? "#22d3ee" : "#0f8b8d";
  const chartGrid = isDark ? "rgba(148, 163, 184, 0.22)" : "rgba(31,42,49,0.12)";
  const chartAxis = isDark ? "#cbd5e1" : "#60707a";
  const chartCursor = isDark ? "#67e8f9" : "#0f8b8d";
  const handleForecastSubmit = (event) => {
    if (isSubmitting) {
      return;
    }
    event.preventDefault();
    const form = event.currentTarget;
    setIsSubmitting(true);
    window.setTimeout(() => {
      form.submit();
    }, 1200);
  };

  if (!ready) {
    return (
      <div className={`dashboard-theme-shell relative w-full overflow-hidden rounded-3xl bg-hero-radial p-5 md:p-8 ${isDark ? "dashboard-theme-dark" : ""}`}>
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((item) => (
            <SkeletonBlock key={item} className="h-28" />
          ))}
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <SkeletonBlock className="h-[420px]" />
          <div className="grid gap-4">
            <SkeletonBlock className="h-[250px]" />
            <SkeletonBlock className="h-[150px]" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`dashboard-theme-shell relative w-full overflow-hidden rounded-3xl border border-white/50 bg-hero-radial p-5 md:p-8 ${isDark ? "dashboard-theme-dark" : ""}`}>
      {isSubmitting ? (
        <div className="forecast-loader-overlay">
          <div className="loader">
            <div data-glitch="Loading..." className="glitch">
              Loading...
            </div>
          </div>
        </div>
      ) : null}

      <div className="pointer-events-none absolute -right-24 top-6 h-72 w-72 rounded-full bg-cyan-400/35 blur-3xl" />
      <div className="pointer-events-none absolute -left-24 bottom-8 h-72 w-72 rounded-full bg-orange-300/35 blur-3xl" />
      <div className="pointer-events-none absolute left-1/3 top-1/2 h-64 w-64 -translate-y-1/2 rounded-full bg-sky-300/25 blur-3xl" />

      <motion.section
        className="relative z-10 mb-6 flex flex-wrap items-end justify-between gap-4"
        initial="hidden"
        animate="show"
        variants={cardMotion}
        transition={{ duration: 0.45 }}
      >
        <div>
          <p className="mb-2 inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
            <Sparkles className="h-3.5 w-3.5 text-cyan-700" />
            Smart Dashboard
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
            Hi {payload.firstName}, own your next score sprint.
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-600 md:text-base">
            Recalibrate your weekly plan with prediction signals, trend confidence, and action-ready study targets.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <ThemeSwitch checked={isDark} onChange={(e) => setIsDark(e.target.checked)} />
          <span className="rounded-full border border-white/60 bg-white/65 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700">
            {payload.className || "Class Not Set"}
          </span>
          <span className="rounded-full border border-white/60 bg-white/65 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700">
            Section {payload.section || "A"}
          </span>
        </div>
      </motion.section>

      <motion.section
        className="relative z-10 mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4"
        initial="hidden"
        animate="show"
        transition={{ staggerChildren: 0.06 }}
      >
        {stats.map((stat) => {
          const Icon = stat.Icon;
          return (
            <motion.div key={stat.label} variants={cardMotion}>
              <Card className="theme-card group border-white/65 bg-white/70 p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-glow">
                <div className="mb-3 flex items-start justify-between">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{stat.label}</p>
                  <div className={`inline-flex items-center rounded-full px-2 py-1 text-[11px] font-semibold ${stat.chip}`}>
                    +trend
                  </div>
                </div>
                <div className="flex items-end justify-between gap-3">
                  <p className="text-3xl font-extrabold tracking-tight text-slate-900">{typeof stat.value === "number" ? `${stat.value}${stat.suffix || ""}` : "--"}</p>
                  <div className={`grid h-12 w-12 place-content-center rounded-2xl bg-gradient-to-br ${stat.bg} text-white shadow-lg`}>
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </motion.section>

      <section className="relative z-10 grid gap-4 xl:grid-cols-[1.35fr_1fr]">
        <motion.div initial="hidden" animate="show" variants={cardMotion} transition={{ duration: 0.45, delay: 0.1 }}>
          <Card className="theme-card h-full border-white/70 bg-white/74">
            <CardHeader className="mr-auto w-full max-w-4xl pb-3">
              <CardTitle className="text-lg">Prediction Studio</CardTitle>
              <CardDescription>Complete your current indicators and generate a new exam forecast.</CardDescription>
            </CardHeader>
            <CardContent className="mr-auto w-full max-w-4xl">
              <form action={payload.formAction} method="POST" className="space-y-4" onSubmit={handleForecastSubmit}>
                <input type="hidden" name="csrf_token" value={payload.csrfToken} />
                <input type="hidden" name="gender" value={selects.gender} />
                <input type="hidden" name="extracurricular" value={selects.extracurricular} />
                <input type="hidden" name="internet_access" value={selects.internet_access} />
                <input type="hidden" name="parental_education" value={selects.parental_education} />

                <div className="grid gap-3 md:grid-cols-2">
                  <FloatingInput id="class_name" label="Current Class" defaultValue={payload.className || "Class Not Set"} disabled />
                  <FloatingInput id="section" label="Section" defaultValue={`Section ${payload.section || "A"}`} disabled />
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <FloatingInput id="attendance" name="attendance" label="Attendance (%)" type="number" min="0" max="100" step="0.1" required />
                  <FloatingInput id="study_hours" name="study_hours" label="Weekly Study Hours" type="number" min="0" max="168" step="1" required />
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <FloatingInput id="previous_marks" name="previous_marks" label="Previous Exam Score" type="number" min="0" max="100" step="0.1" required />
                  <FloatingSelect
                    label="Gender"
                    value={selects.gender}
                    onValueChange={(value) => setSelects((prev) => ({ ...prev, gender: value }))}
                    options={["Male", "Female"]}
                  />
                </div>

                <div className="grid gap-3 md:grid-cols-3">
                  <FloatingSelect
                    label="Extracurriculars"
                    value={selects.extracurricular}
                    onValueChange={(value) => setSelects((prev) => ({ ...prev, extracurricular: value }))}
                    options={["No", "Yes"]}
                  />
                  <FloatingSelect
                    label="Internet Access"
                    value={selects.internet_access}
                    onValueChange={(value) => setSelects((prev) => ({ ...prev, internet_access: value }))}
                    options={["Yes", "No"]}
                  />
                  <FloatingSelect
                    label="Parental Education"
                    value={selects.parental_education}
                    onValueChange={(value) => setSelects((prev) => ({ ...prev, parental_education: value }))}
                    options={["High School", "Bachelors", "Masters", "PhD"]}
                  />
                </div>

                <motion.div className="w-full md:w-auto" whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}>
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="h-12 w-full md:w-[280px] bg-[length:200%_200%] bg-gradient-to-r from-cyan-600 via-teal-500 to-orange-400 text-base font-bold animate-gradient-shift shadow-[0_15px_30px_rgba(14,116,144,0.35)] hover:shadow-[0_18px_35px_rgba(14,116,144,0.5)]"
                  >
                    Run Forecast
                    <ArrowUpRight className="h-4 w-4" />
                  </Button>
                </motion.div>

                <p className="text-xs text-slate-500">
                  Predictions are guidance signals based on historical patterns, not final grades.
                </p>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        <div className="grid gap-4">
          <motion.div initial="hidden" animate="show" variants={cardMotion} transition={{ duration: 0.45, delay: 0.15 }}>
            <Card className="theme-card border-white/70 bg-white/74">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Performance Trend</CardTitle>
                <CardDescription>Smooth score curve from your prediction history.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  {chartPoints.length ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartPoints} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                        <defs>
                          <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={chartFill} stopOpacity={0.45} />
                            <stop offset="95%" stopColor={chartFill} stopOpacity={0.02} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke={chartGrid} />
                        <XAxis dataKey="date" stroke={chartAxis} tickLine={false} axisLine={false} fontSize={12} />
                        <YAxis
                          stroke={chartAxis}
                          tickLine={false}
                          axisLine={false}
                          fontSize={12}
                          domain={["dataMin - 8", 100]}
                        />
                        <Tooltip content={<TrendTooltip />} cursor={{ stroke: chartCursor, strokeWidth: 1 }} />
                        <Area
                          type="monotone"
                          dataKey="score"
                          stroke={chartStroke}
                          strokeWidth={3}
                          fill="url(#scoreFill)"
                          activeDot={{ r: 6, strokeWidth: 2, stroke: "#ffffff", fill: chartStroke }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="pt-8 text-sm text-slate-500">No trend yet. Submit your first forecast to render this graph.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial="hidden" animate="show" variants={cardMotion} transition={{ duration: 0.45, delay: 0.22 }}>
            <Card className="theme-card border-white/70 bg-white/74">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Recent Results</CardTitle>
                <CardDescription>Latest outcomes and risk flags.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {payload.recentPredictions.length ? (
                  payload.recentPredictions.slice(0, 4).map((entry) => {
                    const meta = statusMeta(entry.label);
                    const Icon = meta.icon;
                    return (
                      <div
                        key={entry.id}
                        className={`flex items-center justify-between rounded-xl border px-3 py-2 ${meta.tone}`}
                      >
                        <div className="flex items-center gap-2">
                          <Icon className="h-4 w-4" />
                          <div>
                            <p className="text-sm font-semibold leading-tight">{entry.label} Performance</p>
                            <p className="text-xs opacity-80">{shortDate(entry.date)}</p>
                          </div>
                        </div>
                        <span className={`rounded-full px-2 py-1 text-xs font-semibold ${meta.chip}`}>{entry.score}%</span>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-sm text-slate-500">No entries yet. Run your first forecast to populate recent results.</p>
                )}
                <a
                  href={payload.historyUrl}
                  className="inline-flex items-center text-sm font-semibold text-cyan-700 hover:text-cyan-800"
                >
                  View all history
                  <ArrowUpRight className="ml-1 h-4 w-4" />
                </a>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
