import React, { useState, useEffect, useMemo, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  Layers,
  ArrowUpRight,
  ArrowRight,
  Download,
  Radio,
  Search,
  ChevronDown,
  ChevronRight,
  Command,
  ShieldCheck,
  FlaskConical,
  Terminal,
  GitBranch,
  FileText,
  ChartNoAxesCombined,
  Settings2,
  Clock,
  X,
  Check,
  Copy,
  AlertTriangle,
  RefreshCw,
  Link,
  Database,
  WifiOff,
  CheckCircle2,
  Info,
  Plus,
  SlidersHorizontal,
  SquareArrowOutUpRight,
  Users,
  TrendingUp,
  TrendingDown,
  Minus,
  TriangleAlert,
} from "lucide-react";
import "./styles.css";

const PH = {
  discovery: "Descubrimiento",
  enrichment: "Enriquecimiento",
  planning: "Planificación",
  proposal: "Proposal",
  specs: "Specs",
  design: "Design",
  tasks: "Tasks",
  apply: "Implementación",
  verify: "Verificación",
  close: "Cierre",
  unassigned: "Sin fase",
};
const COMMAND_LABEL = {
  "/opsx:propose": "Propuesta OpenSpec",
  "/openspec:proposal": "Propuesta OpenSpec",
  "/opsx:apply": "Aplicar cambio",
  "/openspec:apply": "Aplicar cambio",
  "/opsx:archive": "Archivar cambio",
  "/openspec:archive": "Archivar cambio",
  "/opsx:explore": "Exploración",
  "/opsx:verify": "Verificación",
  "/opsx:new": "Nueva propuesta",
  "/opsx:continue": "Continuar propuesta",
  "/opsx:ff": "Fast-forward",
  "/opsx:update": "Actualizar propuesta",
  "/opsx:sync": "Sincronizar",
};
const SOURCE_LABEL = {
  main: "agente principal",
  subagent: "subagente",
  auxiliary: "proceso auxiliar",
};
const COL = {
  input_tokens: "#254f47",
  output_tokens: "#a0d573",
  cache_read_tokens: "#cddbc2",
  cache_creation_tokens: "#d4a96e",
};
const KEYS = Object.keys(COL);
const LABEL = {
  input_tokens: "Entrada no cacheada",
  output_tokens: "Salida",
  cache_read_tokens: "Lectura de caché",
  cache_creation_tokens: "Escritura de caché",
};
const NAV = [
  ["overview", "Vista general", ChartNoAxesCombined],
  ["sessions", "Sesiones", Terminal],
  ["tasks", "Historias de usuario", FileText],
  ["team", "Equipo", Users],
  ["phases", "Fases OpenSpec", Layers],
  ["insights", "Optimización", Activity],
  ["diagnostics", "Diagnósticos", Settings2],
];
const num = (n) => new Intl.NumberFormat("es-CO").format(n || 0);
const compact = (n) =>
  new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(n || 0);
const money = (n) =>
  n === null || n === undefined
    ? "—"
    : new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 3,
      }).format(n);
const token = (r) => KEYS.reduce((s, k) => s + (r[k] || 0), 0);
const sum = (rows, k) => rows.reduce((s, r) => s + (r[k] || 0), 0);
const total = (rows) => rows.reduce((s, r) => s + token(r), 0);
const cost = (rows) =>
  rows.some((r) => r.cost_usd !== null && r.cost_usd !== undefined)
    ? sum(rows, "cost_usd")
    : null;
const cacheRate = (rs) => {
  const inputs =
    sum(rs, "input_tokens") +
    sum(rs, "cache_read_tokens") +
    sum(rs, "cache_creation_tokens");
  return inputs ? (sum(rs, "cache_read_tokens") / inputs) * 100 : 0;
};
const median = (nums) => {
  if (!nums.length) return 0;
  const s = [...nums].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
};
// ISO week key (Mon-Sun), stable across years for grouping real timestamps only.
const isoWeek = (iso) => {
  const d = new Date(iso);
  d.setUTCHours(0, 0, 0, 0);
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
  return `${d.getUTCFullYear()}-W${String(week).padStart(2, "0")}`;
};
const shorten = (s) =>
  s?.length > 22
    ? s.slice(0, 10) + "…" + s.slice(-6)
    : s || "Sin identificador";
