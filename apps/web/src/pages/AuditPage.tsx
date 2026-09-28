import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  CheckCircle2, 
  XCircle, 
  Eye, 
  X
} from 'lucide-react';
import type { AuditLogItem, AuditListResponse } from '../types';
import { apiRequest } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';

export const AuditPage: React.FC = () => {
  const { t, language } = useLanguage();
  const { user } = useAuth();

  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<AuditLogItem | null>(null);

  useEffect(() => {
    loadLogs();
  }, [page, statusFilter, user]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      let url = `/audit?page=${page}&page_size=${pageSize}`;
      if (statusFilter === 'success') url += '&success=true';
      if (statusFilter === 'failed') url += '&success=false';
      if (search.trim()) url += `&search=${encodeURIComponent(search.trim())}`;

      const res = await apiRequest<AuditListResponse>(url);
      setLogs(res.items);
      setTotalCount(res.total_count);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadLogs();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Title */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
        <h2 style={{ fontSize: 'var(--font-xl)', color: 'var(--color-text-primary)' }}>
          {t('auditTitle')}
        </h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-sm)' }}>
          {t('auditSubtitle')} &bull; ({totalCount} {language === 'ar' ? 'سجل مسجل' : 'events logged'})
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div
        className="card"
        style={{
          padding: 'var(--space-3) var(--space-4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-3)',
        }}
      >
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: 'var(--space-2)', flex: 1, minWidth: '240px' }}>
          <div style={{ position: 'relative', width: '100%' }}>
            <input
              type="text"
              className="input-control"
              placeholder={t('searchPlaceholder')}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                paddingLeft: language === 'en' ? '34px' : '12px',
                paddingRight: language === 'ar' ? '34px' : '12px',
                height: '36px',
              }}
            />
            <Search
              size={15}
              style={{
                position: 'absolute',
                top: '50%',
                transform: 'translateY(-50%)',
                left: language === 'en' ? '10px' : 'auto',
                right: language === 'ar' ? '10px' : 'auto',
                color: 'var(--color-text-muted)',
              }}
            />
          </div>
          <button type="submit" className="btn btn-secondary btn-sm">
            Search
          </button>
        </form>

        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <button
            className={`btn btn-sm ${statusFilter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setStatusFilter('all'); setPage(1); }}
          >
            {t('filterAll')}
          </button>
          <button
            className={`btn btn-sm ${statusFilter === 'success' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setStatusFilter('success'); setPage(1); }}
          >
            {t('filterSuccess')}
          </button>
          <button
            className={`btn btn-sm ${statusFilter === 'failed' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setStatusFilter('failed'); setPage(1); }}
          >
            {t('filterFailed')}
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      {loading ? (
        <div className="card skeleton" style={{ height: '360px' }} />
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-container" style={{ border: 'none', maxHeight: '560px' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Audit ID</th>
                  <th>{t('status')}</th>
                  <th>{t('user')}</th>
                  <th>{t('question')}</th>
                  <th>Execution Time</th>
                  <th>Records</th>
                  <th>{t('timestamp')}</th>
                  <th style={{ textAlign: 'center' }}>{t('inspect')}</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td>
                      <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>#{log.id}</span>
                    </td>
                    <td>
                      <span className={`badge ${log.success ? 'badge-success' : 'badge-danger'}`}>
                        {log.success ? <CheckCircle2 size={11} /> : <XCircle size={11} />}
                        {log.success ? 'Success' : 'Rejected'}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-neutral">{log.user_role || 'User'}</span>
                    </td>
                    <td style={{ maxWidth: '320px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      <span title={log.user_question}>{log.user_question}</span>
                    </td>
                    <td className="num-cell">{log.execution_time_ms ? `${log.execution_time_ms} ms` : '-'}</td>
                    <td className="num-cell">{log.result_row_count ?? 0}</td>
                    <td style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => setSelectedLog(log)}
                        style={{ padding: '2px 8px' }}
                      >
                        <Eye size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={8} style={{ textAlign: 'center', padding: 'var(--space-6)', color: 'var(--color-text-muted)' }}>
                      No audit records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Inspect Modal */}
      {selectedLog && (
        <div className="drawer-backdrop" onClick={() => setSelectedLog(null)}>
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
                <History size={18} color="var(--color-accent)" />
                <h3 style={{ fontSize: 'var(--font-md)', fontWeight: 600 }}>
                  Audit Trail Detail &bull; #{selectedLog.id}
                </h3>
              </div>
              <button className="btn btn-ghost btn-icon" onClick={() => setSelectedLog(null)}>
                <X size={18} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              <div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>Question Asked</div>
                <div style={{ fontSize: 'var(--font-base)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  "{selectedLog.user_question}"
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 'var(--space-3)' }}>
                <div style={{ padding: 'var(--space-2-5)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>User Role</div>
                  <div style={{ fontWeight: 600 }}>{selectedLog.user_role}</div>
                </div>
                <div style={{ padding: 'var(--space-2-5)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>Language</div>
                  <div style={{ fontWeight: 600 }}>{selectedLog.language?.toUpperCase() || 'EN'}</div>
                </div>
                <div style={{ padding: 'var(--space-2-5)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>Execution Time</div>
                  <div style={{ fontWeight: 600 }}>{selectedLog.execution_time_ms} ms</div>
                </div>
                <div style={{ padding: 'var(--space-2-5)', backgroundColor: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>Result Rows</div>
                  <div style={{ fontWeight: 600 }}>{selectedLog.result_row_count}</div>
                </div>
              </div>

              <div>
                <div style={{ fontSize: 'var(--font-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  Validated SQL Executed on Database
                </div>
                <pre
                  style={{
                    backgroundColor: '#0F172A',
                    color: '#38BDF8',
                    padding: 'var(--space-3)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '12px',
                    fontFamily: 'Consolas, monospace',
                    whiteSpace: 'pre-wrap',
                    overflowX: 'auto',
                  }}
                >
                  {selectedLog.validated_sql || selectedLog.generated_sql || 'N/A'}
                </pre>
              </div>

              {selectedLog.error_message && (
                <div
                  style={{
                    backgroundColor: 'var(--color-danger-bg)',
                    border: '1px solid var(--color-danger-border)',
                    padding: 'var(--space-3)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--color-danger)',
                    fontSize: 'var(--font-sm)',
                  }}
                >
                  <strong>Security Error:</strong> {selectedLog.error_message}
                </div>
              )}

              {selectedLog.final_response && (
                <div>
                  <div style={{ fontSize: 'var(--font-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                    Final Response Delivered
                  </div>
                  <div
                    style={{
                      padding: 'var(--space-3)',
                      backgroundColor: 'var(--color-bg-subtle)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-sm)',
                      lineHeight: 1.5,
                    }}
                  >
                    {selectedLog.final_response}
                  </div>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'var(--space-2)' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedLog(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
