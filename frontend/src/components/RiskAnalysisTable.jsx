export function RiskAnalysisTable({ risks }) {
  return <div className="card table-card">
    <div className="section-title"><div><span className="eyebrow">DETERMINISTIC SCORING</span><h2>Component Risk Ranking</h2></div><p>40% blast radius · 25% app impact · 20% centrality · 15% depth</p></div>
    <div className="table-scroll"><table><thead><tr><th>Component</th><th>Type</th><th>Score</th><th>Risk</th><th>Blast Radius</th><th>Apps Affected</th></tr></thead><tbody>{risks.map(risk => <tr key={risk.name}><td><b>{risk.name}</b></td><td>{risk.type === 'service' ? 'API' : risk.type.replace('_', ' ')}</td><td><strong>{risk.score}</strong></td><td><span className={`pill ${risk.level.toLowerCase()}`}>{risk.level}</span></td><td>{risk.blast_radius}</td><td>{risk.applications_affected}</td></tr>)}</tbody></table></div>
    <small>RIP Composite Risk Score is an explainable project metric, not an industry-standard universal score.</small>
  </div>
}
