export interface BreadcrumbItem {
  label: string;
  path?: string;
  requireConfirm?: boolean;
}

export const ROUTES = {
  UPLOAD: '/',
  RESUME_REPORT: '/resume-report',
  ASSESSMENT: '/assessment',
} as const;

export const BREADCRUMB_ITEMS: BreadcrumbItem[] = [
  { 
    label: 'Upload',
    path: ROUTES.UPLOAD,
    requireConfirm: true 
  },
  { 
    label: 'Resume Report',
    path: ROUTES.RESUME_REPORT
  },
  { 
    label: 'Assessment Suite',
    path: ROUTES.ASSESSMENT
  }
];
