'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useState } from 'react';
import dynamic from 'next/dynamic';
import styles from './page.module.css';

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false }
);

export default function Assessment() {
  const router = useRouter();
  const pathname = usePathname();
  const hash = pathname.split('/').pop();
  const [showWarning, setShowWarning] = useState(false);
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);

  const handleRunCode = async () => {
    setIsExecuting(true);
    setOutput('');
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/execute-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();
      
      if (data.success) {
        setOutput(data.output);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to execute code. Please try again.');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleBack = () => {
    router.push(`/resume-report/${hash}`);
  };

  const handleHome = () => {
    if (showWarning) {
      router.push('/');
    } else {
      setShowWarning(true);
      setTimeout(() => setShowWarning(false), 3000); // Hide warning after 3 seconds
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.breadcrumbs}>
        <button onClick={handleHome} className={styles.breadcrumbLink}>Upload</button>
        <span className={styles.breadcrumbSeparator}>/</span>
        <button onClick={handleBack} className={styles.breadcrumbLink}>Resume Report</button>
        <span className={styles.breadcrumbSeparator}>/</span>
        <span className={styles.breadcrumbCurrent}>Assessment</span>
      </div>

      {showWarning && (
        <div className={`${styles.notification} ${styles.errorNotification}`}>
          Warning: Going back to the upload page will reset your progress. Click the button again to confirm.
        </div>
      )}

      <div className={styles.content}>
        <h1 className={styles.title}>Assessment</h1>
        <p className={styles.description}>Python Code Editor:</p>
        
        <div className={styles.editorContainer}>
          <MonacoEditor
            height="400px"
            defaultLanguage="python"
            theme="vs-dark"
            onChange={(value) => setCode(value || '')}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </div>

        <div className={styles.outputContainer}>
          <h3 className={styles.outputTitle}>Output:</h3>
          <pre className={styles.output}>
            {output || 'Run your code to see the output here'}
          </pre>
          {error && (
            <pre className={styles.error}>{error}</pre>
          )}
        </div>

        <button 
          onClick={handleRunCode} 
          className={styles.runButton}
          disabled={isExecuting}
        >
          {isExecuting ? 'Running...' : 'Run Code'}
        </button>
        
        <div className={styles.navigation}>
          <button onClick={handleBack} className={styles.backButton}>
            Back to Report
          </button>
          <button 
            onClick={handleHome} 
            className={styles.homeButton}
          >
            Return to Upload
          </button>
        </div>
      </div>
    </div>
  );
}
