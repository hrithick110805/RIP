import { useMemo, useState } from 'react'
import { AlertTriangle, Boxes, Database, Globe2, HeartPulse, Search, Server, ShieldAlert } from 'lucide-react'
import { BrandHeader } from './components/BrandHeader.jsx'
import { DatasetUploadPanel } from './components/DatasetUploadPanel.jsx'
import { RequirementGraphViewer } from './components/RequirementGraphViewer.jsx'
import { RiskAnalysisTable } from './components/RiskAnalysisTable.jsx'
import { ServiceDetailsPanel } from './components/ServiceDetailsPanel.jsx'
import { dependencyAnalysisApi } from './services/dependencyAnalysisApi.js'
import './styles.css'
import './requirementsCorrections.css'

export default function RipDashboard() {
  const [analysis, setAnalysis] = useState(null)
  const [selected, setSelected] = useState(null)
  const [impact, setImpact] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('all')
  const selectedComponent = analysis?.components.find(component => component.name === selected) || null
  const searchResults = useMemo(() => analysis?.components.filter(component => component.name.toLowerCase().includes(query.toLowerCase())).slice(0, 6) || [], [analysis, query])

  function showAnalysis(result) {
    setAnalysis(result)
    setImpact(null)
    setSelected(null)
    setTimeout(() => document.querySelector('#overview')?.scrollIntoView({ behavior: 'smooth' }), 50)
  }

  async function analyzeFiles(files) {
    setBusy(true); setError('')
    try { showAnalysis(await dependencyAnalysisApi.analyze(files)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Analysis failed') }
    finally { setBusy(false) }
  }

  async function loadOfficialDataset() {
    setBusy(true); setError('')
    try { showAnalysis(await dependencyAnalysisApi.loadOfficialDataset()) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not load the official dataset') }
    finally { setBusy(false) }
  }

  async function runAnalysis(kind) {
    if (!selected) return
    setBusy(true); setError('')
    try {
      const result = kind === 'failure' ? await dependencyAnalysisApi.simulateFailure(selected) : await dependencyAnalysisApi.analyzeChange(selected)
      setImpact(result)
      setSelected(null)
      setTimeout(() => document.querySelector('#impact-analysis')?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Request failed') }
    finally { setBusy(false) }
  }

  async function deployStopper() {
    const failedComponent = impact?.failed_component
    const protectedConsumer = impact?.direct_impact[0]
    if (!failedComponent || !protectedConsumer) return
    setBusy(true); setError('')
    try { setImpact(await dependencyAnalysisApi.deployRippleStopper(failedComponent, protectedConsumer)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Could not deploy Ripple Stopper') }
    finally { setBusy(false) }
  }

  const mostConnected = analysis?.structural_analysis.most_connected[0]
  const criticalCandidate = analysis?.risk_analysis[0]
  const largestBlast = analysis?.risk_analysis.slice().sort((first, second) => second.blast_radius - first.blast_radius || second.score - first.score)[0]

  return <><BrandHeader /><main>
    <DatasetUploadPanel onAnalyze={analyzeFiles} onLoadOfficial={loadOfficialDataset} busy={busy} />
    {error && <div className="error"><AlertTriangle /> {error}</div>}
    {analysis && <>
      <section id="overview"><div className="section-title"><div><span className="eyebrow">LIVE DATASET</span><h2>Required Dashboard Metrics</h2>{analysis.dataset_context && <p className="dataset-context">✓ {analysis.dataset_context}</p>}</div><div className="search"><Search size={18} /><input placeholder="Search components…" value={query} onChange={event => setQuery(event.target.value)} />{query && <div className="results">{searchResults.length ? searchResults.map(component => <button key={component.name} onClick={() => { setSelected(component.name); setQuery('') }}>{component.name}<small>{component.type === 'service' ? 'API' : component.type}</small></button>) : <p>No matching components</p>}</div>}</div></div>
        <div className="metrics"><Metric icon={<Server />} label="Total Services / APIs" value={analysis.metrics.service} /><Metric icon={<Globe2 />} label="Total Applications" value={analysis.metrics.application} /><Metric icon={<Database />} label="Total Databases" value={analysis.metrics.database} /><Metric icon={<Globe2 />} label="Total External Systems" value={analysis.metrics.external_system} /><Metric icon={<Boxes />} label="Total Components" value={analysis.metrics.total_components} /><Metric icon={<Boxes />} label="Most Connected Service" value={mostConnected?.name || '—'} compact /><Metric icon={<ShieldAlert />} label="Critical Service Candidate" value={criticalCandidate?.name || '—'} compact /><Metric icon={<AlertTriangle />} label="Largest Blast Radius" value={largestBlast?.name || '—'} compact /><Metric icon={<HeartPulse />} label="Criticality Score" value={`${largestBlast?.blast_radius || 0} downstream`} compact /><Metric icon={<HeartPulse />} label="Architecture Health" value={`${analysis.architecture_health.score}/100`} /></div>
      </section>
      <section id="dependency-graph" className="card graph-card"><div className="section-title"><div><span className="eyebrow">INTERACTIVE MAP</span><h2>Dependency Graph</h2></div><div className="filters">{[['all', 'All'], ['service', 'APIs'], ['application', 'Applications'], ['database', 'Databases'], ['external_system', 'External'], ['high', 'High Risk'], ['spof', 'Potential SPOF']].map(([value, label]) => <button className={filter === value ? 'active' : ''} onClick={() => setFilter(value)} key={value}>{label}</button>)}</div></div><RequirementGraphViewer analysis={analysis} selected={selected} onSelect={setSelected} impact={impact} filter={filter} /></section>
      {impact && <ImpactPanel impact={impact} onDeployStopper={deployStopper} busy={busy} />}
      <section className="analysis-grid"><ConnectedComponents analysis={analysis} /><ArchitectureHealth health={analysis.architecture_health} /><BusinessInsights insights={analysis.business_insights} /></section>
      <section className="analysis-grid"><PotentialFailures candidates={analysis.potential_spofs} /><Cycles cycles={analysis.cycles} /><CriticalPaths paths={analysis.critical_paths} /></section>
      <section id="risk-analysis"><RiskAnalysisTable risks={analysis.risk_analysis} /></section>
      {selectedComponent && <ServiceDetailsPanel item={selectedComponent} onFailure={() => runAnalysis('failure')} onChange={() => runAnalysis('change')} onClose={() => setSelected(null)} busy={busy} />}
    </>}
  </main><footer><strong>RIP</strong> — Resilient Impact Platform <span>Deterministic graph intelligence. No AI required.</span></footer></>
}

function Metric({ icon, label, value, compact = false }) {
  return <div className={`metric ${compact ? 'compact' : ''}`}><i>{icon}</i><span>{label}<strong>{value}</strong></span></div>
}

function ImpactPanel({ impact, onDeployStopper, busy }) {
  const title = impact.stopper_deployed ? 'RIPPLE STOPPER ACTIVE' : impact.failed_component ? 'FAILURE IMPACT ANALYSIS' : 'CHANGE IMPACT ANALYSIS'
  return <section id="impact-analysis" className={`card impact ${impact.stopper_deployed ? 'stopper-active' : ''}`}>
    <div className="section-title"><div><span className="eyebrow">{title}</span><h2>{impact.failed_component || impact.modified_component}</h2></div><div className="blast"><strong>{impact.blast_radius}</strong><span>Impacted<br />Components</span></div></div>
    <div className="impact-columns"><ImpactList title="Direct Impact" values={impact.direct_impact} /><ImpactList title="Indirect Impact" values={impact.indirect_impact} /><div><h3>Affected Applications</h3>{impact.affected_applications.length ? <ul>{impact.affected_applications.map(name => <li key={name}>{name}</li>)}</ul> : <p>None</p>}<p>Databases: <b>{impact.affected_databases.length}</b></p><p>External systems: <b>{impact.affected_external_systems.length}</b></p>{impact.risk_level && <span className={`pill ${impact.risk_level.toLowerCase()}`}>{impact.risk_level} RISK</span>}</div></div>
    {impact.failed_component && <div className="impact-story"><div><span className="eyebrow">IMPACT STORY</span><h3>{impact.stopper_deployed ? 'Protection layer deployed' : 'Stop the ripple before it spreads'}</h3><p>{impact.stopper_deployed ? impact.explanation : 'Test a queue, retry process, cache, or backup route on the first vulnerable dependency link, then see the reduced impact immediately.'}</p></div>{impact.stopper_deployed ? <div className="saved-summary"><strong>{impact.systems_saved}</strong><span>systems saved</span><small>Blast radius {impact.original_blast_radius} → {impact.reduced_blast_radius}</small><b>Protected: {impact.protected_link?.source} → {impact.protected_link?.target}</b><div>{impact.protection_options?.map(option => <em key={option}>{option}</em>)}</div></div> : <button className="stopper-button" disabled={busy || !impact.direct_impact.length} onClick={onDeployStopper}>Deploy Stopper</button>}</div>}
    {impact.recommended_test_scope && <div className="test-plan"><h3>Suggested Test Scope</h3>{impact.recommended_test_scope.map(group => <div key={group.priority}><b>{group.priority}</b>{group.tests.length ? <ul>{group.tests.map(test => <li key={test}>{test}</li>)}</ul> : <p>No tests at this level.</p>}</div>)}<small>{impact.explanation}</small></div>}
  </section>
}

function ImpactList({ title, values }) { return <div><h3>{title}</h3>{values.length ? <ul>{values.map(value => <li key={value}>{value}</li>)}</ul> : <p>None</p>}</div> }
function ConnectedComponents({ analysis }) { return <div className="card"><span className="eyebrow">GRAPH STRUCTURE</span><h2>Most Connected</h2>{analysis.structural_analysis.most_connected.map((row, index) => <div className="rank" key={row.name}><b>{index + 1}</b><span>{row.name}<small>{row.downstream_reach} downstream reach</small></span><strong>{row.connections}</strong></div>)}</div> }
function ArchitectureHealth({ health }) { return <div className="card"><span className="eyebrow">ARCHITECTURE HEALTH</span><h2>{health.score} / 100</h2><div className="healthbar"><i style={{ width: `${health.score}%` }} /></div>{health.positive_findings.map(item => <p className="finding good" key={item}>✓ {item}</p>)}{health.warnings.map(item => <p className="finding warn" key={item}>⚠ {item}</p>)}<small>{health.disclaimer}</small></div> }
function BusinessInsights({ insights }) { return <div className="card"><span className="eyebrow">BUSINESS TRANSLATION</span><h2>Business Insights</h2>{insights.map(item => <p className="insight" key={item}>{item}</p>)}</div> }
function PotentialFailures({ candidates }) { return <div className="card"><h2>Potential Single Points of Failure</h2>{candidates.length ? candidates.map(item => <div className="spof" key={item.name}><ShieldAlert /><span><b>{item.name}</b><small>Blast radius: {item.blast_radius} · {item.reason}</small></span></div>) : <p>No potential SPOFs detected.</p>}</div> }
function Cycles({ cycles }) { return <div className="card"><h2>Circular Dependencies</h2>{cycles.length ? cycles.map((cycle, index) => <p className="cycle" key={index}>{cycle.join(' → ')}</p>) : <p className="finding good">✓ No circular dependencies detected</p>}</div> }
function CriticalPaths({ paths }) { return <div className="card"><h2>Critical Dependency Paths</h2>{paths.length ? paths.map((item, index) => <p className="path" key={index}>{item.path.join(' → ')}<small>{item.length} relationships</small></p>) : <p>No multi-level paths detected.</p>}</div> }
