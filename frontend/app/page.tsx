"use client";
import {useEffect,useState} from "react";
export default function Home(){
 const [leads,setLeads]=useState<any[]>([]); const [range,setRange]=useState<any>();
 useEffect(()=>{fetch("http://127.0.0.1:8000/api/v1/leads").then(r=>r.json()).then(x=>setLeads(x.items));fetch("http://127.0.0.1:8000/api/v1/leads/date-range?kind=previous_month").then(r=>r.json()).then(setRange)},[]);
 return <main className="container"><h1>AI Lead Discovery & Intelligence</h1><p>LinkedIn activity and intent intelligence</p><div className="grid"><div className="card"><b>Previous Month</b><p>{range?.start} → {range?.end}</p></div><div className="card"><b>Leads</b><p>{leads.length}</p></div></div><h2>Activity Leads</h2><div className="grid">{leads.map(l=><div className="card" key={l.id}><h3>{l.full_name}</h3><p>{l.job_title} · {l.company}</p><p>Score: <b>{l.score}</b> · Intent: {l.intent}</p><p>{l.signal_type} · {l.post_date}</p><a href={l.post_url} target="_blank">View LinkedIn result</a></div>)}</div></main>
}
