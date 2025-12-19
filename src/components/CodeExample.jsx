import React, { useState } from 'react';
import CodeBlock from '@theme/CodeBlock';

/**
 * CodeExample Component
 *
 * Renders a code example with metadata and copy-to-clipboard functionality.
 *
 * Props:
 * - title: string - Brief description of the code example
 * - language: string - Programming language (python, cpp, bash, yaml, etc.)
 * - code: string - The actual code content
 * - framework: string - Framework/library (ros2, isaac-sim, pytorch, generic)
 * - expectedOutput: string - What running the code should produce (optional)
 * - troubleshooting: string - Common errors and solutions (optional)
 */
export default function CodeExample({
  title,
  language,
  code,
  framework = 'generic',
  expectedOutput,
  troubleshooting,
  children
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code || children);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  return (
    <div className="code-example" style={{ marginBottom: '2rem' }}>
      <div
        className="code-example-header"
        style={{
          backgroundColor: 'var(--ifm-color-emphasis-100)',
          padding: '0.75rem 1rem',
          borderRadius: '4px 4px 0 0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid var(--ifm-color-emphasis-300)'
        }}
      >
        <div>
          <strong>{title}</strong>
          {framework && framework !== 'generic' && (
            <span
              style={{
                marginLeft: '0.5rem',
                fontSize: '0.875rem',
                color: 'var(--ifm-color-primary)',
                fontWeight: 'normal'
              }}
            >
              [{framework}]
            </span>
          )}
        </div>
        <button
          className="copy-button"
          onClick={handleCopy}
          style={{
            backgroundColor: copied ? 'var(--ifm-color-success)' : 'var(--ifm-color-primary)',
            color: 'white',
            border: 'none',
            padding: '0.375rem 0.75rem',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.875rem',
            transition: 'background-color 0.2s'
          }}
          aria-label={copied ? 'Code copied' : 'Copy code to clipboard'}
        >
          {copied ? '✓ Copied!' : 'Copy'}
        </button>
      </div>

      <CodeBlock language={language}>
        {code || children}
      </CodeBlock>

      {expectedOutput && (
        <div
          style={{
            backgroundColor: 'var(--ifm-color-emphasis-100)',
            padding: '0.75rem 1rem',
            marginTop: '0.5rem',
            borderRadius: '4px',
            borderLeft: '4px solid var(--ifm-color-success)'
          }}
        >
          <strong>Expected Output:</strong>
          <pre style={{ margin: '0.5rem 0 0 0', whiteSpace: 'pre-wrap' }}>
            {expectedOutput}
          </pre>
        </div>
      )}

      {troubleshooting && (
        <details
          style={{
            backgroundColor: 'var(--ifm-color-warning-lightest)',
            padding: '0.75rem 1rem',
            marginTop: '0.5rem',
            borderRadius: '4px',
            borderLeft: '4px solid var(--ifm-color-warning)'
          }}
        >
          <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
            🔧 Troubleshooting
          </summary>
          <div style={{ marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
            {troubleshooting}
          </div>
        </details>
      )}
    </div>
  );
}
