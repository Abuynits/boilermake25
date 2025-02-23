'use client';

import { useRouter, usePathname } from 'next/navigation';
import styles from './page.module.css';
import Breadcrumbs from '@/components/Breadcrumbs';

export default function ResumeReport() {
  const router = useRouter();
  const pathname = usePathname();
  const hash = pathname.split('/').pop();

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
        <p className={styles.description}>Resume analysis details will be displayed here.</p>
        
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
