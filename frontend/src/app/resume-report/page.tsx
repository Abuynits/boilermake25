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
        <p className={styles.description}>{JSON.stringify(report)}</p>

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
