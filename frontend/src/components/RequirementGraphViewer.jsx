import { useMemo } from 'react'
import { Background, Controls, MarkerType, MiniMap, ReactFlow } from '@xyflow/react'
import '@xyflow/react/dist/style.css'

const colors = { service: '#f5bd24', application: '#75401d', database: '#4f6d62', external_system: '#b97834', unresolved: '#9a8d84' }

export function RequirementGraphViewer({ analysis, selected, onSelect, impact, filter }) {
  const graphData = useMemo(() => {
    const baseIds = new Set(analysis.graph.nodes.map(node => node.id))
    const scenarioNames = [...(impact?.direct_impact || []), ...(impact?.indirect_impact || [])]
    const virtualNodes = scenarioNames.filter(name => !baseIds.has(name)).map(name => ({ id: name, name, type: name.includes('App') ? 'application' : 'service', virtual: true }))
    const virtualEdges = virtualNodes.map((node, index) => ({ source: impact?.direct_impact[index % Math.max(1, impact.direct_impact.length)] || selected || '', target: node.id, virtual: true }))
    return { nodes: [...analysis.graph.nodes, ...virtualNodes], edges: [...analysis.graph.edges, ...virtualEdges] }
  }, [analysis, impact, selected])

  const visible = useMemo(() => new Set(graphData.nodes.filter(node => filter === 'all' || node.type === filter || (filter === 'high' && analysis.risk_analysis.some(risk => risk.name === node.id && ['HIGH', 'CRITICAL'].includes(risk.level))) || (filter === 'spof' && analysis.potential_spofs.some(candidate => candidate.name === node.id))).map(node => node.id)), [analysis, filter, graphData])

  const nodes = graphData.nodes.filter(node => visible.has(node.id)).map((node, index) => {
    const direct = impact?.direct_impact.includes(node.id)
    const indirect = impact?.indirect_impact.includes(node.id)
    const saved = impact?.saved_components?.includes(node.id)
    const failed = impact?.failed_component === node.id
    const typeLabel = node.type === 'service' ? 'API' : node.type.replace('_', ' ').toUpperCase()
    return { id: node.id, position: { x: (index % 4) * 230, y: Math.floor(index / 4) * 145 }, data: { label: <div><small>{typeLabel}{node.virtual ? ' · SCENARIO' : ''}</small><strong>{node.name}</strong>{failed && <b>FAILED</b>}</div> }, className: `graph-node ${selected === node.id ? 'selected' : ''} ${failed ? 'failed' : saved ? 'protected-saved' : direct ? 'direct' : indirect ? 'indirect' : ''}`, style: { background: colors[node.type], opacity: impact && !failed && !direct && !indirect && !saved ? .32 : 1 } }
  })

  const edges = graphData.edges.filter(edge => visible.has(edge.source) && visible.has(edge.target)).map((edge, index) => {
    const protectedEdge = impact?.protected_link?.source === edge.target && impact.protected_link.target === edge.source
    return { id: `edge-${index}`, source: edge.source, target: edge.target, label: protectedEdge ? 'STOPPER' : undefined, markerEnd: { type: MarkerType.ArrowClosed }, animated: protectedEdge || Boolean(impact && (impact.direct_impact.includes(edge.source) || impact.indirect_impact.includes(edge.target))), style: { stroke: protectedEdge ? '#1f9d55' : edge.virtual ? '#df7626' : '#6b3a1e', strokeWidth: protectedEdge ? 5 : edge.virtual ? 2.8 : 1.8, strokeDasharray: edge.virtual ? '5 4' : undefined }, labelStyle: protectedEdge ? { fill: '#146c3a', fontWeight: 800, fontSize: 10 } : undefined }
  })

  return <div className="graph-wrap"><ReactFlow nodes={nodes} edges={edges} onNodeClick={(_, node) => onSelect(node.id)} fitView minZoom={.25}><Background color="#cfbca6" /><Controls /><MiniMap nodeColor={node => String(node.style?.background || '#f5bd24')} /></ReactFlow><div className="legend">{Object.entries(colors).map(([type, color]) => <span key={type}><i style={{ background: color }} />{type === 'service' ? 'API' : type.replace('_', ' ')}</span>)}</div></div>
}
