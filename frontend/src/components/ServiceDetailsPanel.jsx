export function ServiceDetailsPanel({ item, onFailure, onChange, onClose, busy }) {
  return <aside className="details">
    <button className="close" onClick={onClose}>×</button><span className="tag">{item.type === 'service' ? 'API' : item.type.replace('_', ' ')}</span><h2>{item.name}</h2>
    <div className="risk-score"><strong>{item.risk.score}</strong><span>RIP Risk Score<br /><b>{item.risk.level}</b></span></div>
    <Information title="Upstream Dependencies" values={item.dependencies} /><Information title="Direct Downstream Consumers" values={item.consumers} />
    <div className="detail-grid"><span>Blast radius<b>{item.risk.blast_radius}</b></span><span>Potential SPOF<b>{item.potential_spof ? 'Yes' : 'No'}</b></span></div>
    <h3>Why this score?</h3><ul>{item.risk.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul>
    <button className="primary" disabled={busy} onClick={onFailure}>Simulate Failure</button><button className="secondary" disabled={busy} onClick={onChange}>Analyze Change</button>
  </aside>
}

function Information({ title, values }) {
  return <div className="info"><h3>{title}</h3>{values.length ? <div className="chips">{values.map(value => <span key={value}>{value}</span>)}</div> : <p>None</p>}</div>
}
