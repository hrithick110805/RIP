const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
let activeAnalysisId = ''

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, options)
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    const detail = typeof body.detail === 'string' ? body.detail : body.detail?.details || JSON.stringify(body.detail)
    throw new Error(detail)
  }
  return response.json()
}

async function beginAnalysis(path, options) {
  const result = await request(path, options)
  activeAnalysisId = result.analysis_id
  return result
}

function withSession(path) {
  return `${path}?analysis_id=${encodeURIComponent(activeAnalysisId)}`
}

export const dependencyAnalysisApi = {
  analyze(files) {
    const form = new FormData()
    files.forEach(file => form.append('files', file))
    return beginAnalysis('/analyze', { method: 'POST', body: form })
  },
  loadOfficialDataset() {
    return beginAnalysis('/load-official-dataset', { method: 'POST' })
  },
  simulateFailure(name) {
    return request(withSession(`/simulate-failure/${encodeURIComponent(name)}`), { method: 'POST' })
  },
  deployRippleStopper(name, consumer) {
    const path = withSession(`/deploy-ripple-stopper/${encodeURIComponent(name)}`)
    return request(`${path}&protected_consumer=${encodeURIComponent(consumer)}`, { method: 'POST' })
  },
  analyzeChange(name) {
    return request(withSession(`/change-impact/${encodeURIComponent(name)}`), { method: 'POST' })
  },
}
