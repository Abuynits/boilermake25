'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import styles from './page.module.css';
import CodeEditor from '@/components/CodeEditor';
import AssessmentEditor from '@/components/AssessmentEditor';
import Breadcrumbs from '@/components/Breadcrumbs';

export default function Assessment() {
  const router = useRouter();
  const [showWarning, setShowWarning] = useState(false);

  const handleBack = () => {
    router.push(`/resume-report`);
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
      <Breadcrumbs items={[]} />

      <div className={styles.content}>
        <h1 className={styles.title}>Assessment Suite</h1>
        <h2 className={styles.description}>Code Editor</h2>
        
        <CodeEditor />

        <h2 className={styles.description} style={{marginTop: "2rem", marginBottom: "0px"}}>Code Review</h2>

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
