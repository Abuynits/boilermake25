'use client';

import { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import styles from './page.module.css';
import CodeEditor from '@/components/CodeEditor';
import AssessmentEditor from '@/components/AssessmentEditor';
import Breadcrumbs from '@/components/Breadcrumbs';

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
      <Breadcrumbs items={[]} />

      <div className={styles.content}>
        <h1 className={styles.title}>Assessment Suite</h1>
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
