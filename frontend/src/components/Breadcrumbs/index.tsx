"use client";

import { useRouter, usePathname } from "next/navigation";
import { useState } from "react";
import styles from "./styles.module.css";
import { BREADCRUMB_ITEMS, ROUTES, type BreadcrumbItem } from "./config";

export default function Breadcrumbs() {
  const router = useRouter();
  const pathname = usePathname();
  const [showWarning, setShowWarning] = useState(false);
  const [warningPath, setWarningPath] = useState<string | null>(null);

  // Determine which items to show based on the current path
  const currentPath = `/${pathname.split("/")[1]}`;
  const items = BREADCRUMB_ITEMS.map((item) => ({
    ...item,
    current: item.path === currentPath,
    path: item.path === ROUTES.UPLOAD ? item.path : `${item.path}`,
  }));

  const handleNavigation = (item: BreadcrumbItem) => {
    if (!item.path) return;

    if (item.requireConfirm) {
      if (showWarning && warningPath === item.path) {
        setShowWarning(false);
        setWarningPath(null);
        router.push(item.path);
      } else {
        setShowWarning(true);
        setWarningPath(item.path);
        setTimeout(() => {
          setShowWarning(false);
          setWarningPath(null);
        }, 3000);
      }
    } else {
      router.push(item.path);
    }
  };

  return (
    <>
      <div className={styles.breadcrumbs}>
        {items.map((item, index) => (
          <div key={`${item.label}-${index}`} className={styles.breadcrumbItem}>
            {item.path && !item.current ? (
              <button
                onClick={() => handleNavigation(item)}
                className={styles.breadcrumbLink}
              >
                {item.label}
              </button>
            ) : (
              <span
                className={
                  item.current
                    ? styles.breadcrumbCurrent
                    : styles.breadcrumbInactive
                }
              >
                {item.label}
              </span>
            )}
            {index < items.length - 1 && (
              <span className={styles.breadcrumbSeparator}>/</span>
            )}
          </div>
        ))}
      </div>
      {showWarning && (
        <div className={`${styles.notification} ${styles.errorNotification}`}>
          Warning: Going back to the upload page will reset your progress. Click
          the button again to confirm.
        </div>
      )}
    </>
  );
}
