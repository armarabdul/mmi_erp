import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import { DemoBanner } from './components/layout/DemoBanner';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { MobileNav } from './components/layout/MobileNav';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ReportsPage } from './pages/ReportsPage';
import { AuditPage } from './pages/AuditPage';

const MainApplication: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { t } = useLanguage();
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [mobileNavOpen, setMobileNavOpen] = useState<boolean>(false);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const getPageTitle = () => {
    switch (currentTab) {
      case 'dashboard': return t('overview');
      case 'analytics': return t('aiAnalytics');
      case 'reports': return t('reports');
      case 'audit': return t('auditLog');
      default: return t('overview');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100%' }}>
      {/* Demo Disclaimer Banner */}
      <DemoBanner />

      <div className="app-shell">
        {/* Desktop Sidebar & Mobile Drawer */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          isOpen={mobileNavOpen}
          onClose={() => setMobileNavOpen(false)}
        />

        {/* Main Content Area */}
        <div className="main-content">
          <Header
            activePageTitle={getPageTitle()}
            onToggleMobileNav={() => setMobileNavOpen(!mobileNavOpen)}
          />

          <main className="page-body">
            {currentTab === 'dashboard' && (
              <DashboardPage onNavigateToAnalytics={() => setCurrentTab('analytics')} />
            )}
            {currentTab === 'analytics' && <AnalyticsPage />}
            {currentTab === 'reports' && <ReportsPage />}
            {currentTab === 'audit' && <AuditPage />}
          </main>
        </div>
      </div>

      {/* Handheld Device Bottom Navigation */}
      <MobileNav
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <LanguageProvider>
      <AuthProvider>
        <MainApplication />
      </AuthProvider>
    </LanguageProvider>
  );
};

export default App;
