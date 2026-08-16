import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

export default function TestCasePanel({ onGenerate, loading, result, error }) {
  const [issueId, setIssueId] = useState('KAN-5')

  const handleSubmit = (e) => {
    e.preventDefault()
    const val = issueId.trim().toUpperCase()
    if (val) onGenerate(val)
  }

  return (
    <div className="panel">
      {/* Search Bar */}
      <div className="search-bar">
        <form className="search-form" onSubmit={handleSubmit}>
          <label className="search-label" htmlFor="issue-input">Jira Issue ID</label>
          <input
            id="issue-input"
            className="search-input"
            type="text"
            value={issueId}
            onChange={(e) => setIssueId(e.target.value)}
            placeholder="KAN-5"
            disabled={loading}
          />
          <button
            className="btn-primary btn-generate"
            type="submit"
            disabled={loading || !issueId.trim()}
          >
            {loading ? (
              <span className="spinner-row">
                <span className="spinner" /> Generating…
              </span>
            ) : (
              '▶ Generate Test Cases'
            )}
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="alert-error">
          <span className="alert-icon">⚠</span> {error}
        </div>
      )}

      {/* Empty State */}
      {!result && !error && !loading && (
        <div className="empty-state">
          <div className="empty-icon">🧪</div>
          <h2>Enter a Jira Issue ID to generate test cases</h2>
          <p>The app fetches the issue from Jira and uses GROQ to generate<br/>
            3 test cases: Happy Path · Negative · Edge Case</p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="empty-state">
          <div className="pulse-ring" />
          <h2>Fetching issue and generating test cases…</h2>
          <p>Connecting to Jira → GROQ ({issueId})</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="result-area">
          {/* Issue Metadata Card */}
          <div className="issue-card">
            <div className="issue-card-top">
              <span className="issue-key">{result.issue.key}</span>
              <span className="badge">{result.issue.issue_type}</span>
              <span className={`badge priority-${result.issue.priority.toLowerCase()}`}>
                {result.issue.priority}
              </span>
              <span className="badge status">{result.issue.status}</span>
            </div>
            <div className="issue-summary">{result.issue.summary}</div>
            <div className="issue-meta">
              Assignee: {result.issue.assignee}
            </div>
          </div>

          {/* Test Cases */}
          <div className="tc-header">
            <h2>Generated Test Cases</h2>
            <button
              className="btn-ghost btn-copy"
              onClick={() => navigator.clipboard.writeText(result.test_cases_md)}
              title="Copy markdown"
            >
              📋 Copy
            </button>
          </div>
          <div className="tc-body">
            <ReactMarkdown>{result.test_cases_md}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}
