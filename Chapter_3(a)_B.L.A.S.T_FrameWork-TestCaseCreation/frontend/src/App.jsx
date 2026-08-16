import { useState } from 'react'
import SettingsPanel from './components/SettingsPanel'
import TestCasePanel from './components/TestCasePanel'

const DEFAULT_SETTINGS = {
  jira_url:   '',
  jira_email: '',
  jira_token: '',
  groq_key:   '',
  model:      'llama-3.3-70b-versatile',
}

function loadSettings() {
  try {
    return JSON.parse(localStorage.getItem('blast_tc_settings')) || DEFAULT_SETTINGS
  } catch {
    return DEFAULT_SETTINGS
  }
}

export default function App() {
  const [showSettings, setShowSettings] = useState(false)
  const [settings, setSettings]         = useState(loadSettings)
  const [result, setResult]             = useState(null)
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState(null)

  const saveSettings = (next) => {
    setSettings(next)
    localStorage.setItem('blast_tc_settings', JSON.stringify(next))
    setShowSettings(false)
  }

  const generate = async (issueId) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res  = await fetch('/api/generate', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ issue_id: issueId, settings }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || `Server error ${res.status}`)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <span className="header-icon">🧪</span>
          <div>
            <div className="header-title">Test Case Creator</div>
            <div className="header-sub">B.L.A.S.T Framework · Jira + GROQ</div>
          </div>
        </div>
        <button className="btn-settings" onClick={() => setShowSettings(true)}>
          ⚙ Settings
        </button>
      </header>

      <main className="main">
        <TestCasePanel
          onGenerate={generate}
          loading={loading}
          result={result}
          error={error}
        />
      </main>

      {showSettings && (
        <SettingsPanel
          settings={settings}
          onSave={saveSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}
