'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useState } from 'react';
import styles from './page.module.css';
import CodeEditor from '@/components/CodeEditor';
import AssessmentEditor from '@/components/AssessmentEditor';

export default function Assessment() {
  const router = useRouter();
  const pathname = usePathname();
  const hash = pathname.split('/').pop();
  const [showWarning, setShowWarning] = useState(false);

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
        <p className={styles.description}>Code Editor:</p>
        
        <CodeEditor />

        <p className={styles.description}>Code Review:</p>

        <AssessmentEditor />

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
