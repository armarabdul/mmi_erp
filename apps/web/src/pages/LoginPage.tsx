import React, { useState } from 'react';
import { Lock, Mail, Globe, ArrowRight, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export const LoginPage: React.FC = () => {
  const { login, quickLogin, isLoading } = useAuth();
  const { language, setLanguage, t } = useLanguage();

  const [email, setEmail] = useState('admin@mmi-demo.com');
  const [password, setPassword] = useState('Demo@12345');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    }
  };

  const handleQuickDemo = async (role: 'Admin' | 'Branch Manager' | 'Analyst') => {
    setError(null);
    try {
      await quickLogin(role);
    } catch (err: any) {
      setError(err.message || 'Demo login failed.');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#0B1120', // Enterprise deep navy background
        padding: 'var(--space-4)',
      }}
    >
      {/* Language Switcher in corner */}
      <div style={{ position: 'absolute', top: 'var(--space-4)', right: 'var(--space-4)' }}>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setLanguage(language === 'en' ? 'ar' : 'en')}
          style={{
            backgroundColor: '#1E293B',
            borderColor: '#334155',
            color: '#F8FAFC',
            gap: 'var(--space-2)',
          }}
        >
          <Globe size={14} />
          <span>{language === 'en' ? 'العربية' : 'English'}</span>
        </button>
      </div>

      <div
        style={{
          width: '100%',
          maxWidth: '440px',
          backgroundColor: '#0F172A',
          border: '1px solid #1E293B',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
          overflow: 'hidden',
        }}
      >
        {/* Card Header */}
        <div
          style={{
            padding: 'var(--space-6) var(--space-6) var(--space-4)',
            textAlign: 'center',
            borderBottom: '1px solid #1E293B',
          }}
        >
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--color-accent)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontWeight: 800,
              fontSize: '20px',
              marginBottom: 'var(--space-3)',
            }}
          >
            MMI
          </div>
          <h2 style={{ fontSize: 'var(--font-xl)', color: '#F8FAFC', marginBottom: 'var(--space-1)' }}>
            {t('loginTitle')}
          </h2>
          <p style={{ fontSize: 'var(--font-xs)', color: '#94A3B8' }}>
            {t('loginSubtitle')}
          </p>
        </div>

        {/* Form Body */}
        <div style={{ padding: 'var(--space-6)' }}>
          {error && (
            <div
              style={{
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid #EF4444',
                color: '#FCA5A5',
                padding: 'var(--space-3)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-sm)',
                marginBottom: 'var(--space-4)',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
              }}
            >
              <AlertTriangle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div className="input-group">
              <label className="input-label" style={{ color: '#E2E8F0' }}>
                {t('emailLabel')}
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type="email"
                  className="input-control"
                  style={{
                    backgroundColor: '#1E293B',
                    borderColor: '#334155',
                    color: '#F8FAFC',
                    paddingLeft: language === 'en' ? '36px' : '12px',
                    paddingRight: language === 'ar' ? '36px' : '12px',
                  }}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <Mail
                  size={16}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    left: language === 'en' ? '12px' : 'auto',
                    right: language === 'ar' ? '12px' : 'auto',
                    color: '#64748B',
                  }}
                />
              </div>
            </div>

            <div className="input-group">
              <label className="input-label" style={{ color: '#E2E8F0' }}>
                {t('passwordLabel')}
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type="password"
                  className="input-control"
                  style={{
                    backgroundColor: '#1E293B',
                    borderColor: '#334155',
                    color: '#F8FAFC',
                    paddingLeft: language === 'en' ? '36px' : '12px',
                    paddingRight: language === 'ar' ? '36px' : '12px',
                  }}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <Lock
                  size={16}
                  style={{
                    position: 'absolute',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    left: language === 'en' ? '12px' : 'auto',
                    right: language === 'ar' ? '12px' : 'auto',
                    color: '#64748B',
                  }}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={isLoading}
              style={{
                marginTop: 'var(--space-2)',
                backgroundColor: 'var(--color-accent)',
                borderColor: 'var(--color-accent)',
              }}
            >
              {isLoading ? 'Authenticating...' : t('signInBtn')}
              <ArrowRight size={16} />
            </button>
          </form>

          {/* Quick Demo Access Section (Section 6) */}
          <div style={{ marginTop: 'var(--space-6)', paddingTop: 'var(--space-4)', borderTop: '1px solid #1E293B' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>
              {t('oneClickDemo')}
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-2)' }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => handleQuickDemo('Admin')}
                disabled={isLoading}
                style={{
                  backgroundColor: '#1E293B',
                  borderColor: '#334155',
                  color: '#38BDF8',
                  flexDirection: 'column',
                  padding: '8px 4px',
                  height: 'auto',
                }}
              >
                <span style={{ fontWeight: 700, fontSize: '12px' }}>Admin</span>
                <span style={{ fontSize: '9px', color: '#94A3B8' }}>All Branches</span>
              </button>

              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => handleQuickDemo('Branch Manager')}
                disabled={isLoading}
                style={{
                  backgroundColor: '#1E293B',
                  borderColor: '#334155',
                  color: '#F59E0B',
                  flexDirection: 'column',
                  padding: '8px 4px',
                  height: 'auto',
                }}
              >
                <span style={{ fontWeight: 700, fontSize: '12px' }}>Manager</span>
                <span style={{ fontSize: '9px', color: '#94A3B8' }}>Muscat Only</span>
              </button>

              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => handleQuickDemo('Analyst')}
                disabled={isLoading}
                style={{
                  backgroundColor: '#1E293B',
                  borderColor: '#334155',
                  color: '#10B981',
                  flexDirection: 'column',
                  padding: '8px 4px',
                  height: 'auto',
                }}
              >
                <span style={{ fontWeight: 700, fontSize: '12px' }}>Analyst</span>
                <span style={{ fontSize: '9px', color: '#94A3B8' }}>Analytics</span>
              </button>
            </div>
          </div>
        </div>

        {/* Demo Disclaimer */}
        <div style={{ padding: 'var(--space-3)', backgroundColor: '#090D16', textAlign: 'center', fontSize: '11px', color: '#64748B' }}>
          Production-Ready Architecture &bull; Synthetic Demo Database
        </div>
      </div>
    </div>
  );
};
