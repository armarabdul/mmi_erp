import React, { useState } from 'react';
import { 
  Globe, 
  Menu, 
  LogOut, 
  ShieldCheck, 
  Building2, 
  Check,
  ChevronDown
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';

interface HeaderProps {
  onToggleMobileNav: () => void;
  activePageTitle: string;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileNav, activePageTitle }) => {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);

  return (
    <header className="topbar">
      <div style={{ display: 'flex', alignContent: 'center', alignItems: 'center', gap: 'var(--space-3)' }}>
        <button
          className="btn btn-ghost btn-icon"
          onClick={onToggleMobileNav}
          aria-label="Toggle navigation"
          style={{ display: 'inline-flex' }}
        >
          <Menu size={20} />
        </button>
        <h1 style={{ fontSize: 'var(--font-md)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
          {activePageTitle}
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        {/* Language Switcher */}
        <div style={{ position: 'relative' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setLangMenuOpen(!langMenuOpen)}
            style={{ gap: 'var(--space-1-5)', minHeight: '34px', padding: '0 var(--space-2-5)' }}
          >
            <Globe size={14} />
            <span style={{ fontSize: 'var(--font-xs)', fontWeight: 600 }}>
              {language === 'ar' ? 'العربية' : 'English'}
            </span>
            <ChevronDown size={12} />
          </button>

          {langMenuOpen && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '4px',
                backgroundColor: 'var(--color-bg-surface)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                boxShadow: 'var(--shadow-md)',
                zIndex: 50,
                minWidth: '120px',
                overflow: 'hidden',
              }}
            >
              <button
                onClick={() => {
                  setLanguage('en');
                  setLangMenuOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: 'var(--space-2) var(--space-3)',
                  border: 'none',
                  background: language === 'en' ? 'var(--color-bg-subtle)' : 'transparent',
                  cursor: 'pointer',
                  fontSize: 'var(--font-sm)',
                  textAlign: 'left',
                }}
              >
                <span>English</span>
                {language === 'en' && <Check size={14} color="var(--color-primary)" />}
              </button>
              <button
                onClick={() => {
                  setLanguage('ar');
                  setLangMenuOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  width: '100%',
                  padding: 'var(--space-2) var(--space-3)',
                  border: 'none',
                  background: language === 'ar' ? 'var(--color-bg-subtle)' : 'transparent',
                  cursor: 'pointer',
                  fontSize: 'var(--font-sm)',
                  textAlign: 'right',
                }}
              >
                <span>العربية</span>
                {language === 'ar' && <Check size={14} color="var(--color-primary)" />}
              </button>
            </div>
          )}
        </div>

        {/* User Profile */}
        {user && (
          <div style={{ position: 'relative' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
                minHeight: '34px',
                padding: '0 var(--space-2-5)',
              }}
            >
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'var(--color-primary-light)',
                  color: 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '11px',
                  fontWeight: 700,
                }}
              >
                {user.full_name.charAt(0)}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', lineHeight: 1.1 }}>
                <span style={{ fontSize: 'var(--font-xs)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  {user.full_name.split(' ')[0]}
                </span>
                <span style={{ fontSize: '10px', color: 'var(--color-text-muted)' }}>
                  {user.role}
                </span>
              </div>
              <ChevronDown size={12} />
            </button>

            {userMenuOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: '4px',
                  backgroundColor: 'var(--color-bg-surface)',
                  border: '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: 'var(--shadow-lg)',
                  zIndex: 50,
                  width: '240px',
                  padding: 'var(--space-2)',
                }}
              >
                <div style={{ padding: 'var(--space-2)', borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <div style={{ fontWeight: 600, fontSize: 'var(--font-sm)' }}>{user.full_name}</div>
                  <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>{user.email}</div>
                  
                  <div style={{ marginTop: 'var(--space-2)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-1)' }}>
                    <span className="badge badge-primary">
                      <ShieldCheck size={10} />
                      {user.role}
                    </span>
                    {user.branch_name ? (
                      <span className="badge badge-warning">
                        <Building2 size={10} />
                        {user.branch_name}
                      </span>
                    ) : (
                      <span className="badge badge-neutral">
                        <Building2 size={10} />
                        {t('allBranches')}
                      </span>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => {
                    setUserMenuOpen(false);
                    logout();
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-2)',
                    width: '100%',
                    padding: 'var(--space-2) var(--space-2)',
                    marginTop: 'var(--space-1)',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    background: 'transparent',
                    color: 'var(--color-danger)',
                    fontSize: 'var(--font-sm)',
                    fontWeight: 500,
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-danger-bg)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <LogOut size={14} />
                  <span>{t('logout')}</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};
