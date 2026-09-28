import React, { useState, useEffect } from 'react';
import { 
  FileSpreadsheet, 
  FileText, 
  FileCode, 
  RefreshCw, 
  CheckCircle2
} from 'lucide-react';
import type { ReportDefinition, ReportPreviewResponse } from '../types';
import { apiRequest, downloadReportFile } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';

export const ReportsPage: React.FC = () => {
  const { t, language } = useLanguage();
  const { user } = useAuth();

  const [catalog, setCatalog] = useState<ReportDefinition[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string>('sales-summary');
  const [previewData, setPreviewData] = useState<ReportPreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [exportingFormat, setExportingFormat] = useState<string | null>(null);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  useEffect(() => {
    const loadCatalog = async () => {
      try {
        const cat = await apiRequest<ReportDefinition[]>('/reports');
        setCatalog(cat);
        if (cat.length > 0) {
          loadPreview(cat[0].id);
        }
      } catch (err) {
        console.error('Failed to load reports catalog:', err);
      }
    };
    loadCatalog();
  }, [user]);

  const loadPreview = async (reportId: string) => {
    setSelectedReportId(reportId);
    setLoading(true);
    setExportNotice(null);
    try {
      const data = await apiRequest<ReportPreviewResponse>(`/reports/${reportId}/preview?limit=50`);
      setPreviewData(data);
    } catch (err: any) {
      console.error('Failed to preview report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'xlsx' | 'pdf' | 'docx' | 'csv') => {
    if (!selectedReportId || exportingFormat) return;
    setExportingFormat(format);
    setExportNotice(null);
    try {
      await downloadReportFile(selectedReportId, format, language);
      setExportNotice(language === 'ar' ? 'تم تنزيل الملف بنجاح.' : 'File exported and downloaded successfully.');
    } catch (err: any) {
      setExportNotice(language === 'ar' ? 'فشل تصدير التقرير.' : 'Export failed. Please try again.');
    } finally {
      setExportingFormat(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Title */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
        <h2 style={{ fontSize: 'var(--font-xl)', color: 'var(--color-text-primary)' }}>
          {t('reportsTitle')}
        </h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-sm)' }}>
          {t('reportsSubtitle')}
        </p>
      </div>

      {/* Catalog Selector Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: 'var(--space-4)',
        }}
      >
        {catalog.map((r) => {
          const isSelected = selectedReportId === r.id;
          const name = language === 'ar' ? r.name_ar : r.name;
          const desc = language === 'ar' ? r.description_ar : r.description;

          return (
            <div
              key={r.id}
              className="card"
              onClick={() => loadPreview(r.id)}
              style={{
                cursor: 'pointer',
                borderColor: isSelected ? 'var(--color-primary)' : 'var(--color-border)',
                backgroundColor: isSelected ? 'var(--color-primary-light)' : 'var(--color-bg-surface)',
                transition: 'all var(--transition-fast)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
                <span className="badge badge-neutral">{r.category}</span>
                {isSelected && <span className="badge badge-primary">Active</span>}
              </div>
              <h3 style={{ fontSize: 'var(--font-base)', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 'var(--space-1)' }}>
                {name}
              </h3>
              <p style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
                {desc}
              </p>
            </div>
          );
        })}
      </div>

      {/* Action / Export Toolbar */}
      {previewData && (
        <div
          className="card"
          style={{
            padding: 'var(--space-4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 'var(--space-3)',
          }}
        >
          <div>
            <h3 style={{ fontSize: 'var(--font-md)', fontWeight: 600 }}>
              {language === 'ar' ? previewData.title_ar : previewData.title}
            </h3>
            <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
              Generated: {previewData.generated_at} &bull; {previewData.total_count} records displayed
            </div>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            <button
              className="btn btn-primary btn-sm"
              onClick={() => handleExport('xlsx')}
              disabled={!!exportingFormat}
            >
              {exportingFormat === 'xlsx' ? <RefreshCw size={14} className="spin" /> : <FileSpreadsheet size={14} />}
              <span>{t('exportExcel')}</span>
            </button>

            <button
              className="btn btn-secondary btn-sm"
              onClick={() => handleExport('pdf')}
              disabled={!!exportingFormat}
            >
              {exportingFormat === 'pdf' ? <RefreshCw size={14} className="spin" /> : <FileText size={14} />}
              <span>{t('exportPdf')}</span>
            </button>

            <button
              className="btn btn-secondary btn-sm"
              onClick={() => handleExport('docx')}
              disabled={!!exportingFormat}
            >
              {exportingFormat === 'docx' ? <RefreshCw size={14} className="spin" /> : <FileText size={14} />}
              <span>{t('exportWord')}</span>
            </button>

            <button
              className="btn btn-outline btn-sm"
              onClick={() => handleExport('csv')}
              disabled={!!exportingFormat}
            >
              {exportingFormat === 'csv' ? <RefreshCw size={14} className="spin" /> : <FileCode size={14} />}
              <span>{t('exportCsv')}</span>
            </button>
          </div>
        </div>
      )}

      {/* Export feedback toast */}
      {exportNotice && (
        <div
          style={{
            padding: 'var(--space-3)',
            backgroundColor: 'var(--color-success-bg)',
            border: '1px solid var(--color-success-border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-success)',
            fontSize: 'var(--font-sm)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
          }}
        >
          <CheckCircle2 size={16} />
          <span>{exportNotice}</span>
        </div>
      )}

      {/* Preview Table */}
      {loading ? (
        <div className="card skeleton" style={{ height: '320px' }} />
      ) : previewData ? (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none', maxHeight: '520px' }}>
            <table className="table">
              <thead>
                <tr>
                  {previewData.columns.map((c) => (
                    <th key={c}>
                      {language === 'ar' ? previewData.column_headers_ar[c] : previewData.column_headers[c]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewData.data.map((row, rIdx) => (
                  <tr key={rIdx}>
                    {previewData.columns.map((c) => {
                      const val = row[c];
                      const isNum = typeof val === 'number';
                      return (
                        <td key={c} className={isNum ? 'num-cell' : ''}>
                          {isNum ? val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : String(val)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
};
