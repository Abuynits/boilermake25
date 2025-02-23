'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import styles from './page.module.css';
import Breadcrumbs from '@/components/Breadcrumbs';

export default function ResumeReport() {
  const router = useRouter();
  const pathname = usePathname();
  const hash = pathname.split('/').pop();

  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const checkGrift = async () => {
      try {
        const formData = new FormData();
        formData.append('hash', hash || '');

        const response = await fetch('http://localhost:8000/api/grift_check', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('Failed to get annotated PDF');
        }

        const data = await response.json();
        if (data.out_path) {
          setPdfPath(data.out_path);
        } else {
          throw new Error('No PDF path returned');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get annotated PDF');
      } finally {
        setIsLoading(false);
      }
    };

    if (hash) {
      checkGrift();
    }
  }, [hash]);

  const handleNext = () => {
    router.push(`/assessment/${hash}`);
  };

  const handleBack = () => {
    router.push('/');
  };

  return (
    <div className={styles.container}>
      <Breadcrumbs items={[]} />

      <div className={styles.content}>
        <h1 className={styles.title}>Resume Report</h1>
        
        {isLoading ? (
          <div className={styles.loading}>Loading annotated resume...</div>
        ) : error ? (
          <div className={styles.error}>{error}</div>
        ) : pdfPath ? (
          <div className={styles.analysis}>
            <div className={styles.pdfContainer}>
              <h2>Annotated Resume Analysis</h2>
              <iframe 
                src={`http://localhost:8000${pdfPath}`}
                className={styles.pdfViewer}
                title="Annotated Resume"
              />
            </div>
          </div>
        ) : (
          <p className={styles.description}>No annotated resume available.</p>
        )}
        
        <div className={styles.navigation}>
          <button onClick={handleBack} className={styles.backButton}>
            Back to Upload
          </button>
          <button onClick={handleNext} className={styles.nextButton}>
            Continue to Assessment
          </button>
        </div>
      </div>
    </div>
  );
}
