import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'en' | 'ar';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  dir: 'ltr' | 'rtl';
  t: (key: string) => string;
}

const translations: Record<string, Record<Language, string>> = {
  // Brand & Navigation
  appTitle: { en: 'MMI AI Analytics', ar: 'إم إم آي للتحليلات الذكية' },
  appSubtitle: { en: 'Intelligent ERP Analytics & Reporting', ar: 'تحليلات ذكية وتقارير تخطيط موارد المؤسسات' },
  overview: { en: 'Overview', ar: 'نظرة عامة' },
  aiAnalytics: { en: 'AI Analytics', ar: 'التحليلات الذكية' },
  reports: { en: 'Reports', ar: 'التقارير' },
  savedQueries: { en: 'Saved Queries', ar: 'الاستعلامات المحفوظة' },
  auditLog: { en: 'Audit Log', ar: 'سجل التدقيق' },
  settings: { en: 'Settings', ar: 'الإعدادات' },
  logout: { en: 'Logout', ar: 'تسجيل الخروج' },

  // Demo Banner
  demoBanner: { 
    en: 'DEMO ENVIRONMENT — Connected to Synthetic ERP Analytics Dataset. Real SQL Server bridge ready.', 
    ar: 'بيئة تجريبية — متصلة بنموذج بيانات تخطيط الموارد المحاكاة. جاهزة للربط مع مخدّم SQL Server.' 
  },

  // Auth & Roles
  adminRole: { en: 'Administrator', ar: 'مسؤول النظام' },
  managerRole: { en: 'Branch Manager', ar: 'مدير فرع' },
  analystRole: { en: 'Senior Analyst', ar: 'محلل أعمال' },
  allBranches: { en: 'All Branches (Company-Wide)', ar: 'كافة الفروع (مستوى الشركة)' },
  branchRestricted: { en: 'Assigned Branch Only', ar: 'الفرع المخصص فقط' },
  loginTitle: { en: 'Sign in to MMI Analytics', ar: 'تسجيل الدخول إلى تحليلات إم إم آي' },
  loginSubtitle: { en: 'Enterprise ERP Intelligence & Executive Reporting', ar: 'ذكاء الأعمال والتقارير التنفيذية للمؤسسة' },
  emailLabel: { en: 'Corporate Email', ar: 'البريد الإلكتروني المهني' },
  passwordLabel: { en: 'Password', ar: 'كلمة المرور' },
  signInBtn: { en: 'Sign In to Portal', ar: 'تسجيل الدخول إلى البوابة' },
  oneClickDemo: { en: 'Quick Demo Access', ar: 'وصول تجريبي فوري' },

  // Dashboard
  dashboardTitle: { en: 'Enterprise Executive Dashboard', ar: 'لوحة المؤشرات التنفيذية' },
  dashboardSubtitle: { en: 'Consolidated performance KPIs across operations', ar: 'مؤشرات الأداء المجمعة لكافة العمليات' },
  salesTrendTitle: { en: 'Monthly Sales Revenue Trend', ar: 'اتجاه إيرادات المبيعات الشهرية' },
  salesByBranchTitle: { en: 'Sales Distribution by Branch', ar: 'توزيع المبيعات حسب الفرع' },
  topProductsTitle: { en: 'Top 10 Performing Products', ar: 'أفضل 10 منتجات من حيث الإيرادات' },
  recentActivityTitle: { en: 'Recent Analytics Inquiries', ar: 'أحدث الاستفسارات التحليلية' },
  viewAll: { en: 'View All', ar: 'عرض الكل' },

  // AI Analytics
  askQuestionPlaceholder: { en: 'Ask a question about your business data...', ar: 'اطرح سؤالاً حول بيانات أعمالك...' },
  askBtn: { en: 'Analyze', ar: 'تحليل' },
  clearChat: { en: 'Clear History', ar: 'مسح السجل' },
  suggestionsTitle: { en: 'Suggested Questions:', ar: 'أسئلة مقترحة:' },
  understandingRequest: { en: 'Understanding request...', ar: 'جاري فهم وتحليل الطلب...' },
  checkingPermissions: { en: 'Checking role permissions...', ar: 'التحقق من صلاحيات المستخدم...' },
  preparingQuery: { en: 'Preparing analytics query...', ar: 'إعداد استعلام تحليلات الأعمال...' },
  validatingSecurity: { en: 'Validating query via SQL Guard...', ar: 'فحص الأمان عبر جدار حماية SQL...' },
  executingAnalysis: { en: 'Executing read-only database analysis...', ar: 'تنفيذ التحليل على قاعدة البيانات للقراءة فقط...' },
  preparingResults: { en: 'Preparing visualizations & business explanation...', ar: 'تجهيز الرسوم البيانية والشرح الإداري...' },
  queryDetails: { en: 'Technical Details', ar: 'التفاصيل التقنية' },
  dataSource: { en: 'Data Source', ar: 'مصدر البيانات' },
  executionTime: { en: 'Execution Time', ar: 'وقت التنفيذ' },
  rowCount: { en: 'Records', ar: 'عدد السجلات' },
  sqlQuery: { en: 'Validated SQL Query', ar: 'استعلام SQL المعتمد' },
  modelUsed: { en: 'AI Model', ar: 'نموذج الذكاء الاصطناعي' },

  // Reports
  reportsTitle: { en: 'Business Reports & Operational Summaries', ar: 'تقارير الأعمال والملخصات التشغيلية' },
  reportsSubtitle: { en: 'Export verified transaction and inventory datasets', ar: 'تصدير مجموعات بيانات المعاملات والمخزون المعتمدة' },
  previewReport: { en: 'Preview Report', ar: 'معاينة التقرير' },
  exportExcel: { en: 'Export Excel (.xlsx)', ar: 'تصدير إكسل (.xlsx)' },
  exportPdf: { en: 'Export PDF (.pdf)', ar: 'تصدير PDF (.pdf)' },
  exportCsv: { en: 'Export CSV', ar: 'تصدير CSV' },
  exportWord: { en: 'Export Word (.docx)', ar: 'تصدير وورد (.docx)' },
  exporting: { en: 'Generating file...', ar: 'جاري تجهيز الملف...' },

  // Audit
  auditTitle: { en: 'Security & Analytics Audit Trail', ar: 'سجل تدقيق الأمان والتحليلات' },
  auditSubtitle: { en: 'Comprehensive chronological log of user questions, generated SQL, and security validations', ar: 'سجل زمني شامل لأسئلة المستخدمين، واستعلامات SQL المولدة وفحوصات الأمان' },
  searchPlaceholder: { en: 'Search questions or logs...', ar: 'بحث في الأسئلة أو السجلات...' },
  filterAll: { en: 'All Statuses', ar: 'كافة الحالات' },
  filterSuccess: { en: 'Success Only', ar: 'الناجحة فقط' },
  filterFailed: { en: 'Rejected / Errors', ar: 'المرفوضة / الأخطاء' },
  status: { en: 'Status', ar: 'الحالة' },
  user: { en: 'User / Role', ar: 'المستخدم / الصلاحية' },
  question: { en: 'Question Asked', ar: 'السؤال المطروح' },
  timestamp: { en: 'Timestamp', ar: 'الوقت والتاريخ' },
  inspect: { en: 'Inspect', ar: 'معاينة' },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem('mmi_lang') as Language) || 'en';
  });

  const dir = language === 'ar' ? 'rtl' : 'ltr';

  useEffect(() => {
    localStorage.setItem('mmi_lang', language);
    document.documentElement.lang = language;
    document.documentElement.dir = dir;
  }, [language, dir]);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
  };

  const t = (key: string): string => {
    return translations[key]?.[language] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, dir, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider');
  return ctx;
};
