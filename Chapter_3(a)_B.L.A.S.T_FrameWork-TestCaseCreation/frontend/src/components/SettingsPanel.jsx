import { useState } from 'react'

export default function SettingsPanel({ settings, onSave, onClose }) {
  const [form, setForm] = useState({ ...settings })

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>⚙ Configuration</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="settings-section">
            <div className="settings-section-title">
              <span className="settings-icon">🔗</span> Jira
            </div>
            <label className="field-label">
              Base URL
              <input
                className="field-input"
                type="text"
                placeholder="https://yoursite.atlassian.net"
                value={form.jira_url}
                onChange={set('jira_url')}
              />
            </label>
            <label className="field-label">
              Email
              <input
                className="field-input"
                type="email"
                placeholder="you@example.com"
                value={form.jira_email}
                onChange={set('jira_email')}
              />
            </label>
            <label className="field-label">
              API Token
              <input
                className="field-input"
                type="password"
                placeholder="ATATT3x..."
                value={form.jira_token}
                onChange={set('jira_token')}
              />
            </label>
          </div>

          <div className="settings-section">
            <div className="settings-section-title">
              <span className="settings-icon">🤖</span> GROQ
            </div>
            <label className="field-label">
              API Key
              <input
                className="field-input"
                type="password"
                placeholder="gsk_..."
                value={form.groq_key}
                onChange={set('groq_key')}
              />
            </label>
            <label className="field-label">
              Model
              <input
                className="field-input"
                type="text"
                placeholder="llama-3.3-70b-versatile"
                value={form.model}
                onChange={set('model')}
              />
              <span className="field-hint">Leave blank to use server default</span>
            </label>
          </div>

          <p className="settings-note">
            Credentials are saved to localStorage only. Leave blank to use server .env values.
          </p>
        </div>

        <div className="modal-footer">
          <button className="btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={() => onSave(form)}>
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}
