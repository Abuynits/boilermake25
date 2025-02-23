'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './page.module.css';

export default function Home() {
  const router = useRouter();
  const [resume, setResume] = useState<File | null>(null);
  const [jobPosting, setJobPosting] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Auto-dismiss notifications after 3 seconds
  const autoDismissNotification = (type: 'error' | 'success') => {
    setTimeout(() => {
      if (type === 'error') setError('');
      else setSuccess('');
    }, 3000);
  };

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError('');
    setSuccess('');
    const file = e.target.files?.[0];
    
    if (!file) return;
    
    // Check file type
    const fileType = file.type;
    const validTypes = ['application/pdf', 'text/plain'];
    if (!validTypes.includes(fileType)) {
      setError('Please upload only PDF or TXT files');
      autoDismissNotification('error');
      e.target.value = '';
      return;
    }

    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size should be less than 10MB');
      autoDismissNotification('error');
      e.target.value = '';
      return;
    }

    setResume(file);
  };

  const handleJobPostingChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setError('');
    setSuccess('');
    const text = e.target.value;
    
    // Check word count (rough estimate)
    const wordCount = text.trim().split(/\s+/).length;
    if (wordCount > 2000) {
      setError('Job posting should not exceed 2000 words');
      autoDismissNotification('error');
      return;
    }
    
    setJobPosting(text);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!resume) {
      setError('Please upload a resume');
      autoDismissNotification('error');
      return;
    }

    if (!jobPosting.trim()) {
      setError('Please enter a job posting');
      autoDismissNotification('error');
      return;
    }

    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('resume', resume);
      formData.append('job_posting', jobPosting);
      
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze resume');
      }
      
      setSuccess('Analysis complete! Redirecting to report...');
      // Short delay to show the success message before redirecting
      setTimeout(() => {
        router.push(`/resume-report`);
      }, 1000);
    } catch (_err) {
      setError('An error occurred while uploading. Please try again.');
      autoDismissNotification('error');
      console.error(_err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.formContainer}>
        <h1 className={styles.title}>Resume to Job Analysis Suite</h1>
        
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Resume Upload */}
          <div className={styles.formGroup}>
            <label htmlFor="resume" className={styles.label}>
              Upload Resume (PDF or TXT)
            </label>
            <input
              type="file"
              id="resume"
              accept=".pdf,.txt"
              onChange={handleResumeChange}
              className={styles.fileInput}
            />
          </div>

          {/* Job Posting */}
          <div className={styles.formGroup}>
            <label htmlFor="jobPosting" className={styles.label}>
              Job Posting
            </label>
            <textarea
              id="jobPosting"
              rows={6}
              value={jobPosting}
              onChange={handleJobPostingChange}
              placeholder="Paste job description here..."
              className={styles.textarea}
            />
          </div>

          {/* Notifications */}
          {error && (
            <div className={`${styles.notification} ${styles.errorNotification}`}>
              {error}
            </div>
          )}
          {success && (
            <div className={`${styles.notification} ${styles.successNotification}`}>
              {success}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className={styles.submitButton}
          >
            {isLoading ? 'Processing...' : 'Submit'}
          </button>
        </form>
      </div>
    </div>
  );
}
