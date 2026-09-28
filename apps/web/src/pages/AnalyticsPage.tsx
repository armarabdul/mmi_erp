import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  Code, 
  ShieldCheck, 
  RefreshCw, 
  X,
  Calendar
} from 'lucide-react';
import type { AnalyticsQueryResponse } from '../types';
import { apiRequest } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { EChartComponent } from '../components/charts/EChartComponent';

interface ProcessingStage {
  id: string;
  label: string;
  label_ar: string;
}

const STAGES: ProcessingStage[] = [
  { id: '1', label: 'Understanding request intent...', label_ar: 'فهم قصد الاستعلام...' },
  { id: '2', label: 'Verifying user permissions & RBAC scope...', label_ar: 'التحقق من الصلاحيات ونطاق الفرع...' },
  { id: '3', label: 'Retrieving semantic metrics & schema...', label_ar: 'استرجاع المقاييس والطبقة الدلالية...' },
  { id: '4', label: 'Validating generated SQL via Security Guard...', label_ar: 'فحص استعلام SQL عبر جدار الحماية...' },
  { id: '5', label: 'Executing read-only analytical query...', label_ar: 'تنفيذ الاستعلام على قاعدة البيانات...' },
  { id: '6', label: 'Assembling visualization & executive summary...', label_ar: 'تجهيز الرسوم البيانية والملخص التنفيذي...' },
];

