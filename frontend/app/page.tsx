"use client";

import {useEffect,useState} from "react";

const API="/api/backend";

export default function Home(){
 const [leads,setLeads]=useState<any[]>([]),[range,setRange]=useState<any>();
 useEffect(()=>{
   fetch(API+"/leads").then(r=>r.json()).then(setLeads);
   fetch(API+"/leads/date-range?kind=previous_month").then(r=>r.json()).then(setRange);
 },[]);
 return <main className="container"><header><h1>AI Lead Discovery</h1><p>LinkedIn activity & buying-intent intelligence</p></header><section className="grid"><div className="card"><b>Previous month</b><p>{range?.start} → {range?.end}</p></div><div className="card"><b>Leads</b><p>{leads.length}</p></div></section><h2>Activity signals</h2><div className="grid">{leads.map(l=><article className="card" key={l.id}><h3>{l.full_name}</h3><p>{l.job_title||"—"} · {l.company||"—"}</p><p><b>{l.score}</b> score · {l.intent} intent</p><p>{l.signal_type} · {l.post_date?.slice(0,10)||"—"}</p>{l.evidence&&<p>{l.evidence}</p>}{l.post_url&&<a href={l.post_url} target="_blank" rel="noreferrer">Open activity</a>}</article>)}</div></main>
}
