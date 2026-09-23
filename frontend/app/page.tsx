"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

const API = "/api/backend";

type Lead = {
  id: number; full_name: string; job_title?: string | null; company?: string | null;
  location?: string | null; linkedin_url?: string | null; post_url?: string | null;
  post_date?: string | null; signal_type: string; intent: string; evidence?: string | null;
  source: string; score: number;
};
type Activity = {
  activity_id: string; author_name: string; author_url?: string | null;
  author_title?: string | null; company?: string | null; post_url: string;
  published_at: string; text: string; source: string; source_provider: string;
  signal_type: string; intent: string; evidence?: string | null;
};
type Range = { start: string; end: string };

const countries = [
  ["", "Any country"],
  ["in", "India"],
  ["us", "United States"],
  ["gb", "United Kingdom"],
  ["ca", "Canada"],
  ["au", "Australia"],
  ["de", "Germany"],
  ["fr", "France"],
  ["nl", "Netherlands"],
  ["sg", "Singapore"],
  ["ae", "United Arab Emirates"],
];

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) throw new Error(data?.detail || "Request failed");
  return data;
}
const intentClass = (intent: string) => intent.toLowerCase();

export default function Home() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [range, setRange] = useState<Range | null>(null);
  const [query, setQuery] = useState("");
  const [days, setDays] = useState("30");
  const [country, setCountry] = useState("");
  const [location, setLocation] = useState("");
  const [signalFilter, setSignalFilter] = useState("");
  const [intentFilter, setIntentFilter] = useState("");
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");

  const loadLeads = async () => {
    try {
      setLoading(true); setError("");
      const params = new URLSearchParams();
      if (signalFilter) params.set("signal_type", signalFilter);
      if (intentFilter) params.set("intent", intentFilter);
      const data = await getJson<Lead[]>(API + "/leads?" + params.toString());
      setLeads(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load leads");
    } finally { setLoading(false); }
  };

  useEffect(() => {
    getJson<Range>(API + "/leads/date-range?kind=previous_month").then(setRange).catch(() => {});
    loadLeads();
  }, [signalFilter, intentFilter]);

  const stats = useMemo(() => ({
    total: leads.length,
    high: leads.filter((lead) => lead.intent === "HIGH").length,
    medium: leads.filter((lead) => lead.intent === "MEDIUM").length,
    signals: new Set(leads.map((lead) => lead.signal_type)).size,
  }), [leads]);

  async function searchActivity(event: FormEvent) {
    event.preventDefault();
    if (!query.trim()) return;
    try {
      setSearching(true); setError("");
      const params = new URLSearchParams({ q: query.trim(), days, limit: "25" });
      if (country) params.set("country", country);
      if (location.trim()) params.set("location", location.trim());
      const data = await getJson<{ items: Activity[] }>(API + "/activity/linkedin/search?" + params.toString());
      setActivities(data.items || []);
      if ((data.items || []).length === 0) {
        setError("No matching real activity was found for these search filters.");
      }
    } catch (err) {
      setActivities([]);
      setError(err instanceof Error ? err.message : "Activity search failed");
    } finally { setSearching(false); }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">AI</div>
          <div><strong>LeadIntel</strong><span>Lead Discovery</span></div>
        </div>
        <nav>
          <a className="nav-item active" href="#dashboard">⌂ <span>Dashboard</span></a>
          <a className="nav-item" href="#activity">◉ <span>LinkedIn Activity</span></a>
          <a className="nav-item" href="#leads">♢ <span>Leads</span></a>
        </nav>
        <div className="sidebar-note">
          <span className="status-dot" />
          <div><strong>Live data mode</strong><p>No mock leads are shown.</p></div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">INTENT INTELLIGENCE</p>
            <h1>Lead Discovery Dashboard</h1>
            <p className="subtitle">Find buying signals from recent LinkedIn activity.</p>
          </div>
          <button className="refresh-btn" onClick={loadLeads}>↻ Refresh</button>
        </header>

        <section id="dashboard" className="stats-grid">
          <div className="stat-card"><span>Total leads</span><strong>{stats.total}</strong><small>Current database</small></div>
          <div className="stat-card"><span>High intent</span><strong>{stats.high}</strong><small>Requires attention</small></div>
          <div className="stat-card"><span>Medium intent</span><strong>{stats.medium}</strong><small>Potential opportunities</small></div>
          <div className="stat-card"><span>Signal types</span><strong>{stats.signals}</strong><small>Detected categories</small></div>
        </section>

        <section id="activity" className="panel search-panel">
          <div className="panel-heading">
            <div><p className="eyebrow">DISCOVER</p><h2>Search LinkedIn activity</h2><p>Search recent activity through the configured data provider.</p></div>
            <span className="provider-badge">REAL DATA ONLY</span>
          </div>
          <form className="search-form" onSubmit={searchActivity}>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="e.g. AI hiring, cloud migration, funding" />
            <select value={country} onChange={(event) => setCountry(event.target.value)} aria-label="Search country">
              {countries.map(([code, name]) => <option key={code} value={code}>{name}</option>)}
            </select>
            <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="City / state / region (optional)" aria-label="Location" />
            <select value={days} onChange={(event) => setDays(event.target.value)}>
              <option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="90">Last 90 days</option>
            </select>
            <button type="submit" disabled={searching || !query.trim()}>{searching ? "Searching..." : "Search activity"}</button>
          </form>
          <p className="search-help">Country controls Google search localization; city/state further focuses the search. It does not guarantee the author's physical location.</p>
          {error && <div className="error-box">{error}</div>}
          {activities.length > 0 && (
            <div className="activity-results">
              <div className="results-title">{activities.length} activity result{activities.length === 1 ? "" : "s"}</div>
              {activities.map((activity) => (
                <article className="activity-row" key={activity.activity_id}>
                  <div className="activity-main">
                    <div className="activity-top"><strong>{activity.author_name}</strong><span className={"intent " + intentClass(activity.intent)}>{activity.intent}</span></div>
                    <p>{activity.author_title || "Role not provided"}{activity.company ? " · " + activity.company : ""}</p>
                    <p className="activity-text">{activity.text}</p>
                    <div className="activity-meta">
                      <span>{activity.signal_type}</span><span>{new Date(activity.published_at).toLocaleDateString()}</span><span>Source: {activity.source_provider}</span>
                    </div>
                  </div>
                  <a className="open-link" href={activity.post_url} target="_blank" rel="noreferrer">Open post ↗</a>
                </article>
              ))}
            </div>
          )}
        </section>

        <section id="leads" className="panel">
          <div className="panel-heading compact">
            <div><p className="eyebrow">LEAD DATABASE</p><h2>Discovered leads</h2>{range && <p>Previous month: {range.start} → {range.end}</p>}</div>
            <div className="filters">
              <select value={intentFilter} onChange={(event) => setIntentFilter(event.target.value)}>
                <option value="">All intent</option><option value="HIGH">High</option><option value="MEDIUM">Medium</option><option value="LOW">Low</option><option value="NONE">None</option>
              </select>
              <select value={signalFilter} onChange={(event) => setSignalFilter(event.target.value)}>
                <option value="">All signals</option><option value="HIRING">Hiring</option><option value="FUNDING">Funding</option><option value="AI_INITIATIVE">AI initiative</option><option value="CLOUD_MIGRATION">Cloud migration</option><option value="PRODUCT_LAUNCH">Product launch</option><option value="PAIN_POINT">Pain point</option><option value="VENDOR_SEARCH">Vendor search</option>
              </select>
            </div>
          </div>

          {loading ? <div className="empty-state"><div className="spinner" />Loading leads...</div> :
           leads.length === 0 ? <div className="empty-state"><div className="empty-icon">⌁</div><h3>No leads yet</h3><p>Search recent LinkedIn activity above. Leads will appear here only when real data is available and stored.</p></div> :
           <div className="lead-table-wrap"><table><thead><tr><th>Lead</th><th>Company</th><th>Signal</th><th>Intent</th><th>Score</th><th>Activity</th></tr></thead>
             <tbody>{leads.map((lead) => <tr key={lead.id}>
               <td><strong>{lead.full_name}</strong><small>{lead.job_title || "Role not provided"}</small></td><td>{lead.company || "—"}</td>
               <td><span className="signal">{lead.signal_type}</span></td><td><span className={"intent " + intentClass(lead.intent)}>{lead.intent}</span></td>
               <td><strong>{lead.score}</strong></td><td>{lead.post_url ? <a className="open-link" href={lead.post_url} target="_blank" rel="noreferrer">Open ↗</a> : "—"}</td>
             </tr>)}</tbody></table></div>}
        </section>
      </main>
    </div>
  );
}
