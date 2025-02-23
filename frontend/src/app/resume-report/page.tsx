"use client";

import { useRouter, usePathname } from "next/navigation";
import styles from "./page.module.css";
import Breadcrumbs from "@/components/Breadcrumbs";
import { useEffect, useState } from "react";

export default function ResumeReport() {
  const router = useRouter();

  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    fetch("/api/get-analysis")
      .then((response) => {
        if (response.status === 403) {
          router.push("/");
        }
        return response.json();
      })
      .then((data) => {
        setReport(data);
      });
  }, []);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const checkGrift = async () => {
      try {
        const formData = new FormData();
        const response = await fetch('/api/grift_check', {
          method: 'POST',
          body: formData
        }).then((response) => {
          if (response.status === 403) {
            router.push("/");
          }
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get annotated PDF');
      } finally {
        setIsLoading(false);
      }
    };

      checkGrift();
  }, []);

  const handleNext = () => {
    router.push(`/assessment`);
  };

  const handleBack = () => {
    router.push("/");
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
        ) : true ? (
          <div className={styles.analysis}>
            <div className={styles.pdfContainer}>
              <h2>Annotated Resume Analysis</h2>
              <iframe 
                src={`http://localhost:8000/api/annotated-pdf`}
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