const date = (s) =>
  s
    ? new Date(s).toLocaleString("es-CO", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";
const group = (rs, key) =>
  Object.values(
    rs.reduce((acc, r) => {
      const id = r[key] || "";
      (acc[id] ??= { id, rows: [] }).rows.push(r);
      return acc;
    }, {}),
  );
const groupByPrompt = (rs) => {
  const order = [];
  const map = {};
  for (const r of rs) {
    if (!r.prompt_id) continue;
    const k = r.session_id + "::" + r.prompt_id;
    if (!map[k]) {
      map[k] = { key: k, id: r.prompt_id, session: r.session_id, rows: [] };
      order.push(k);
    }
    map[k].rows.push(r);
  }
  return order.map((k) => map[k]);
};
const sourceBreakdown = (rows) => {
  const counts = {};
  for (const r of rows)
    counts[r.query_source] = (counts[r.query_source] || 0) + 1;
  return counts;
};
const promptLabel = (meta, idx) => {
  if (meta?.command) return COMMAND_LABEL[meta.command] || meta.command;
  return `Turno ${idx}`;
};
const api = async (path, opts) => {
  const res = await fetch(path, opts);
  if (!res.ok) {
    let data;
    try {
      data = await res.json();
    } catch {}
    throw new Error(
      typeof data?.detail === "string" ? data.detail : `Error ${res.status}`,
    );
  }
  return res.json();
};
const post = (data, method = "POST") => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});
function Badge({ children, type = "neutral" }) {
  return <span className={"badge " + type}>{children}</span>;
}
function Empty({
  title = "Todavía no hay solicitudes",
  text = "Configura Claude Code y envía un prompt. Los eventos aparecerán aquí.",
  onDemo,
}) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <Radio size={26} />
      </div>
      <h3>{title}</h3>
      <p>{text}</p>
      {onDemo && (
        <button className="button" onClick={onDemo}>
          <FlaskConical size={16} />
          Explorar con datos demo
        </button>
      )}
    </div>
  );
}
function Breakdown({ rows, large = false }) {
  const t = total(rows);
  return (
    <div className={"breakdown " + (large ? "large" : "")}>
      <div className="stackbar">
        {KEYS.map((k) => (
          <div
            key={k}
            style={{
              width: `${t ? (sum(rows, k) / t) * 100 : 0}%`,
              background: COL[k],
            }}
            title={`${LABEL[k]}: ${num(sum(rows, k))}`}
          />
        ))}
      </div>
      <div className="legend">
        {KEYS.map((k) => (
          <div key={k}>
            <i style={{ background: COL[k] }} />
            <span>{LABEL[k]}</span>
            <b>{compact(sum(rows, k))}</b>
          </div>
        ))}
      </div>
    </div>
  );
}
function Trend({ rows }) {
  let buckets = Array(16).fill(0);
  if (rows.length) {
    const times = rows.map((r) => new Date(r.occurred_at).getTime());
    let min = Math.min(...times),
      max = Math.max(...times);
    rows.forEach((r, i) => {
      buckets[
        Math.min(
          15,
          Math.floor(((times[i] - min) / Math.max(1, max - min)) * 15),
        )
      ] += token(r);
    });
  }
  let max = Math.max(...buckets, 1);
  const points = buckets
    .map((v, i) => `${45 + i * 40},${170 - (v / max) * 132}`)
    .join(" ");
  return (
    <div className="trend">
      <div className="chart-axis">
        <span>{compact(max)}</span>
        <span>{compact(max / 2)}</span>
        <span>0</span>
      </div>
      <svg
        viewBox="0 0 680 190"
        role="img"
        aria-label="Tokens procesados por intervalo dentro del período seleccionado"
      >
        <defs>
          <linearGradient id="fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#b9dca1" stopOpacity=".55" />
            <stop offset="100%" stopColor="#b9dca1" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[38, 104, 170].map((y) => (
          <line
            key={y}
            x1="45"
            x2="645"
            y1={y}
            y2={y}
            stroke="#edf0e9"
            strokeDasharray="4 5"
          />
        ))}
        {rows.length > 0 && (
          <>
            <polygon points={`45,170 ${points} 645,170`} fill="url(#fill)" />
            <polyline
              points={points}
              fill="none"
              stroke="#43734c"
              strokeWidth="2.7"
              strokeLinejoin="round"
            />
            {buckets.map((v, i) => (
              <circle
                key={i}
                cx={45 + i * 40}
                cy={170 - (v / max) * 132}
                r="3"
                fill="#43734c"
              >
                <title>
                  {num(v)} tokens · intervalo {i + 1}
                </title>
              </circle>
            ))}
          </>
        )}
      </svg>
      <div className="chart-footer">
        <span>Inicio del período observado</span>
        <span>Última solicitud</span>
      </div>
    </div>
  );
}
function App() {
  const [source, setSource] = useState(
    localStorage.getItem("tl-source") || "real",
  );
  const sourceRef = useRef(source);
  sourceRef.current = source;
  const [page, setPage] = useState("overview"),
    [data, setData] = useState({
      requests: [],
      sessions: [],
      prompts: [],
      tools: [],
      receipts: [],
      audit: [],
      metrics: [],
      phases: Object.keys(PH),
      reconciliations: [],
    });
  const [online, setOnline] = useState(false),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [query, setQuery] = useState(""),
    [range, setRange] = useState("all"),
    [sessionId, setSessionId] = useState(""),
    [workItem, setWorkItem] = useState(""),
    [developer, setDeveloper] = useState(""),
    [repoFilter, setRepoFilter] = useState("");
  const [detail, setDetail] = useState(null),
    [binding, setBinding] = useState(null),
    [setup, setSetup] = useState(false),
    [reconcile, setReconcile] = useState(null);
  const [last, setLast] = useState(""),
    [busy, setBusy] = useState(false),
    [rankBy, setRankBy] = useState("tokens");
  const [expanded, setExpanded] = useState(() => new Set());
  const toggleExpanded = (key) =>
    setExpanded((s) => {
      const n = new Set(s);
      n.has(key) ? n.delete(key) : n.add(key);
      return n;
    });
  const refresh = async () => {
    const requested = source;
    try {
      const d = await api(`/api/dashboard?source=${requested}`);
      if (sourceRef.current !== requested) return;
      setData(d);
      setLast(new Date().toLocaleTimeString("es-CO"));
      setError("");
    } catch (e) {
      if (sourceRef.current === requested) setError(e.message);
    } finally {
      if (sourceRef.current === requested) setLoading(false);
    }
  };
  useEffect(() => {
    const saved = localStorage.getItem("tl-source");
    api("/api/health")
      .then((h) => {
        if (!h.local_only && !saved) setSource("demo");
      })
      .catch(() => {});
  }, []);
  useEffect(() => {
    localStorage.setItem("tl-source", source);
    setSessionId("");
    setWorkItem("");
    setDeveloper("");
    setRepoFilter("");
    setDetail(null);
    setLoading(true);
    refresh();
    const es = new EventSource("/api/events");
    es.onopen = () => setOnline(true);
    es.addEventListener("update", refresh);
    es.onerror = () => setOnline(false);
    const poll = setInterval(refresh, 15000);
    return () => {
      es.close();
      clearInterval(poll);
    };
  }, [source]);
  useEffect(() => {
    if (notice) {
      const timer = setTimeout(() => setNotice(""), 6000);
      return () => clearTimeout(timer);
    }
  }, [notice]);
  const run = async (fn, message) => {
    setBusy(true);
    try {
      await fn();
      await refresh();
      if (message) setNotice(message);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };
  const loadDemo = () =>
    run(async () => {
      await api("/api/demo", { method: "POST" });
      setSource("demo");
    }, "Datos sintéticos cargados. No consumen tokens.");
  const sessionRepo = useMemo(() => {
    const m = {};
    for (const s of data.sessions) m[s.id] = s.repo || "";
    return m;
  }, [data.sessions]);
  const repos = useMemo(
    () => [...new Set(data.sessions.map((s) => s.repo || ""))].sort(),
    [data.sessions],
  );
  const rows = useMemo(
    () =>
      data.requests.filter((r) => {
        const text = [
          r.work_item,
          r.change_id,
          r.session_id,
          r.model,
          r.phase,
          r.prompt_id,
        ]
          .join(" ")
          .toLowerCase();
        return (
          (!query || text.includes(query.toLowerCase())) &&
          (!sessionId || r.session_id === sessionId) &&
          (!workItem || r.work_item === workItem) &&
          (!developer || r.developer === developer) &&
          (!repoFilter || sessionRepo[r.session_id] === repoFilter) &&
          (range === "all" ||
            new Date(r.occurred_at).getTime() >
              Date.now() - (range === "24h" ? 24 : 168) * 3600000)
        );
      }),
    [data, query, range, sessionId, workItem, developer, repoFilter, sessionRepo],
  );
  const all = total(rows),
    inputs =
      sum(rows, "input_tokens") +
      sum(rows, "cache_read_tokens") +
      sum(rows, "cache_creation_tokens"),
    cache = inputs ? (sum(rows, "cache_read_tokens") / inputs) * 100 : 0;
  const phases = group(rows, "phase").sort(
    (a, b) => total(b.rows) - total(a.rows),
  );
  const tasks = group(rows, "work_item").sort(
    (a, b) => total(b.rows) - total(a.rows),
  );
  const session = data.sessions.find((s) => s.id === sessionId);
  const title = NAV.find((n) => n[0] === page)?.[1] || "Vista general";
  // Missing prompt IDs are excluded from per-turn totals, not merged into a fictitious turn.
  const prompts = groupByPrompt(rows).sort(
    (a, b) => total(b.rows) - total(a.rows),
  );
  const promptMeta = useMemo(() => {
    const m = {};
    for (const p of data.prompts) m[p.session_id + "::" + p.id] = p;
    return m;
  }, [data.prompts]);
  const sessionOrder = useMemo(() => {
    const sorted = [...data.sessions].sort(
      (a, b) => new Date(a.started_at) - new Date(b.started_at),
    );
    const m = {};
    sorted.forEach((s, i) => (m[s.id] = i + 1));
    return m;
  }, [data.sessions]);
  const teams = group(rows, "developer").sort(
    (a, b) => total(b.rows) - total(a.rows),
  );
  // Tokens spent on turns that never finished cleanly: real cost of errors/retries, not an estimate.
  const abandonedPromptKeys = new Set(
    data.prompts
      .filter((p) => p.status === "error" || p.status === "interrupted")
      .map((p) => p.session_id + "::" + p.id),
  );
  const wastedRows = rows.filter(
    (r) =>
      r.status === "error" ||
      abandonedPromptKeys.has(r.session_id + "::" + r.prompt_id),
  );
  const wastedTokens = total(wastedRows);
  const wastedPct = all ? (wastedTokens / all) * 100 : 0;
  // Median cost per turn, per HU, so a HU's total cost reads relative to its peers instead of alone.
  const taskBenchmark = {};
  {
    const withId = tasks.filter((t) => t.id);
    const perTurn = withId.map((t) => {
      const turns = new Set(t.rows.map((r) => r.session_id + "::" + r.prompt_id))
        .size;
      return turns ? (cost(t.rows) ?? 0) / turns : 0;
    });
    const med = median(perTurn);
    withId.forEach((t, i) => {
      taskBenchmark[t.id] = {
        avgTurnCost: perTurn[i],
        median: med,
        ratio: med ? perTurn[i] / med : 1,
      };
    });
  }
  // Turns costing far more than peers in the same phase (sample size >= 4 to avoid false signals).
  const outlierPrompts = [];
  {
    const byPhase = {};
    for (const p of prompts)
      (byPhase[p.rows[0].phase] ??= []).push(p);
    for (const ph in byPhase) {
      const peers = byPhase[ph];
      if (peers.length < 4) continue;
      const costs = peers.map((p) => cost(p.rows) ?? 0);
      const med = median(costs);
      if (!med) continue;
      peers.forEach((p, i) => {
        if (costs[i] >= med * 2)
          outlierPrompts.push({ ...p, medianCost: med, ratio: costs[i] / med });
      });
    }
    outlierPrompts.sort((a, b) => b.ratio - a.ratio);
  }
  // Current vs previous ISO week, from the full unfiltered capture so it's independent of the range filter.
  const weekCompare = (() => {
    const byWeek = {};
    for (const r of data.requests)
      (byWeek[isoWeek(r.occurred_at)] ??= []).push(r);
    const weeks = Object.keys(byWeek).sort();
    if (weeks.length < 2) return null;
    const cur = byWeek[weeks[weeks.length - 1]];
    const prev = byWeek[weeks[weeks.length - 2]];
    const curCost = cost(cur),
      prevCost = cost(prev);
    const curTokens = total(cur),
      prevTokens = total(prev);
    return {
      curTokens,
      prevTokens,
      curCost,
      prevCost,
      costDelta:
        prevCost !== null && prevCost !== 0
          ? ((curCost - prevCost) / prevCost) * 100
          : null,
      tokenDelta: prevTokens ? ((curTokens - prevTokens) / prevTokens) * 100 : null,
    };
  })();
  const latest = data.receipts[0];
  const promptKeys = new Set(
    rows.map((r) => r.session_id + "::" + r.prompt_id),
  );
  const visibleTools = data.tools.filter((t) =>
    promptKeys.has(t.session_id + "::" + t.prompt_id),
  );
  const exportHref = `/api/export.csv?source=${source}&range=${range}&q=${encodeURIComponent(query)}${workItem ? "&work_item=" + encodeURIComponent(workItem) : ""}${sessionId ? "&session_id=" + encodeURIComponent(sessionId) : ""}${developer ? "&developer=" + encodeURIComponent(developer) : ""}${repoFilter ? "&repo=" + encodeURIComponent(repoFilter) : ""}`;
  const go = (p) => {
    setPage(p);
    setSessionId("");
    setWorkItem("");
    setDeveloper("");
    setQuery("");
  };
  function RequestRow({ r, max, indent }) {
    return (
      <tr
        key={r.id}
        className={indent ? "request-child" : ""}
        onClick={() => setDetail(r)}
        tabIndex="0"
        onKeyDown={(e) => {
          if (e.key === "Enter") setDetail(r);
        }}
      >
        <td>
          <div className="table-primary">
            {shorten(r.request_id || r.prompt_id)}
          </div>
          <div className="table-secondary">
            {r.model.replace("claude-", "")}{" "}
            <span className="dotsep">·</span> {date(r.occurred_at)}
            {r.query_source && SOURCE_LABEL[r.query_source] && (
              <>
                {" "}
                <span className="dotsep">·</span>{" "}
                {SOURCE_LABEL[r.query_source]}
              </>
            )}
          </div>
        </td>
        <td>
          <div className="table-primary">
            {r.work_item ? "HU #" + r.work_item : "Sin HU"}{" "}
            {r.status === "error" && <Badge type="warning">Error</Badge>}
          </div>
          <div className="table-secondary">{PH[r.phase] || r.phase}</div>
        </td>
        <td>
          <div className="table-primary numeric">{num(token(r))}</div>
          <div className="mini-bar">
            <i
              style={{
                width: `${Math.max(4, (token(r) / Math.max(max, 1)) * 100)}%`,
              }}
            />
          </div>
        </td>
        <td className="numeric">{money(r.cost_usd)}</td>
        <td className="muted">{(r.duration_ms / 1000).toFixed(1)} s</td>
        <td>
          <ArrowUpRight size={16} />
        </td>
      </tr>
    );
  }
  function Requests({ list = rows, limit = 50 }) {
    const groups = groupByPrompt(list).sort(
      (a, b) =>
        new Date(b.rows[0].occurred_at) - new Date(a.rows[0].occurred_at),
    );
    const loose = list.filter((r) => !r.prompt_id);
    const rowCount = groups.length + loose.length;
    const max = Math.max(...list.map(token), 1);
    return rowCount ? (
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Solicitud / modelo</th>
              <th>HU y fase</th>
              <th>Tokens procesados</th>
              <th>Equiv. USD</th>
              <th>Duración</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {groups.slice(0, limit).map((g, i) => {
              if (g.rows.length === 1)
                return <RequestRow key={g.key} r={g.rows[0]} max={max} />;
              const meta = promptMeta[g.key];
              const isOpen = expanded.has(g.key);
              const sources = sourceBreakdown(g.rows);
              const extra = Object.keys(sources).filter(
                (s) => s !== "main" && s !== "unknown",
              );
              return (
                <React.Fragment key={g.key}>
                  <tr
                    className="group-row"
                    onClick={() => toggleExpanded(g.key)}
                    tabIndex="0"
                    onKeyDown={(e) => {
                      if (e.key === "Enter") toggleExpanded(g.key);
                    }}
                  >
                    <td>
                      <div className="table-primary">
                        {isOpen ? (
                          <ChevronDown size={14} />
                        ) : (
                          <ChevronRight size={14} />
                        )}{" "}
                        {promptLabel(meta, groups.length - i)}
                      </div>
                      <div className="table-secondary">
                        {date(g.rows[0].occurred_at)}{" "}
                        <span className="dotsep">·</span> {g.rows.length}{" "}
                        llamadas agrupadas
                        {extra.length > 0 && (
                          <>
                            {" "}
                            <span className="dotsep">·</span>{" "}
                            {extra
                              .map(
                                (s) =>
                                  `${sources[s]} de ${SOURCE_LABEL[s] || s}`,
                              )
                              .join(" · ")}
                          </>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="table-primary">
                        {g.rows[0].work_item
                          ? "HU #" + g.rows[0].work_item
                          : "Sin HU"}
                      </div>
                      <div className="table-secondary">
                        {PH[g.rows[0].phase] || g.rows[0].phase}
                      </div>
                    </td>
                    <td>
                      <div className="table-primary numeric">
                        {num(total(g.rows))}
                      </div>
                    </td>
                    <td className="numeric">{money(cost(g.rows))}</td>
                    <td className="muted">
                      {(sum(g.rows, "duration_ms") / 1000).toFixed(1)} s
                    </td>
                    <td>
                      <button
                        className="icon-button"
                        title="Ver detalle del turno"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDetail({ ...g.rows[0], _promptRows: g.rows });
                        }}
                      >
                        <ArrowUpRight size={16} />
                      </button>
                    </td>
                  </tr>
                  {isOpen &&
                    g.rows.map((r) => (
                      <RequestRow key={r.id} r={r} max={max} indent />
                    ))}
                </React.Fragment>
              );
            })}
            {loose.slice(0, limit).map((r) => (
              <RequestRow key={r.id} r={r} max={max} />
            ))}
          </tbody>
        </table>
        {rowCount > limit && (
          <div className="table-note">
            Mostrando las primeras {limit} de {rowCount}. Filtra o exporta el
            detalle completo.
          </div>
        )}
      </div>
    ) : (
      <Empty onDemo={source === "real" ? loadDemo : null} />
    );
  }
  function PhaseList() {
    return (
      <div className="phase-list">
        {phases.length ? (
          phases.map((p, i) => (
            <div className="phase-row" key={p.id}>
              <div className="phase-label">
                <span className="phase-number">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span>{PH[p.id] || p.id}</span>
                <strong>{compact(total(p.rows))}</strong>
              </div>
              <div className="phase-track">
                <div
                  style={{
                    width: `${(total(p.rows) / Math.max(all, 1)) * 100}%`,
                    background: ["#284e43", "#94bf6e", "#d1ad73", "#cad7c1"][
                      i % 4
                    ],
                  }}
                />
              </div>
              <div className="phase-sub">
                <span>{p.rows.length} solicitudes</span>
                <span>{cacheRate(p.rows).toFixed(1)}% caché</span>
                <span>
                  {Math.round((total(p.rows) / Math.max(all, 1)) * 100)}% del
                  consumo
                </span>
              </div>
            </div>
          ))
        ) : (
          <p className="muted">Las fases aparecerán con la primera captura.</p>
        )}
      </div>
    );
  }
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            go("overview");
          }}
        >
          <span className="brand-mark">
            <span />
            <span />
            <span />
          </span>
          <span>
            tokenlens<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="workspace">
          <div className="workspace-avatar">OS</div>
          <div>
            <strong>OpenSpec workspace</strong>
            <span>Piloto personal</span>
          </div>
          <ChevronDown size={14} />
        </div>
        <div className="nav-caption">OBSERVABILIDAD</div>
        <nav>
          {NAV.map(([id, label, Icon]) => (
            <button
              key={id}
              className={page === id ? "nav-item active" : "nav-item"}
              onClick={() => go(id)}
            >
              <Icon size={18} />
              <span>{label}</span>
              {id === "sessions" && (
                <span className="nav-count">{data.sessions.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <div className="note-symbol">
            <ShieldCheck size={21} />
          </div>
          <h4>Tu código se queda contigo.</h4>
          <p>
            Solo metadatos de consumo.
            <br />
            Sin prompts. Sin nube.
          </p>
          <button onClick={() => setSetup(true)}>
            Ver configuración <ArrowUpRight size={14} />
          </button>
        </div>
        <div className="local-status">
          <span className="status-dot" />
          <div>
            <strong>Local-first</strong>
            <span>SQLite · localhost</span>
          </div>
          <Database size={17} />
        </div>
        <div className="sidebar-footer">
          <div className="user-avatar">TU</div>
          <div>
            <strong>Mi máquina</strong>
            <span>TokenLens v0.1.0</span>
          </div>
          <span className="pilot-tag">PILOTO</span>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <ChevronRight size={14} />
            <span>{title}</span>
          </div>
          <div className="top-actions">
            <span className={"connection " + (!online ? "offline" : "")}>
              <span className="status-dot" />
              {online ? "En vivo" : "Reconectando"}
            </span>
            <div className="divider" />
            <button
              className="icon-button"
              onClick={refresh}
              title="Actualizar"
            >
              <RefreshCw size={16} />
            </button>
            <button className="top-setup" onClick={() => setSetup(true)}>
              <Settings2 size={16} />
              Configuración
            </button>
          </div>
        </header>
        <main>
          <div className="page-heading">
            <div>
              <div className="eyebrow">CLAUDE CODE × OPENSPEC</div>
              <h1>
                {title}
                <span className="heading-dot">.</span>
              </h1>
              <p>Entiende el consumo. Mejora el flujo. Conserva el control.</p>
            </div>
            <div className="heading-actions">
              <button className="button" onClick={() => setSetup(true)}>
                <Plus size={16} />
                Conectar Claude Code
              </button>
              <a className="button dark" href={exportHref}>
                <Download size={16} />
                Exportar CSV
              </a>
            </div>
          </div>
          <div className="source-bar">
            <div className="segmented">
              <button
                className={source === "real" ? "selected" : ""}
                onClick={() => setSource("real")}
              >
                <Radio size={14} />
                Datos reales
              </button>
              <button
                className={source === "demo" ? "selected" : ""}
                onClick={() =>
                  source === "demo" ? setSource("demo") : loadDemo()
                }
              >
                <FlaskConical size={14} />
                Demo
              </button>
            </div>
            <span className="source-info">
              {source === "demo" ? (
                <>
                  <FlaskConical size={14} />
                  Datos sintéticos · no representan uso real
                </>
              ) : (
                <>
                  <ShieldCheck size={14} />
                  Captura local · solo metadatos
                </>
              )}
            </span>
            <span className="sync-time">
              {loading ? "Cargando…" : `Actualizado ${last}`}
            </span>
          </div>
          {error && (
            <div className="alert error">
              <AlertTriangle size={17} />
              {error}
              <button onClick={() => setError("")}>
                <X size={16} />
              </button>
            </div>
          )}
          {source === "real" && repos.length > 1 && !repoFilter && (
            <div className="alert warning">
              <AlertTriangle size={17} />
              <span>
                Estos totales mezclan {repos.length} repositorios/proyectos:
                la telemetría OTel de Claude Code se configura a nivel de
                usuario, no por proyecto, así que cualquier sesión de Claude
                Code en esta máquina puede sumar aquí mientras el piloto esté
                activo — no solo el repositorio que indicaste con{" "}
                <code>pilot.py init --project</code>. Usa el filtro de
                repositorio para aislar el tuyo.
                {repos.some((r) => !r) && (
                  <>
                    {" "}
                    Las sesiones marcadas "sin repositorio identificado" nunca
                    recibieron un hook de este proyecto.
                  </>
                )}
              </span>
            </div>
          )}
          {rows.some(
            (r) =>
              !r.prompt_id ||
              r.identity_quality.includes("partial") ||
              r.cost_usd === null,
          ) && (
            <div className="alert warning">
              <AlertTriangle size={17} />
              <span>
                Captura con datos incompletos:{" "}
                {rows.filter((r) => !r.prompt_id).length} solicitudes sin prompt
                ID,{" "}
                {
                  rows.filter((r) => r.identity_quality.includes("partial"))
                    .length
                }{" "}
                con contadores parciales y{" "}
                {rows.filter((r) => r.cost_usd === null).length} sin costo
                reportado. Los totales solo incluyen lo observado; no garantizan
                cobertura completa.
              </span>
            </div>
          )}
          {source === "demo" && (
            <div className="demo-banner">
              <span>
                <Info size={16} />
                <strong>Estás explorando el piloto.</strong> Estos datos son
                ficticios y están separados de tus capturas.
              </span>
              <button disabled={busy} onClick={loadDemo}>
                Regenerar demo <RefreshCw size={13} />
              </button>
            </div>
          )}
          <div className="filter-bar">
            <div className="search-input">
              <Search size={16} />
              <input
                aria-label="Buscar capturas"
                placeholder="Buscar HU, cambio, sesión o modelo…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              {query && (
                <button onClick={() => setQuery("")}>
                  <X size={14} />
                </button>
              )}
            </div>
            <select
              aria-label="Período"
              value={range}
              onChange={(e) => setRange(e.target.value)}
            >
              <option value="all">Todo el período</option>
              <option value="24h">Últimas 24 horas</option>
              <option value="7d">Últimos 7 días</option>
            </select>
            {repos.length > 1 && (
              <select
                aria-label="Repositorio"
                value={repoFilter}
                onChange={(e) => setRepoFilter(e.target.value)}
              >
                <option value="">Todos los repositorios</option>
                {repos.map((r) => (
                  <option key={r} value={r}>
                    {r || "Sin repositorio identificado"}
                  </option>
                ))}
              </select>
            )}
            {repoFilter && (
              <button
                className="filter-pill"
                onClick={() => setRepoFilter("")}
              >
                Repo: {repoFilter || "sin identificar"}
                <X size={13} />
              </button>
            )}
            {(sessionId || workItem || developer) && (
              <button
                className="filter-pill"
                onClick={() => {
                  setSessionId("");
                  setWorkItem("");
                  setDeveloper("");
                }}
              >
                {sessionId
                  ? "Sesión: " + shorten(sessionId)
                  : workItem
                    ? "HU #" + workItem
                    : "Desarrollador: " + developer}
                <X size={13} />
              </button>
            )}
            <span className="results-label">
              {num(rows.length)} solicitudes
            </span>
          </div>
          {(page === "overview" || page === "phases") && (
            <>
              <div className="stats-grid">
                <div className="stat-card featured">
                  <div className="stat-top">
                    Tokens procesados <Layers size={17} />
                  </div>
                  <div className="stat-number">
                    {compact(all)}
                    <span>tokens</span>
                  </div>
                  <div className="stat-foot">
                    <span className="small-dot" />
                    Entrada + salida + caché
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-top">
                    Costo equivalente <ChartNoAxesCombined size={17} />
                  </div>
                  <div className="stat-number">
                    {money(cost(rows))}
                    <span>USD</span>
                  </div>
                  <div className="stat-foot">
                    Estimado reportado · no es factura
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-top">
                    Lectura de caché <RefreshCw size={17} />
                  </div>
                  <div className="stat-number">
                    {cache.toFixed(1)}
                    <span>% de entrada</span>
                  </div>
                  <div className="stat-foot">
                    {compact(sum(rows, "cache_read_tokens"))} tokens
                    reutilizados
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-top">
                    Peticiones observadas <Command size={17} />
                  </div>
                  <div className="stat-number">
                    {num(prompts.length)}
                    <span>turnos</span>
                  </div>
                  <div className="stat-foot">
                    {new Set(rows.map((r) => r.session_id)).size} sesiones ·{" "}
                    {tasks.filter((t) => t.id).length} HUs
                  </div>
                </div>
                <div className={"stat-card" + (wastedPct > 0 ? " warn" : "")}>
                  <div className="stat-top">
                    Fuga en errores/reintentos <TriangleAlert size={17} />
                  </div>
                  <div className="stat-number">
                    {wastedPct.toFixed(1)}
                    <span>% del consumo</span>
                  </div>
                  <div className="stat-foot">
                    {compact(wastedTokens)} tokens ·{" "}
                    {money(cost(wastedRows))} en turnos con error o
                    interrumpidos
                  </div>
                </div>
              </div>
            </>
          )}
          {page === "overview" && (
            <>
              <div className="overview-grid">
                <section className="panel consumption-panel">
                  <div className="panel-head">
                    <div>
                      <h2>El recorrido de tus tokens</h2>
                      <p>Consumo observado en el período seleccionado</p>
                    </div>
                    <Badge type="green">
                      <span className="tiny-dot" />
                      OTel
                    </Badge>
                  </div>
                  <Trend rows={rows} />
                  <Breakdown rows={rows} />
                </section>
                <section className="panel">
                  <div className="panel-head">
                    <div>
                      <h2>Consumo por fase</h2>
                      <p>¿Dónde se concentra el trabajo?</p>
                    </div>
                    <button
                      className="icon-button"
                      onClick={() => setPage("phases")}
                    >
                      <ArrowUpRight size={17} />
                    </button>
                  </div>
                  <PhaseList />
                  <button
                    className="text-link"
                    onClick={() => setPage("phases")}
                  >
                    Explorar fases OpenSpec <ArrowRight size={14} />
                  </button>
                </section>
              </div>
              <div className="secondary-grid">
                <section className="panel task-panel">
                  <div className="panel-head">
                    <div>
                      <h2>Historias en foco</h2>
                      <p>Una HU, incluso a través de varios chats</p>
                    </div>
                    <button
                      className="text-link"
                      onClick={() => setPage("tasks")}
                    >
                      Ver todas <ArrowRight size={14} />
                    </button>
                  </div>
                  {tasks.length ? (
                    <div className="task-preview">
                      {tasks.slice(0, 3).map((t) => (
                        <button
                          key={t.id}
                          onClick={() => {
                            setPage("tasks");
                            setWorkItem(t.id);
                          }}
                        >
                          <div className="task-icon">
                            <FileText size={18} />
                          </div>
                          <div>
                            <strong>
                              {t.id ? "HU #" + t.id : "Sin HU asignada"}
                            </strong>
                            <span>
                              {t.rows[0]?.change_id ||
                                "Pendiente de atribución"}
                            </span>
                          </div>
                          <div className="task-consumption">
                            <strong>{compact(total(t.rows))}</strong>
                            <span>{money(cost(t.rows))} equiv.</span>
                          </div>
                          <ChevronRight size={15} />
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="small-empty">
                      Asocia una sesión a una HU para empezar.
                    </div>
                  )}
                </section>
                <section className="insight-callout">
                  <div className="insight-label">
                    <Activity size={16} /> SEMANA ACTUAL VS. ANTERIOR
                  </div>
                  {weekCompare ? (
                    <>
                      <h2
                        className={
                          weekCompare.costDelta === null
                            ? ""
                            : weekCompare.costDelta > 5
                              ? "delta-up"
                              : weekCompare.costDelta < -5
                                ? "delta-down"
                                : ""
                        }
                      >
                        {weekCompare.costDelta === null ? (
                          "Primer costo reportado"
                        ) : (
                          <>
                            {weekCompare.costDelta > 5 ? (
                              <TrendingUp size={18} />
                            ) : weekCompare.costDelta < -5 ? (
                              <TrendingDown size={18} />
                            ) : (
                              <Minus size={18} />
                            )}{" "}
                            {weekCompare.costDelta >= 0 ? "+" : ""}
                            {weekCompare.costDelta.toFixed(1)}% en costo
                          </>
                        )}
                      </h2>
                      <p>
                        Esta semana: {compact(weekCompare.curTokens)} tokens ·{" "}
                        {money(weekCompare.curCost)}
                        <br />
                        Semana anterior: {compact(weekCompare.prevTokens)}{" "}
                        tokens · {money(weekCompare.prevCost)}
                      </p>
                    </>
                  ) : (
                    <>
                      <h2>Aún no hay dos semanas de datos</h2>
                      <p>
                        La comparación aparece sola cuando haya al menos dos
                        semanas calendario con capturas reales.
                      </p>
                    </>
                  )}
                  <button onClick={() => setPage("insights")}>
                    Revisar oportunidades <ArrowUpRight size={17} />
                  </button>
                </section>
              </div>
              <section className="panel requests-panel">
                <div className="panel-head">
                  <div>
                    <h2>Últimas solicitudes</h2>
                    <p>
                      Cada llamada al modelo, sin doble conteo entre métricas y
                      eventos
                    </p>
                  </div>
                  <Badge>{rows.length} observadas</Badge>
                </div>
                <Requests list={rows} limit={6} />
              </section>
            </>
          )}
          {page === "sessions" && (
            <>
              <div className="section-header">
                <h2>{session ? "Detalle de sesión" : "Sesiones observadas"}</h2>
                <span>Asigna la HU antes de empezar una nueva petición</span>
              </div>
              {!data.sessions.length ? (
                <Empty title="Esperando la primera sesión" onDemo={loadDemo} />
              ) : (
                <div className="session-grid">
                  {data.sessions
                    .filter((s) => !sessionId || s.id === sessionId)
                    .map((s) => {
                      let rs = data.requests.filter(
                        (r) => r.session_id === s.id,
                      );
                      return (
                        <section className="panel session-card" key={s.id}>
                          <div className="session-card-head">
                            <div className="session-icon">
                              <Terminal size={21} />
                            </div>
                            <Badge
                              type={s.status === "active" ? "green" : "neutral"}
                            >
                              {s.status === "active"
                                ? "Observada"
                                : "Finalizada"}
                            </Badge>
                          </div>
                          <h3>
                            Sesión {sessionOrder[s.id] || "?"}{" "}
                            <span className="muted">
                              · {s.repo || "workspace sin identificar"}
                            </span>
                          </h3>
                          <span className="mono" title={s.id}>
                            {shorten(s.id)}
                          </span>
                          <div className="session-meta">
                            <span>
                              <GitBranch size={14} />
                              {s.change_id || "Cambio sin asignar"}
                            </span>
                            <span>
                              <Clock size={14} />
                              {date(s.last_seen)}
                            </span>
                          </div>
                          <div className="session-card-stats">
                            <div>
                              <strong>{compact(total(rs))}</strong>
                              <span>tokens</span>
                            </div>
                            <div>
                              <strong>{money(cost(rs))}</strong>
                              <span>USD equivalente</span>
                            </div>
                            <div>
                              <strong>{rs.length}</strong>
                              <span>solicitudes</span>
                            </div>
                          </div>
                          <div className="session-card-bottom">
                            <Badge>
                              {s.work_item ? "HU #" + s.work_item : "Sin HU"}
                            </Badge>
                            <span>{PH[s.phase]}</span>
                          </div>
                          <div className="session-buttons">
                            <button
                              className="button"
                              onClick={() =>
                                setBinding({ session: s, scope: "future" })
                              }
                            >
                              <Link size={14} />
                              Asignar HU / fase
                            </button>
                            <button
                              className="icon-button"
                              title="Ver solicitudes"
                              onClick={() => setSessionId(s.id)}
                            >
                              <ArrowUpRight size={18} />
                            </button>
                            <button
                              className="icon-button"
                              title="Conciliar"
                              onClick={() => setReconcile(s)}
                            >
                              <CheckCircle2 size={18} />
                            </button>
                          </div>
                        </section>
                      );
                    })}
                </div>
              )}
              {session && (
                <section className="panel requests-panel">
                  <div className="panel-head">
                    <h2>Solicitudes de {shorten(session.id)}</h2>
                    <button
                      className="text-link"
                      onClick={() => setSessionId("")}
                    >
                      Todas las sesiones
                    </button>
                  </div>
                  <Requests />
                </section>
              )}
            </>
          )}
          {page === "tasks" && (
            <>
              <div className="section-header">
                <h2>Consumo por historia de usuario</h2>
                <span>
                  Agregación de solicitudes únicas · no mide productividad
                </span>
              </div>
              {tasks.length ? (
                <div className="task-grid">
                  {tasks.map((t) => {
                    const bench = taskBenchmark[t.id];
                    return (
                    <section className="panel task-detail" key={t.id}>
                      <div className="panel-head">
                        <div className="task-title">
                          <div className="task-icon">
                            <FileText size={19} />
                          </div>
                          <div>
                            <h2>{t.id ? "HU #" + t.id : "Sin HU"}</h2>
                            <p>
                              {t.rows[0]?.change_id || "Asignación pendiente"}
                            </p>
                          </div>
                        </div>
                        <div className="task-badges">
                          <Badge>
                            {new Set(t.rows.map((r) => r.session_id)).size}{" "}
                            sesiones
                          </Badge>
                          {bench && bench.ratio >= 1.5 && (
                            <Badge type="warning">
                              {bench.ratio.toFixed(1)}x la mediana
                            </Badge>
                          )}
                          {bench && bench.ratio <= 0.7 && (
                            <Badge type="green">Eficiente</Badge>
                          )}
                        </div>
                      </div>
                      <div className="task-big">
                        {compact(total(t.rows))}
                        <span>tokens procesados</span>
                        <b>
                          {money(cost(t.rows))} <small>equiv. USD</small>
                        </b>
                      </div>
                      <div className="task-sub-stats">
                        <span>{cacheRate(t.rows).toFixed(1)}% caché</span>
                        {bench && (
                          <span>
                            {money(bench.avgTurnCost)}/turno · mediana{" "}
                            {money(bench.median)}
                          </span>
                        )}
                      </div>
                      <Breakdown rows={t.rows} />
                      <div className="task-phases">
                        {group(t.rows, "phase").map((p) => (
                          <Badge key={p.id}>
                            {PH[p.id]} · {compact(total(p.rows))}
                          </Badge>
                        ))}
                      </div>
                      <button
                        className="text-link"
                        onClick={() => setWorkItem(t.id)}
                      >
                        Ver solicitudes de la HU <ArrowRight size={14} />
                      </button>
                    </section>
                    );
                  })}
                </div>
              ) : (
                <Empty title="Sin historias observadas" onDemo={loadDemo} />
              )}
              {workItem && (
                <section className="panel requests-panel">
                  <div className="panel-head">
                    <h2>Detalle HU #{workItem}</h2>
                  </div>
                  <Requests />
                </section>
              )}
            </>
          )}
          {page === "team" && (
            <>
              <div className="section-header">
                <h2>Consumo por desarrollador</h2>
                <span>
                  Identidad reportada por el hook local · un mismo equipo
                  puede compartir alias si no configuró uno propio
                </span>
              </div>
              {teams.filter((t) => t.id).length ? (
                <div className="task-grid">
                  {teams
                    .filter((t) => t.id)
                    .map((t) => {
                      const turnCount = groupByPrompt(t.rows).length;
                      return (
                        <section className="panel task-detail" key={t.id}>
                          <div className="panel-head">
                            <div className="task-title">
                              <div className="task-icon">
                                <Users size={19} />
                              </div>
                              <div>
                                <h2>{t.id}</h2>
                                <p>
                                  {new Set(t.rows.map((r) => r.work_item))
                                    .size}{" "}
                                  HU(s) tocadas
                                </p>
                              </div>
                            </div>
                            <Badge>
                              {new Set(t.rows.map((r) => r.session_id)).size}{" "}
                              sesiones
                            </Badge>
                          </div>
                          <div className="task-big">
                            {compact(total(t.rows))}
                            <span>tokens procesados</span>
                            <b>
                              {money(cost(t.rows))} <small>equiv. USD</small>
                            </b>
                          </div>
                          <div className="task-sub-stats">
                            <span>{cacheRate(t.rows).toFixed(1)}% caché</span>
                            <span>{turnCount} turnos</span>
                          </div>
                          <Breakdown rows={t.rows} />
                          <div className="task-phases">
                            {group(t.rows, "phase").map((p) => (
                              <Badge key={p.id}>
                                {PH[p.id]} · {compact(total(p.rows))}
                              </Badge>
                            ))}
                          </div>
                          <button
                            className="text-link"
                            onClick={() => setDeveloper(t.id)}
                          >
                            Ver solicitudes <ArrowRight size={14} />
                          </button>
                        </section>
                      );
                    })}
                </div>
              ) : (
                <Empty
                  title="Sin desarrolladores identificados"
                  text="Cada hook local reporta su propio alias. Aparecerán aquí en cuanto haya capturas."
                  onDemo={loadDemo}
                />
              )}
              {developer && (
                <section className="panel requests-panel">
                  <div className="panel-head">
                    <h2>Solicitudes de {developer}</h2>
                  </div>
                  <Requests />
                </section>
              )}
            </>
          )}
          {page === "phases" && (
            <div className="phase-page">
              <section className="panel">
                <div className="panel-head">
                  <div>
                    <h2>Distribución del flujo</h2>
                    <p>Fases explícitas o inferidas del comando reconocido</p>
                  </div>
                </div>
                <PhaseList />
              </section>
              <div>
                <section className="panel explanation">
                  <div className="info-icon">
                    <Layers size={22} />
                  </div>
                  <h2>Planning es una fase compartida.</h2>
                  <p>
                    <code>/opsx:propose</code> puede generar proposal, specs,
                    design y tasks en una sola ejecución. No repartimos sus
                    tokens arbitrariamente.
                  </p>
                  <p>
                    Para separar esas etapas, fija una fase antes de cada
                    petición. Una solicitud que cubre varios artefactos debe
                    permanecer en <strong>planning</strong>.
                  </p>
                  <button className="button" onClick={() => go("sessions")}>
                    Asignar una fase <ArrowRight size={15} />
                  </button>
                </section>
                <div className="fine-note">
                  <ShieldCheck size={16} />
                  <p>
                    Los eventos tardíos conservan la fase de su petición.
                    Cambiar la fase de una sesión no reetiqueta el pasado salvo
                    que lo solicites.
                  </p>
                </div>
              </div>
            </div>
          )}
          {page === "insights" && (
            <>
              <div className="principle-banner">
                <Activity size={24} />
                <div>
                  <h2>Señales, no veredictos.</h2>
                  <p>
                    Estas heurísticas ayudan a investigar. No demuestran
                    desperdicio, causalidad ni necesidad del consumo.
                  </p>
                </div>
              </div>
              <div className="insights-grid">
                <section className="panel insight-card">
                  <Badge type={wastedPct > 5 ? "warning" : "neutral"}>
                    FUGA
                  </Badge>
                  <h2>
                    {wastedPct.toFixed(1)}% del consumo en errores o
                    interrupciones
                  </h2>
                  <p>
                    {compact(wastedTokens)} tokens ·{" "}
                    {money(cost(wastedRows))} en turnos que fallaron o se
                    interrumpieron sin completarse. Costo real observado, no
                    estimado.
                  </p>
                  {wastedRows.length > 0 && (
                    <div className="tool-list">
                      {groupByPrompt(wastedRows)
                        .sort((a, b) => (cost(b.rows) ?? 0) - (cost(a.rows) ?? 0))
                        .slice(0, 3)
                        .map((g) => (
                          <div
                            key={g.key}
                            style={{ cursor: "pointer" }}
                            onClick={() =>
                              setDetail({ ...g.rows[0], _promptRows: g.rows })
                            }
                          >
                            <span>
                              {promptLabel(promptMeta[g.key], 0)} ·{" "}
                              {PH[g.rows[0].phase]}
                            </span>
                            <strong>{money(cost(g.rows))}</strong>
                          </div>
                        ))}
                    </div>
                  )}
                </section>
                <section className="panel insight-card">
                  <Badge type="green">CACHÉ</Badge>
                  <h2>{cache.toFixed(1)}% de entrada reutilizada</h2>
                  <p>
                    Ratio de lectura sobre entrada total: no cacheada + lectura
                    + escritura. Una caché baja puede ser normal en el primer
                    turno.
                  </p>
                  <Breakdown rows={rows} />
                </section>
                <section className="panel insight-card">
                  <Badge type="warning">ATRIBUCIÓN</Badge>
                  <h2>
                    {rows.filter((r) => !r.work_item).length} solicitudes sin HU
                  </h2>
                  <p>
                    Sin atribución no podemos evaluar cuánto consumió la tarea.
                    Asigna la HU y corrige explícitamente el histórico si
                    corresponde.
                  </p>
                  <button className="text-link" onClick={() => go("sessions")}>
                    Revisar sesiones <ArrowRight size={15} />
                  </button>
                </section>
                <section className="panel insight-card">
                  <Badge>HERRAMIENTAS</Badge>
                  <h2>
                    {visibleTools.filter((t) => t.output_bytes > 50000).length}{" "}
                    salidas mayores a 50 KB
                  </h2>
                  <p>
                    Umbral exploratorio del piloto, no una regla del proveedor.
                    El tamaño en bytes no equivale a tokens ni a costo exacto.
                  </p>
                  <div className="tool-list">
                    {[...visibleTools]
                      .sort((a, b) => b.output_bytes - a.output_bytes)
                      .slice(0, 3)
                      .map((t) => (
                        <div key={t.id}>
                          <span>{t.tool_name}</span>
                          <strong>{compact(t.output_bytes)} B</strong>
                        </div>
                      ))}
                  </div>
                </section>
                <section className="panel insight-card">
                  <Badge>CALIDAD DE DATOS</Badge>
                  <h2>
                    {rows.filter((r) => r.identity_quality !== "server").length}{" "}
                    identidades débiles o parciales
                  </h2>
                  <p>
                    Solicitudes sin ID del servidor o sin alguna categoría de
                    tokens. No se puede garantizar cobertura completa ni
                    deduplicación perfecta.
                  </p>
                  <button
                    className="text-link"
                    onClick={() => go("diagnostics")}
                  >
                    Ver diagnósticos <ArrowRight size={15} />
                  </button>
                </section>
              </div>
              <section className="panel requests-panel">
                <div className="panel-head">
                  <div>
                    <h2>Turnos con consumo inusual</h2>
                    <p>
                      Costo frente a la mediana de turnos de la misma fase
                      (mínimo 4 turnos comparables, umbral 2x)
                    </p>
                  </div>
                  <Badge>{outlierPrompts.length} detectados</Badge>
                </div>
                {outlierPrompts.length ? (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Turno</th>
                          <th>HU / fase</th>
                          <th>Costo</th>
                          <th>Vs. mediana de fase</th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        {outlierPrompts.slice(0, 10).map((p) => (
                          <tr
                            key={p.key}
                            onClick={() =>
                              setDetail({ ...p.rows[0], _promptRows: p.rows })
                            }
                          >
                            <td>
                              <div className="table-primary">
                                {promptLabel(promptMeta[p.key], 0)}
                              </div>
                              <div className="table-secondary">
                                {date(p.rows[0].occurred_at)}
                              </div>
                            </td>
                            <td>
                              {p.rows[0].work_item
                                ? "#" + p.rows[0].work_item
                                : "Sin HU"}{" "}
                              · {PH[p.rows[0].phase]}
                            </td>
                            <td className="numeric">{money(cost(p.rows))}</td>
                            <td>
                              <Badge type="warning">
                                {p.ratio.toFixed(1)}x (mediana{" "}
                                {money(p.medianCost)})
                              </Badge>
                            </td>
                            <td>
                              <ArrowUpRight size={16} />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="muted">
                    Sin desviaciones relevantes todavía, o sin suficientes
                    turnos comparables por fase.
                  </p>
                )}
              </section>
              <section className="panel requests-panel">
                <div className="panel-head">
                  <div>
                    <h2>Peticiones con mayor consumo</h2>
                    <p>
                      El total incluye todas las solicitudes observadas del
                      mismo prompt
                    </p>
                  </div>
                  <select
                    aria-label="Ordenar peticiones"
                    value={rankBy}
                    onChange={(e) => setRankBy(e.target.value)}
                  >
                    <option value="tokens">Por tokens</option>
                    <option value="cost">Por equiv. USD</option>
                  </select>
                </div>
                {prompts.length ? (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Petición</th>
                          <th>HU / fase</th>
                          <th>Llamadas</th>
                          <th>Tokens</th>
                          <th>Equiv. USD</th>
                          <th />
                        </tr>
                      </thead>
                      <tbody>
                        {[...prompts]
                          .sort((a, b) =>
                            rankBy === "cost"
                              ? (cost(b.rows) ?? -1) - (cost(a.rows) ?? -1)
                              : total(b.rows) - total(a.rows),
                          )
                          .slice(0, 10)
                          .map((p, i) => {
                            const meta = promptMeta[p.key];
                            const sources = sourceBreakdown(p.rows);
                            const extra = Object.keys(sources).filter(
                              (s) => s !== "main" && s !== "unknown",
                            );
                            return (
                              <tr
                                key={p.key}
                                onClick={() =>
                                  setDetail({
                                    ...p.rows[0],
                                    _promptRows: p.rows,
                                  })
                                }
                              >
                                <td>
                                  <div className="table-primary">
                                    {promptLabel(meta, prompts.length - i)}
                                  </div>
                                  <div className="table-secondary">
                                    {date(p.rows[0].occurred_at)}{" "}
                                    <span className="dotsep">·</span>{" "}
                                    {shorten(p.id)}
                                  </div>
                                </td>
                                <td>
                                  {p.rows[0].work_item
                                    ? "#" + p.rows[0].work_item
                                    : "Sin HU"}{" "}
                                  · {PH[p.rows[0].phase]}
                                </td>
                                <td>
                                  {p.rows.length}
                                  {extra.length > 0 && (
                                    <div className="table-secondary">
                                      {extra
                                        .map(
                                          (s) =>
                                            `${sources[s]} de ${SOURCE_LABEL[s] || s}`,
                                        )
                                        .join(" · ")}
                                    </div>
                                  )}
                                </td>
                                <td className="numeric">
                                  {num(total(p.rows))}
                                </td>
                                <td>{money(cost(p.rows))}</td>
                                <td>
                                  <ArrowUpRight size={16} />
                                </td>
                              </tr>
                            );
                          })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <Empty />
                )}
              </section>
            </>
          )}
          {page === "diagnostics" && (
            <>
              <div className="diagnostic-grid">
                <section className="panel">
                  <div className="panel-head">
                    <h2>Estado de captura</h2>
                    <Badge type={online ? "green" : "warning"}>
                      {online ? "UI conectada" : "UI desconectada"}
                    </Badge>
                  </div>
                  <dl className="diagnostic-list">
                    <div>
                      <dt>Fuente seleccionada</dt>
                      <dd>
                        {source === "demo"
                          ? "Sintética / demo"
                          : "Real / local"}
                      </dd>
                    </div>
                    <div>
                      <dt>Último lote recibido</dt>
                      <dd>{date(latest?.received_at)}</dd>
                    </div>
                    <div>
                      <dt>Eventos aceptados (últimos 100 lotes)</dt>
                      <dd>{num(sum(data.receipts, "accepted"))}</dd>
                    </div>
                    <div>
                      <dt>Duplicados descartados</dt>
                      <dd>{num(sum(data.receipts, "duplicates"))}</dd>
                    </div>
                    <div>
                      <dt>Registros rechazados</dt>
                      <dd>{num(sum(data.receipts, "invalid"))}</dd>
                    </div>
                    <div>
                      <dt>Eventos ignorados por contrato</dt>
                      <dd>{num(sum(data.receipts, "ignored"))}</dd>
                    </div>
                    <div>
                      <dt>Normalizador</dt>
                      <dd>v{data.normalizer_version || 1}</dd>
                    </div>
                    <div>
                      <dt>Solicitudes sin costo reportado</dt>
                      <dd>
                        {
                          data.requests.filter((r) => r.cost_usd === null)
                            .length
                        }
                      </dd>
                    </div>
                  </dl>
                  <div className="fine-note">
                    <Info size={16} />
                    <p>
                      La conexión SSE solo confirma que el panel está conectado.
                      No prueba que Claude esté exportando ni que todos sus
                      eventos hayan llegado.
                    </p>
                  </div>
                </section>
                <section className="panel explanation">
                  <div className="info-icon">
                    <CheckCircle2 size={22} />
                  </div>
                  <h2>Conciliar antes de concluir.</h2>
                  <p>
                    Compara las cuatro categorías de tokens con el resumen de la
                    misma sesión. Las métricas se guardan como snapshots para
                    inspección, no se suman al ledger de eventos.
                  </p>
                  <div className="metric-summary">
                    <strong>{data.metrics.length}</strong>
                    <span>
                      snapshots de métricas disponibles
                      <br />
                      últimos 500 en el panel
                    </span>
                  </div>
                  <button
                    className="button"
                    onClick={() =>
                      data.sessions.length
                        ? setReconcile(data.sessions[0])
                        : setNotice("Captura una sesión antes de conciliar.")
                    }
                  >
                    <CheckCircle2 size={16} />
                    Nueva conciliación
                  </button>
                </section>
              </div>
              <section className="panel requests-panel">
                <div className="panel-head">
                  <h2>Últimas conciliaciones</h2>
                </div>
                {data.reconciliations.length ? (
                  <div className="reconciliation-list">
                    {data.reconciliations.map((r) => {
                      let o = JSON.parse(r.observed),
                        e = JSON.parse(r.expected);
                      return (
                        <div key={r.id}>
                          <span className="mono">{shorten(r.session_id)}</span>
                          <span>{date(r.created_at)}</span>
                          <Badge
                            type={
                              KEYS.every((k) => o[k] === e[k])
                                ? "green"
                                : "warning"
                            }
                          >
                            {KEYS.every((k) => o[k] === e[k])
                              ? "Coincide"
                              : "Hay diferencias"}
                          </Badge>
                          <span>
                            {KEYS.map(
                              (k) => `${LABEL[k]}: Δ ${num(o[k] - e[k])}`,
                            ).join(" · ")}
                          </span>
                          <small>{r.note || "Sin nota"}</small>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="small-empty">
                    Aún no hay conciliaciones. No asumimos una tolerancia ni
                    cobertura completa.
                  </div>
                )}
              </section>
              <section className="panel requests-panel">
                <div className="panel-head">
                  <h2>Auditoría de atribución</h2>
                  <Badge>Últimos 50 cambios</Badge>
                </div>
                {data.audit.length ? (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Fecha</th>
                          <th>Sesión</th>
                          <th>HU</th>
                          <th>Fase</th>
                          <th>Alcance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.audit.map((a) => {
                          const d = JSON.parse(a.detail);
                          return (
                            <tr key={a.id}>
                              <td>{date(a.created_at)}</td>
                              <td className="mono">{shorten(a.target)}</td>
                              <td>{d.work_item || "—"}</td>
                              <td>{PH[d.phase]}</td>
                              <td>{d.scope}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="small-empty">
                    Los cambios manuales de HU y fase aparecerán aquí.
                  </div>
                )}
              </section>
              <section className="panel requests-panel">
                <div className="panel-head">
                  <div>
                    <h2>Snapshots OTel (no se suman al consumo)</h2>
                    <p>
                      Señal de métricas, no de eventos: no trae prompt ni HU,
                      solo sirve para contrastar contadores por sesión
                    </p>
                  </div>
                  <Badge>Inspección</Badge>
                </div>
                {data.metrics.length ? (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Sesión</th>
                          <th>Modelo</th>
                          <th>Tipo</th>
                          <th>Valor</th>
                          <th>Temporalidad</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.metrics.slice(0, 15).map((m) => (
                          <tr key={m.id}>
                            <td>
                              {sessionOrder[m.session_id]
                                ? "Sesión " + sessionOrder[m.session_id]
                                : "Sesión desconocida"}
                              <div
                                className="table-secondary mono"
                                title={m.session_id}
                              >
                                {shorten(m.session_id)}
                              </div>
                            </td>
                            <td>{m.model}</td>
                            <td>{m.type}</td>
                            <td>{num(m.value)}</td>
                            <td>
                              {m.temporality === 2
                                ? "Acumulativa"
                                : m.temporality === 1
                                  ? "Delta"
                                  : "Desconocida"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="small-empty">
                    Sin snapshots. Verifica OTEL_METRICS_EXPORTER; la demo no
                    simula métricas.
                  </div>
                )}
              </section>
            </>
          )}
          <footer className="main-footer">
            <span>
              <ShieldCheck size={13} />
              Los tokens son consumo observado, no contexto único ni
              facturación.
            </span>
            <span>Hecho para entender, no para vigilar.</span>
          </footer>
        </main>
      </div>
      {notice && (
        <div className="toast">
          <CheckCircle2 size={18} />
          {notice}
        </div>
      )}
      {setup && (
        <Modal
          title="Conecta tu máquina"
          subtitle="Sin servidor externo. Sin claves de la API de Claude."
          onClose={() => setSetup(false)}
        >
          <div className="setup-step">
            <span>01</span>
            <div>
              <h3>Prepara el piloto</h3>
              <p>
                Descomprime el proyecto y abre una terminal dentro de tokenlens.
              </p>
              <CodeBlock text={"python pilot.py setup\npython pilot.py run"} />
              <p>
                Abre <code>http://127.0.0.1:4318</code>. El frontend compilado
                ya está incluido.
              </p>
            </div>
          </div>
          <div className="setup-step">
            <span>02</span>
            <div>
              <h3>Configura Claude Code</h3>
              <CodeBlock
                text={'python pilot.py init --project "/ruta/a/tu/repositorio"'}
              />
              <p>
                Respalda settings; activa OTLP HTTP/protobuf y hooks. Reinicia
                completamente VS Code. Si hay telemetría existente, el
                instalador pide consentimiento antes de reemplazarla.
              </p>
            </div>
          </div>
          <div className="setup-step">
            <span>03</span>
            <div>
              <h3>Captura y asigna tu HU</h3>
              <p>
                Envía un prompt corto desde la extensión. En{" "}
                <strong>Sesiones</strong>, asigna HU, cambio y fase. Las
                siguientes peticiones conservan esos metadatos. Para corregir la
                primera, elige un alcance histórico explícito.
              </p>
            </div>
          </div>
          <div className="setup-step">
            <span>04</span>
            <div>
              <h3>Valida el total y restaura al terminar</h3>
              <CodeBlock
                text={"python pilot.py test\npython pilot.py restore"}
              />
            </div>
          </div>
          <div className="alert warning">
            <AlertTriangle size={18} />
            <span>
              La telemetría de usuario también afecta otras sesiones mientras
              esté activa. Los hooks están limitados al repositorio. Las
              políticas administradas pueden impedir o cambiar la configuración.
            </span>
          </div>
          <button className="button" onClick={loadDemo} disabled={busy}>
            <FlaskConical size={16} />
            Probar sin conectar Claude
          </button>
        </Modal>
      )}
      {binding && (
        <BindingModal
          binding={binding}
          source={source}
          onClose={() => setBinding(null)}
          onSave={async (body) => {
            await api(
              `/api/sessions/${encodeURIComponent(binding.session.id)}/binding?source=${source}`,
              post(body, "PUT"),
            );
            setBinding(null);
            await refresh();
            setNotice("Atribución guardada y auditada.");
          }}
        />
      )}
      {reconcile && (
        <ReconcileModal
          session={reconcile}
          source={source}
          onClose={() => setReconcile(null)}
          onSave={async (body) => {
            const r = await api(`/api/reconcile?source=${source}`, post(body));
            await refresh();
            return r;
          }}
        />
      )}
      {detail && (
        <Modal
          title={
            detail._promptRows ? "Detalle de petición" : "Detalle de solicitud"
          }
          subtitle={
            detail._promptRows
              ? (() => {
                  const meta =
                    promptMeta[detail.session_id + "::" + detail.prompt_id];
                  const label = meta?.command
                    ? COMMAND_LABEL[meta.command] || meta.command
                    : "";
                  return label
                    ? `${label} · ${shorten(detail.prompt_id)}`
                    : shorten(detail.prompt_id);
                })()
              : shorten(detail.request_id)
          }
          onClose={() => setDetail(null)}
        >
          <div className="detail-total">
            <span>Consumo observado</span>
            <strong>
              {num(
                detail._promptRows ? total(detail._promptRows) : token(detail),
              )}
              <small> tokens</small>
            </strong>
            <Badge
              type={detail.identity_quality === "server" ? "green" : "warning"}
            >
              {detail.identity_quality === "server"
                ? "ID de servidor"
                : "Identidad " + detail.identity_quality}
            </Badge>
          </div>
          <Breakdown rows={detail._promptRows || [detail]} large />
          <dl className="diagnostic-list">
            <div>
              <dt>HU</dt>
              <dd>{detail.work_item || "Sin asignar"}</dd>
            </div>
            <div>
              <dt>Cambio OpenSpec</dt>
              <dd>{detail.change_id || "Sin asignar"}</dd>
            </div>
            <div>
              <dt>Fase</dt>
              <dd>{PH[detail.phase]}</dd>
            </div>
            <div>
              <dt>Atribución</dt>
              <dd>{detail.attribution}</dd>
            </div>
            <div>
              <dt>Modelo</dt>
              <dd>{detail.model}</dd>
            </div>
            <div>
              <dt>Costo equivalente reportado</dt>
              <dd>
                {money(
                  detail._promptRows
                    ? cost(detail._promptRows)
                    : detail.cost_usd,
                )}
              </dd>
            </div>
            <div>
              <dt>Origen de solicitud</dt>
              <dd>{detail.query_source}</dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd>{detail.status}</dd>
            </div>
            <div>
              <dt>Petición</dt>
              <dd className="mono">{detail.prompt_id || "No disponible"}</dd>
            </div>
            <div>
              <dt>Sesión</dt>
              <dd className="mono">{detail.session_id}</dd>
            </div>
          </dl>
          {detail._promptRows && detail._promptRows.length > 1 && (
            <>
              <h3 className="detail-tools-title">
                Llamadas individuales de este turno (
                {detail._promptRows.length})
              </h3>
              <div className="tool-list">
                {detail._promptRows.map((r) => (
                  <div key={r.id}>
                    <span>
                      {r.model.replace("claude-", "")}{" "}
                      {SOURCE_LABEL[r.query_source]
                        ? `· ${SOURCE_LABEL[r.query_source]}`
                        : ""}{" "}
                      · {date(r.occurred_at)}
                    </span>
                    <strong>
                      {num(token(r))} tokens ·{" "}
                      {(r.duration_ms / 1000).toFixed(1)} s
                    </strong>
                  </div>
                ))}
              </div>
            </>
          )}
          <h3 className="detail-tools-title">Herramientas de la petición</h3>
          <div className="tool-list">
            {data.tools
              .filter(
                (t) =>
                  t.session_id === detail.session_id &&
                  t.prompt_id === detail.prompt_id,
              )
              .slice(0, 12)
              .map((t) => (
                <div key={t.id}>
                  <span>
                    {t.tool_name} · {t.success ? "OK" : "Error"}
                  </span>
                  <strong>
                    {compact(t.output_bytes)} B ·{" "}
                    {(t.duration_ms / 1000).toFixed(1)} s
                  </strong>
                </div>
              ))}
          </div>
          <p className="muted">
            Últimas herramientas disponibles (máximo 12). Correlación por
            prompt, no costo exacto por herramienta.
          </p>
          <div className="fine-note">
            <Info size={16} />
            <p>
              Tokens reportados por llamadas observadas. Sin desglose causal por
              herramienta ni lectura de conversación.{" "}
              {source === "demo" ? "Esta captura es sintética." : ""}
            </p>
          </div>
          <button
            className="button"
            onClick={() => {
              setBinding({
                session: data.sessions.find((s) => s.id === detail.session_id),
                scope: detail.prompt_id ? "prompt" : "session",
                prompt: detail.prompt_id,
              });
              setDetail(null);
            }}
          >
            <Link size={15} />
            Corregir atribución
          </button>
        </Modal>
      )}
    </div>
  );
}
function Modal({ title, subtitle, onClose, children }) {
  useEffect(() => {
    const handler = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = prev;
    };
  }, []);
  return (
    <div className="modal-overlay" onClick={onClose}>
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-head">
          <div>
            <h2>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <button aria-label="Cerrar" className="icon-button" onClick={onClose}>
            <X size={21} />
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </section>
    </div>
  );
}
function CodeBlock({ text }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="code-block">
      <pre>{text}</pre>
      <button
        title="Copiar"
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          } catch {}
        }}
      >
        {copied ? <Check size={15} /> : <Copy size={15} />}
      </button>
    </div>
  );
}
function BindingModal({ binding, source, onClose, onSave }) {
  const s = binding.session;
  const [form, setForm] = useState({
    work_item: s.work_item || "",
    change_id: s.change_id || "",
    phase: s.phase || "unassigned",
    developer: s.developer || "local-user",
    scope: binding.scope,
    prompt_id: binding.prompt || "",
  });
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <Modal title="Asignar HU y fase" subtitle={shorten(s.id)} onClose={onClose}>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          try {
            await onSave(form);
          } catch (e) {
            setError(e.message);
            setBusy(false);
          }
        }}
      >
        <div className="form-grid">
          <label>
            Historia de usuario
            <input
              autoFocus
              placeholder="Ej. 1842"
              value={form.work_item}
              onChange={(e) => setForm({ ...form, work_item: e.target.value })}
            />
          </label>
          <label>
            Identidad local
            <input
              value={form.developer}
              onChange={(e) => setForm({ ...form, developer: e.target.value })}
            />
          </label>
          <label className="span-two">
            Cambio OpenSpec
            <input
              placeholder="Ej. mejorar-timeouts"
              value={form.change_id}
              onChange={(e) => setForm({ ...form, change_id: e.target.value })}
            />
          </label>
          <label className="span-two">
            Fase
            <select
              value={form.phase}
              onChange={(e) => setForm({ ...form, phase: e.target.value })}
            >
              {Object.entries(PH).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </label>
          <label className="span-two">
            Alcance
            <select
              value={form.scope}
              onChange={(e) => setForm({ ...form, scope: e.target.value })}
            >
              <option value="future">
                Solo próximas peticiones (recomendado)
              </option>
              {binding.prompt && (
                <option value="prompt">
                  Esta petición + próximas peticiones
                </option>
              )}
              <option value="session">
                Toda esta sesión + próximas peticiones
              </option>
            </select>
          </label>
        </div>
        <div className="fine-note">
          <Info size={16} />
          <p>
            {form.scope === "future"
              ? "No cambia solicitudes ni peticiones ya iniciadas."
              : "Esta acción reetiqueta el histórico seleccionado y también actualiza el contexto para próximas peticiones. Queda auditada."}
          </p>
        </div>
        {error && <div className="alert error">{error}</div>}
        <div className="modal-actions">
          <button className="button" type="button" onClick={onClose}>
            Cancelar
          </button>
          <button className="button dark" disabled={busy}>
            {busy ? "Guardando…" : "Guardar atribución"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
function ReconcileModal({ session, source, onClose, onSave }) {
  const [form, setForm] = useState({
      ...Object.fromEntries(KEYS.map((k) => [k, ""])),
      note: "",
    }),
    [result, setResult] = useState(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <Modal
      title="Conciliar una sesión"
      subtitle={shorten(session.id)}
      onClose={onClose}
    >
      <p className="modal-intro">
        Copia los contadores del resumen de la misma sesión. Usa cantidades
        completas, no cifras redondeadas en k/M. Verifica que el alcance incluya
        los mismos modelos y subagentes.
      </p>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          try {
            setResult(
              await onSave({
                session_id: session.id,
                ...Object.fromEntries(KEYS.map((k) => [k, Number(form[k])])),
                note: form.note,
              }),
            );
            setError("");
          } catch (e) {
            setError(e.message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <div className="form-grid">
          {KEYS.map((k) => (
            <label key={k}>
              {LABEL[k]}
              <input
                required
                type="number"
                min="0"
                step="1"
                value={form[k]}
                onChange={(e) => setForm({ ...form, [k]: e.target.value })}
              />
            </label>
          ))}
          <label className="span-two">
            Nota de alcance
            <input
              maxLength={500}
              value={form.note}
              placeholder="Modelos, período y comandos incluidos"
              onChange={(e) => setForm({ ...form, note: e.target.value })}
            />
          </label>
        </div>
        {error && <div className="alert error">{error}</div>}
        {result && (
          <div className="reconcile-result">
            <h3>Diferencias: observado − referencia</h3>
            {KEYS.map((k) => (
              <div key={k}>
                <span>{LABEL[k]}</span>
                <strong>{num(result.delta[k])}</strong>
              </div>
            ))}
            <p>{result.warning}</p>
          </div>
        )}
        <div className="modal-actions">
          <button className="button dark" disabled={busy}>
            {busy ? "Conciliando…" : "Comparar y guardar"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

createRoot(document.getElementById("root")).render(<App />);
