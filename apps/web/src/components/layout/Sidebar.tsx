import React from 'react';
import { 
  LayoutDashboard, 
  Sparkles, 
  FileText, 
  History, 
  X
} from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, isOpen, onClose }) => {
  const { t } = useLanguage();
  const { user } = useAuth();

  const navItems = [
    { id: 'dashboard', label: t('overview'), icon: LayoutDashboard },
    { id: 'analytics', label: t('aiAnalytics'), icon: Sparkles, badge: 'AI' },
    { id: 'reports', label: t('reports'), icon: FileText },
    { id: 'audit', label: t('auditLog'), icon: History, adminOnly: true },
  ];

  return (
    <>
      {isOpen && <div className="drawer-backdrop" onClick={onClose} />}
      
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Brand Header */}
        <div
          style={{
            padding: 'var(--space-4) var(--space-5)',
            borderBottom: '1px solid #1E293B',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                fontWeight: 700,
                fontSize: '14px',
              }}
            >
              MMI
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#F8FAFC', letterSpacing: '-0.01em' }}>
                MMI Analytics
              </div>
              <div style={{ fontSize: '10px', color: '#94A3B8' }}>
                Intelligent ERP
              </div>
            </div>
          </div>

          <button
            className="btn btn-ghost btn-icon"
            onClick={onClose}
            style={{ color: '#94A3B8', display: 'none' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav style={{ padding: 'var(--space-3) var(--space-2)', flex: 1, display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            
            // Only Admin & Analyst see Audit Log
            if (item.adminOnly && user?.role === 'Branch Manager') {
              return null;
            }

            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectTab(item.id);
                  onClose();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-3)',
                  padding: 'var(--space-2-5) var(--space-3)',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  backgroundColor: isActive ? '#1E293B' : 'transparent',
                  color: isActive ? '#38BDF8' : '#94A3B8',
                  fontSize: 'var(--font-sm)',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  textAlign: 'inherit',
                  width: '100%',
                  transition: 'all var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = '#1E293B80';
                    e.currentTarget.style.color = '#F8FAFC';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = '#94A3B8';
                  }
                }}
              >
                <Icon size={18} color={isActive ? '#38BDF8' : '#94A3B8'} />
                <span style={{ flex: 1 }}>{item.label}</span>
                {item.badge && (
                  <span
                    style={{
                      fontSize: '10px',
                      fontWeight: 700,
                      backgroundColor: 'rgba(56, 189, 248, 0.15)',
                      color: '#38BDF8',
                      padding: '2px 6px',
                      borderRadius: 'var(--radius-sm)',
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Security / System Footer */}
        <div
          style={{
            padding: 'var(--space-3) var(--space-4)',
            borderTop: '1px solid #1E293B',
            backgroundColor: '#090D16',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: '4px' }}>
            <span className="status-dot online" />
            <span style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 500 }}>
              Read-Only SQL Replica
            </span>
          </div>
          <div style={{ fontSize: '10px', color: '#64748B' }}>
            SQL Guard &bull; RBAC Enforced
          </div>
        </div>
      </aside>
    </>
  );
};
