import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import RipDashboard from './RipDashboard.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode><RipDashboard /></StrictMode>,
)
