import React, { useEffect, useState, useMemo } from 'react'
import { runCheck, fetchHistory, fetchLast } from './lib/api'

function Toast({ msg, onClose }) {
  if (!msg) return null
  return <div className="toast">{msg} <button style={{marginLeft:8}} onClick={onClose}>✕</button></div>
}

function Modal({ open, children, onClose }) {
  if (!open) return null
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  )
}

function pretty(obj){ try { return JSON.stringify(obj, null, 2) } catch { return String(obj) } }

export default function App(){
  const [stats, setStats] = useState({total:320, healthy:300, anomalies:20})
  const [runs, setRuns] = useState([])
  const [selected, setSelected] = useState(null)
  const [busy, setBusy] = useState(false)
  const [toast, setToast] = useState(null)
  const [testId, setTestId] = useState('invoice_json_v1')
  const [engine, setEngine] = useState('mock')
  const [dryRun, setDryRun] = useState(true)

  useEffect(()=>{ (async ()=>{ const h = await fetchHistory(); setRuns(Array.isArray(h)?h:[]); const last = await fetchLast(); setStats(s=>({...s, healthy: last && !last.error_type? s.total: s.healthy, anomalies: last && last.error_type? 1: s.anomalies})) })() },[])

  const healthPct = useMemo(()=> Math.round(((stats.healthy||0)/(stats.total||1))*100), [stats])

  async function doRun(){
    setBusy(true); setToast(null)
    try{
      const payload = { test_id: testId, engine, dry_run_repair: !!dryRun }
      const data = await runCheck(payload)
      const entry = { id: (Date.now()).toString(36), agent: data.engine||engine, timestamp: new Date().toISOString(), error_type: data.analysis?.error_type || data.error_type || null, output: data }
      setRuns(r=> [entry, ...r].slice(0,50))
      setSelected(entry)
      setToast('Run completed')
    }catch(e){
      setToast('Run failed: ' + (e?.message||String(e)))
    }finally{ setBusy(false) }
  }

  return (
    <div>
      <header className="header">
        <div className="container" style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
          <div className="brand">
            <div className="badge">PHM</div>
            <div>
              <h1>PHM — Alchemyst Guard</h1>
              <p style={{marginTop:6, color:'#aeb9c6'}}>Saas DB watchdog — Royal Red · Steel Blue · Jet Black · Blood</p>
            </div>
          </div>
          <div className="row">
            <a className="btn" href="https://github.com/Alchemyst-ai/awesome-saas" target="_blank" rel="noreferrer">Awesome-SaaS</a>
            <button className="btn btn-primary" onClick={doRun} disabled={busy}>{busy?'Running…':'Run Check'}</button>
          </div>
        </div>
      </header>

      <main className="container" style={{paddingTop:20, paddingBottom:40}}>
        <section className="grid-3" style={{marginBottom:18}}>
          <div className="card">
            <div style={{fontSize:12, color:'#9aa6b3'}}>Entries</div>
            <div style={{fontSize:28, fontWeight:700, marginTop:6}}>{stats.total}</div>
            <div style={{marginTop:8, color:'#9aa6b3'}}>Total SaaS entries indexed</div>
          </div>
          <div className="card">
            <div style={{fontSize:12, color:'#9aa6b3'}}>Health</div>
            <div style={{fontSize:28, fontWeight:700, marginTop:6, color:'#7ec0e8'}}>{healthPct}%</div>
            <div style={{marginTop:8, color:'#9aa6b3'}}>Schema compliance (approx)</div>
          </div>
          <div className="card">
            <div style={{fontSize:12, color:'#9aa6b3'}}>Anomalies</div>
            <div style={{fontSize:28, fontWeight:700, marginTop:6, color:'#ff7b7b'}}>{stats.anomalies}</div>
            <div style={{marginTop:8, color:'#9aa6b3'}}>Flagged items</div>
          </div>
        </section>

        <section className="card" style={{marginBottom:18}}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h2>Run a PHM Check</h2>
            <div style={{display:'flex', gap:8}}>
              <button className="btn" onClick={()=>{ setTestId('invoice_json_v1'); setEngine('mock'); setDryRun(true) }}>Defaults</button>
              <button className="btn btn-danger" onClick={()=>{ setRuns([]); setSelected(null); setToast('History cleared') }}>Clear</button>
            </div>
          </div>
          <hr className="hr" />
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:12}}>
            <div>
              <div style={{fontSize:13, color:'#9aa6b3'}}>Test ID</div>
              <input className="input mt-1" value={testId} onChange={e=>setTestId(e.target.value)} />
            </div>
            <div>
              <div style={{fontSize:13, color:'#9aa6b3'}}>Engine</div>
              <select className="input mt-1" value={engine} onChange={e=>setEngine(e.target.value)}>
                <option value="mock">mock</option>
                <option value="openai">openai</option>
              </select>
            </div>
            <div>
              <div style={{fontSize:13, color:'#9aa6b3'}}>Dry-run repair</div>
              <select className="input mt-1" value={dryRun?'true':'false'} onChange={e=>setDryRun(e.target.value==='true')}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            </div>
          </div>
          <div style={{display:'flex', justifyContent:'flex-end', marginTop:12}}>
            <button className="btn btn-primary" onClick={doRun} disabled={busy}>{busy? 'Running…' : 'Run Now'}</button>
          </div>
        </section>

        <section className="card">
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h2>Recent Runs</h2>
            <div style={{color:'#9aa6b3'}}>Showing {runs.length}</div>
          </div>
          <div style={{marginTop:12, overflowX:'auto'}}>
            <table className="table">
              <thead>
                <tr><th>ID</th><th>Agent</th><th>Time</th><th>Status</th><th>Inspect</th></tr>
              </thead>
              <tbody>
                {runs.length === 0 ? <tr><td colSpan="5" className="text">No runs yet</td></tr> :
                  runs.map(r=>(
                    <tr key={r.id}>
                      <td>{r.id}</td>
                      <td>{r.agent}</td>
                      <td>{new Date(r.timestamp).toLocaleString()}</td>
                      <td>{r.error_type ? <span className="tag err">{r.error_type}</span> : <span className="tag ok">OK</span>}</td>
                      <td><button className="btn" onClick={()=>setSelected(r)}>Details</button></td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <footer className="container" style={{paddingTop:16}}>
        <hr className="hr" />
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', paddingTop:12, color:'#9aa6b3'}}>
          <div>© {new Date().getFullYear()} PHM — Alchemyst Guard</div>
          <div>Royal Red · Steel Blue · Jet Black · Blood</div>
        </div>
      </footer>

      <Toast msg={toast} onClose={()=>setToast(null)} />

      <Modal open={!!selected} onClose={()=>setSelected(null)}>
        {!selected? null : (
          <div>
            <h2>Run Details</h2>
            <hr className="hr" />
            <pre style={{whiteSpace:'pre-wrap', maxHeight:'60vh', overflow:'auto'}}>{pretty(selected.output)}</pre>
            <div style={{marginTop:10, display:'flex', justifyContent:'flex-end'}}><button className="btn" onClick={()=>setSelected(null)}>Close</button></div>
          </div>
        )}
      </Modal>
    </div>
  )
}
