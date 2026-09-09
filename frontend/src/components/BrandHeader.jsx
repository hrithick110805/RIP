import { RipShieldLogo } from './RipShieldLogo.jsx'

export function BrandHeader() {
  return <header className="topbar">
    <a className="brand" href="#overview"><RipShieldLogo /><span><strong>RIP</strong><small>Resilient Impact Platform</small></span></a>
    <nav><a href="#overview">Overview</a><a href="#dependency-graph">Dependency Graph</a><a href="#impact-analysis">Impact Analysis</a><a href="#risk-analysis">Risk Analysis</a></nav>
    <span className="status"><i /> Operational</span>
  </header>
}
