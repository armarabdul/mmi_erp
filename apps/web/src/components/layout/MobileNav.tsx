import React from 'react';
import { LayoutDashboard, Sparkles, FileText, History } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import { useAuth } from '../../context/AuthContext';

interface MobileNavProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({ currentTab, onSelectTab }) => {
  const { t } = useLanguage();
  const { user } = useAuth();

  const items = [
    { id: 'dashboard', label: t('overview'), icon: LayoutDashboard },
    { id: 'analytics', label: t('aiAnalytics'), icon: Sparkles },
    { id: 'reports', label: t('reports'), icon: FileText },
  ];

  if (user?.role !== 'Branch Manager') {
    items.push({ id: 'audit', label: t('auditLog'), icon: History });
  }

  return (
    <nav
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: 'var(--mobile-nav-height)',
        backgroundColor: 'var(--color-bg-surface)',
        borderTop: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        zIndex: 30,
        boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.05)',
      }}
      className="mobile-nav"
    >
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = currentTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '2px',
              border: 'none',
              background: 'transparent',
              color: isActive ? 'var(--color-accent)' : 'var(--color-text-muted)',
              cursor: 'pointer',
              flex: 1,
              height: '100%',
              padding: '4px',
            }}
          >
            <Icon size={20} color={isActive ? 'var(--color-accent)' : 'var(--color-text-muted)'} />
            <span style={{ fontSize: '11px', fontWeight: isActive ? 600 : 400 }}>
              {item.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
};
