import { useRef, useState } from 'react'
import { UploadCloud, X } from 'lucide-react'

export function DatasetUploadPanel({ onAnalyze, onLoadOfficial, busy }) {
  const [files, setFiles] = useState([])
  const input = useRef(null)

  function addFiles(fileList) {
    if (!fileList) return
    setFiles(current => [...current, ...Array.from(fileList)].filter((file, index, all) => all.findIndex(item => item.name === file.name) === index))
  }

  return <section className="hero">
    <div><span className="eyebrow">DEPENDENCY INTELLIGENCE</span><h1>Understand Your System<br />Before It Fails</h1><p>Upload service dependency definitions to visualize architecture, simulate failures, and analyze change impact.</p></div>
    <div className="upload-card" onDragOver={event => event.preventDefault()} onDrop={event => { event.preventDefault(); addFiles(event.dataTransfer.files) }}>
      <div className="upload-icon"><UploadCloud /></div><h2>Upload Dependency Dataset</h2><p>Drag & drop YAML files here</p>
      <button className="text-button" onClick={() => input.current?.click()}>or Browse Files</button>
      <input ref={input} hidden multiple type="file" accept=".yaml,.yml" onChange={event => addFiles(event.target.files)} />
      <div className="file-list">{files.map(file => <span key={file.name}>✓ {file.name}<button aria-label={`Remove ${file.name}`} onClick={() => setFiles(files.filter(item => item !== file))}><X size={13} /></button></span>)}</div>
      <button className="primary" disabled={!files.length || busy} onClick={() => onAnalyze(files)}>{busy ? 'Building dependency graph…' : 'Analyze Uploaded Files'}</button>
      <div className="or-divider"><span>OR</span></div><button className="secondary official-button" disabled={busy} onClick={onLoadOfficial}>Load Official 15-Component Dataset</button>
      <small>Secure YAML parsing · Up to 1 MB per file</small>
    </div>
  </section>
}