export const AnalyticsPage: React.FC = () => {
  const { t, language } = useLanguage();
  
  const [question, setQuestion] = useState('');
  const [results, setResults] = useState<AnalyticsQueryResponse[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [selectedResultForModal, setSelectedResultForModal] = useState<AnalyticsQueryResponse | null>(null);

  const englishSuggestions = [
    'Show me sales by branch this month',
    'Show me the top 10 products by sales',
    'Show me monthly sales for the last 12 months',
    'What is the total sales value this month?',
    'Which branch has the highest sales?',
  ];

  const arabicSuggestions = [
    'ما هي المبيعات حسب الفرع هذا الشهر؟',
    'أفضل 10 منتجات مبيعا',
    'المبيعات الشهرية لآخر 12 شهرا',
    'ما إجمالي المبيعات هذا الشهر؟',
    'أي فرع لديه أعلى مبيعات؟',
  ];

  const suggestions = language === 'ar' ? arabicSuggestions : englishSuggestions;

  const handleQuery = async (queryText: string) => {
    if (!queryText.trim() || isProcessing) return;

    setIsProcessing(true);
    setCurrentStageIndex(0);

    // Simulate real high-level workflow stage progression
    const stageTimer = setInterval(() => {
      setCurrentStageIndex((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 280);

    try {
      const response = await apiRequest<AnalyticsQueryResponse>('/analytics/query', {
        method: 'POST',
        body: JSON.stringify({
          question: queryText.trim(),
          language: language,
        }),
      });

      clearInterval(stageTimer);
      setResults((prev) => [response, ...prev]);
      setQuestion('');
    } catch (err: any) {
      clearInterval(stageTimer);
      // Create safe error result
      const errorResult: AnalyticsQueryResponse = {
        question: queryText.trim(),
        language: language,
        success: false,
        explanation: language === 'ar' 
          ? `تعذر استكمال الاستعلام: ${err.message}` 
          : `Analytics query failed: ${err.message}`,
        visualization: {
          chart_type: 'table',
          title: language === 'ar' ? 'فشل الاستعلام' : 'Query Failed',
          data: [],
        },
        table_columns: [],
        table_data: [],
        filters_applied: {},
        data_source: 'Demo ERP Analytics Database',
        technical_details: {
          audit_id: 0,
          execution_time_ms: 0,
          result_row_count: 0,
          validated_sql: '',
          model_used: 'N/A',
          ai_provider: 'N/A',
          branch_restricted: false,
        },
        error_message: err.message,
      };
      setResults((prev) => [errorResult, ...prev]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleQuery(question);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Top Description */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
        <h2 style={{ fontSize: 'var(--font-xl)', color: 'var(--color-text-primary)' }}>
          {t('aiAnalytics')}
        </h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-sm)' }}>
          {language === 'ar'
            ? 'اطرح أسئلة باللغة الطبيعية عن مبيعاتك، مخزونك، وأداء الفروع للحصول على تحليلات دقيقة معتمدة.'
            : 'Ask questions about your enterprise ERP data in plain English or Arabic to generate validated charts and insights.'}
        </p>
      </div>

      {/* Interactive Input Box */}
      <div className="card" style={{ padding: 'var(--space-4)', boxShadow: 'var(--shadow-md)' }}>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input
              type="text"
              className="input-control"
              placeholder={t('askQuestionPlaceholder')}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={isProcessing}
              style={{
                fontSize: 'var(--font-base)',
                paddingLeft: language === 'en' ? '42px' : '16px',
                paddingRight: language === 'ar' ? '42px' : '16px',
                minHeight: '48px',
              }}
            />
            <Sparkles
              size={18}
              style={{
                position: 'absolute',
                left: language === 'en' ? '14px' : 'auto',
                right: language === 'ar' ? '14px' : 'auto',
                color: 'var(--color-accent)',
              }}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isProcessing || !question.trim()}
              style={{
                position: 'absolute',
                right: language === 'en' ? '6px' : 'auto',
                left: language === 'ar' ? '6px' : 'auto',
                minHeight: '36px',
                padding: '0 var(--space-4)',
              }}
            >
              {isProcessing ? <RefreshCw size={14} className="spin" /> : <Send size={14} />}
              <span>{t('askBtn')}</span>
            </button>
          </div>

          {/* Quick Suggestions Chips */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1-5)' }}>
            <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
              {t('suggestionsTitle')}
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuestion(s);
                    handleQuery(s);
                  }}
                  disabled={isProcessing}
                  style={{
                    backgroundColor: 'var(--color-bg-subtle)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-full)',
                    padding: '4px 12px',
                    fontSize: 'var(--font-xs)',
                    color: 'var(--color-text-secondary)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)',
                    whiteSpace: 'nowrap',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--color-primary-light)';
                    e.currentTarget.style.borderColor = 'var(--color-accent)';
                    e.currentTarget.style.color = 'var(--color-primary)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--color-bg-subtle)';
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                    e.currentTarget.style.color = 'var(--color-text-secondary)';
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>

      {/* Multi-stage High-Level Processing Banner */}
      {isProcessing && (
        <div
          className="card"
          style={{
            backgroundColor: '#F0F9FF',
            borderColor: '#BAE6FD',
            padding: 'var(--space-4)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-3)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <RefreshCw size={16} className="spin" color="var(--color-accent)" />
            <span style={{ fontSize: 'var(--font-sm)', fontWeight: 600, color: '#0369A1' }}>
              {language === 'ar' ? STAGES[currentStageIndex].label_ar : STAGES[currentStageIndex].label}
            </span>
          </div>

          {/* Progress dots */}
          <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
            {STAGES.map((s, idx) => (
              <div
                key={s.id}
                style={{
                  flex: 1,
                  height: '4px',
                  borderRadius: '2px',
                  backgroundColor: idx <= currentStageIndex ? 'var(--color-accent)' : '#E2E8F0',
                  transition: 'background-color 200ms ease',
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Analytics Results List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        {results.map((res, resIdx) => (
          <div
            key={resIdx}
            className="card"
            style={{
              padding: 'var(--space-5)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)',
              borderLeft: res.success ? '4px solid var(--color-primary)' : '4px solid var(--color-danger)',
            }}
          >
            {/* Header: User Question + Status Badge */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--space-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'var(--color-primary-light)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Sparkles size={14} color="var(--color-primary)" />
                </div>
                <div>
                  <div style={{ fontSize: 'var(--font-md)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    "{res.question}"
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    {res.data_source} &bull; {res.technical_details.execution_time_ms}ms
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                {res.technical_details.branch_restricted && (
                  <span className="badge badge-warning">
                    <ShieldCheck size={11} /> Branch Scoped
                  </span>
                )}
                <span className={`badge ${res.success ? 'badge-success' : 'badge-danger'}`}>
                  {res.success ? 'Validated' : 'Security Alert'}
                </span>
              </div>
            </div>

            {/* Applied Date Filter & Applied Branch Permissions (Phase 3 Requirement) */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', fontSize: 'var(--font-xs)' }}>
              {res.filters_applied && Object.keys(res.filters_applied).length > 0 && (
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', backgroundColor: 'var(--color-bg-subtle)', padding: '2px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
                  <Calendar size={12} color="var(--color-text-muted)" />
                  <span style={{ color: 'var(--color-text-muted)' }}>{language === 'ar' ? 'الفترة المطبقة:' : 'Applied Date Filter:'}</span>
                  <span style={{ fontWeight: 600 }}>{JSON.stringify(res.filters_applied).replace(/["{}]/g, '').replace(':', ': ')}</span>
                </div>
              )}
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', backgroundColor: 'var(--color-bg-subtle)', padding: '2px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
                <ShieldCheck size={12} color={res.technical_details.branch_restricted ? 'var(--color-accent)' : 'var(--color-text-muted)'} />
                <span style={{ color: 'var(--color-text-muted)' }}>{language === 'ar' ? 'نطاق الصلاحيات:' : 'Branch Permission:'}</span>
                <span style={{ fontWeight: 600 }}>
                  {res.technical_details.branch_restricted 
                    ? (language === 'ar' ? 'مقيد للفرع المخصص فقط' : 'Restricted (Assigned Branch Only)')
                    : (language === 'ar' ? 'شامل لكافة الفروع' : 'Global (All Branches)')}
                </span>
              </div>
            </div>

            {/* Business Explanation */}
            <div
              style={{
                backgroundColor: res.success ? 'var(--color-bg-subtle)' : 'var(--color-danger-bg)',
                border: `1px solid ${res.success ? 'var(--color-border)' : 'var(--color-danger-border)'}`,
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-3) var(--space-4)',
                fontSize: 'var(--font-sm)',
                color: res.success ? 'var(--color-text-primary)' : 'var(--color-danger)',
                lineHeight: 1.5,
              }}
            >
              <strong>{language === 'ar' ? 'الملخص التنفيذي: ' : 'Executive Summary: '}</strong>
              {res.explanation}
            </div>

            {/* Visualization (if success and data available) */}
            {res.success && res.visualization.data && res.visualization.data.length > 0 && (
              <div style={{ marginTop: 'var(--space-2)' }}>
                <EChartComponent
                  height={320}
                  metadata={res.visualization}
                />
              </div>
            )}

            {/* Data Table */}
            {res.success && res.table_data && res.table_data.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 'var(--font-xs)', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                    {language === 'ar' ? 'جدول البيانات التحليلية' : 'Underlying Query Records'} ({res.table_data.length} rows)
                  </span>
                </div>
                <div className="table-container" style={{ maxHeight: '240px' }}>
                  <table className="table">
                    <thead>
                      <tr>
                        {res.table_columns.map((col) => (
                          <th key={col}>{col.replace('_', ' ').toUpperCase()}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {res.table_data.slice(0, 15).map((row, rIdx) => (
                        <tr key={rIdx}>
                          {res.table_columns.map((col) => {
                            const val = row[col];
                            const isNumeric = typeof val === 'number';
                            return (
                              <td key={col} className={isNumeric ? 'num-cell' : ''}>
                                {isNumeric ? val.toLocaleString() : String(val)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Footer with Technical Inspection Modal Button */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: 'var(--space-3)',
                borderTop: '1px solid var(--color-border)',
                fontSize: 'var(--font-xs)',
                color: 'var(--color-text-muted)',
              }}
            >
              <div>
                Audit Ref: <strong>#{res.technical_details.audit_id || 'DEMO'}</strong>
              </div>

              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => setSelectedResultForModal(res)}
                style={{ gap: 'var(--space-1-5)' }}
              >
                <Code size={13} />
                <span>{t('queryDetails')}</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Technical Details Inspection Modal (Section 19) */}
      {selectedResultForModal && (
        <div className="drawer-backdrop" onClick={() => setSelectedResultForModal(null)}>
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              backgroundColor: 'var(--color-bg-surface)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border)',
              boxShadow: 'var(--shadow-lg)',
              width: '90%',
              maxWidth: '680px',
              maxHeight: '85vh',
              overflowY: 'auto',
              padding: 'var(--space-6)',
              zIndex: 60,
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-4)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <ShieldCheck size={18} color="var(--color-accent)" />
                <h3 style={{ fontSize: 'var(--font-md)', fontWeight: 600 }}>
                  {language === 'ar' ? 'التفاصيل التقنية والأمان' : 'Technical & Security Inspection'}
                </h3>
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => setSelectedResultForModal(null)}>
                <X size={18} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--space-3)' }}>
              <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Audit Entry ID</div>
                <div style={{ fontSize: 'var(--font-base)', fontWeight: 700 }}>#{selectedResultForModal.technical_details.audit_id}</div>
              </div>
              <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Database Execution Time</div>
                <div style={{ fontSize: 'var(--font-base)', fontWeight: 700 }}>{selectedResultForModal.technical_details.execution_time_ms} ms</div>
              </div>
              <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>AI Provider / Model</div>
                <div style={{ fontSize: 'var(--font-base)', fontWeight: 700 }}>{selectedResultForModal.technical_details.ai_provider} ({selectedResultForModal.technical_details.model_used})</div>
              </div>
              <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Branch Authorization Scope</div>
                <div style={{ fontSize: 'var(--font-base)', fontWeight: 700, color: selectedResultForModal.technical_details.branch_restricted ? 'var(--color-warning)' : 'var(--color-success)' }}>
                  {selectedResultForModal.technical_details.branch_restricted ? 'Restricted to User Branch' : 'Company-Wide Access'}
                </div>
              </div>
            </div>

            <div>
              <div style={{ fontSize: 'var(--font-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 'var(--space-1)' }}>
                {t('sqlQuery')}
              </div>
              <pre
                style={{
                  backgroundColor: '#0F172A',
                  color: '#38BDF8',
                  padding: 'var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '12px',
                  overflowX: 'auto',
                  fontFamily: 'Consolas, monospace',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {selectedResultForModal.technical_details.validated_sql || 'Query generated via safe KPI semantic layer.'}
              </pre>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'var(--space-2)' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedResultForModal(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
