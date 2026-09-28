import React, { useEffect, useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Building2, 
  Package, 
  DollarSign, 
  ShoppingCart, 
  Boxes, 
  Users, 
  Clock, 
  ShieldAlert,
  Sparkles
} from 'lucide-react';
import type { DashboardData } from '../types';
import { apiRequest } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { EChartComponent } from '../components/charts/EChartComponent';

interface DashboardPageProps {
  onNavigateToAnalytics: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigateToAnalytics }) => {
  const { t, language } = useLanguage();
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadDashboard = async () => {
      setLoading(true);
      try {
        const res = await apiRequest<DashboardData>('/dashboard');
        if (isMounted) setData(res);
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Failed to load dashboard data');
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    loadDashboard();
    return () => { isMounted = false; };
  }, [user]);

  const getKPIIcon = (id: string) => {
    switch (id) {
      case 'total_sales': return <DollarSign size={18} color="var(--color-primary)" />;
      case 'month_sales': return <TrendingUp size={18} color="var(--color-accent)" />;
      case 'purchase_value': return <ShoppingCart size={18} color="#D97706" />;
      case 'order_count':
      case 'outstanding_orders': return <Clock size={18} color="#EA580C" />;
      case 'inventory_value': return <Boxes size={18} color="#0D9488" />;
      case 'customer_count':
      case 'active_customers': return <Users size={18} color="#7C3AED" />;
      default: return <Package size={18} color="var(--color-primary)" />;
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-4)' }}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card skeleton" style={{ height: '110px' }} />
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 'var(--space-6)' }}>
          <div className="card skeleton" style={{ height: '360px' }} />
          <div className="card skeleton" style={{ height: '360px' }} />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="card" style={{ borderColor: 'var(--color-danger-border)', backgroundColor: 'var(--color-danger-bg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', color: 'var(--color-danger)' }}>
          <ShieldAlert size={20} />
          <span>{error || 'Unable to retrieve dashboard analytics.'}</span>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Scope Banner if Branch Restricted */}
      {data.is_branch_restricted && (
        <div
          style={{
            backgroundColor: '#EFF6FF',
            border: '1px solid #BFDBFE',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-3) var(--space-4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-3)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Building2 size={16} color="var(--color-accent)" />
            <span style={{ fontSize: 'var(--font-sm)', fontWeight: 600, color: '#1E40AF' }}>
              {language === 'ar'
                ? `بيانات خاصة بفرع ${data.restricted_branch_name} فقط (وفقاً لصلاحيات مدير الفرع)`
                : `Active Filter: Scoped to ${data.restricted_branch_name} Branch Only (RBAC Enforced)`}
            </span>
          </div>
          <span className="badge badge-primary">RBAC Protected</span>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: 'var(--space-4)',
        }}
      >
        {data.kpis.map((kpi) => {
          const isAr = language === 'ar';
          const title = isAr ? kpi.title_ar : kpi.title;
          const subtitle = isAr ? kpi.subtitle_ar : kpi.subtitle;

          return (
            <div key={kpi.id} className="card" style={{ padding: 'var(--space-4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
                <span style={{ fontSize: 'var(--font-xs)', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  {title}
                </span>
                <div
                  style={{
                    padding: 'var(--space-1)',
                    backgroundColor: 'var(--color-bg-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                  }}
                >
                  {getKPIIcon(kpi.id)}
                </div>
              </div>

              <div style={{ fontSize: 'var(--font-xl)', fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 'var(--space-1)' }}>
                {kpi.formatted_value}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 'var(--font-xs)' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>{subtitle}</span>
                {kpi.trend === 'up' && (
                  <span className="badge badge-success">
                    <TrendingUp size={11} /> +{kpi.change_pct}%
                  </span>
                )}
                {kpi.trend === 'down' && (
                  <span className="badge badge-danger">
                    <TrendingDown size={11} /> {kpi.change_pct}%
                  </span>
                )}
                {kpi.trend === 'neutral' && (
                  <span className="badge badge-neutral">
                    <Minus size={11} /> Active
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
          gap: 'var(--space-6)',
        }}
      >
        {/* Sales Trend */}
        <div className="card">
          <EChartComponent
            height={320}
            metadata={{
              chart_type: 'area',
              title: t('salesTrendTitle'),
              x_axis_key: 'period',
              y_axis_key: 'sales',
              data: data.sales_trend,
            }}
          />
        </div>

        {/* Sales by Branch */}
        <div className="card">
          <EChartComponent
            height={320}
            metadata={{
              chart_type: 'bar',
              title: t('salesByBranchTitle'),
              x_axis_key: 'branch_name',
              y_axis_key: 'sales',
              data: data.sales_by_branch,
            }}
          />
        </div>
      </div>

      {/* Lower Section: Top Products & Recent Analytics */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
          gap: 'var(--space-6)',
        }}
      >
        {/* Top Products Table */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">{t('topProductsTitle')}</h3>
          </div>
          <div className="table-container" style={{ maxHeight: '340px' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th className="num-cell">Units</th>
                  <th className="num-cell">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {data.top_products.map((p) => (
                  <tr key={p.product_id}>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{p.product_name}</div>
                      <div style={{ fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>{p.sku}</div>
                    </td>
                    <td>
                      <span className="badge badge-neutral">{p.category_name}</span>
                    </td>
                    <td className="num-cell">{p.units_sold.toLocaleString()}</td>
                    <td className="num-cell" style={{ fontWeight: 600, color: 'var(--color-primary)' }}>
                      {p.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} OMR
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">{t('recentActivityTitle')}</h3>
            <button className="btn btn-outline btn-sm" onClick={onNavigateToAnalytics}>
              <Sparkles size={14} />
              <span>{t('aiAnalytics')}</span>
            </button>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {data.recent_activity.map((item) => (
              <div
                key={item.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: 'var(--space-3)',
                  backgroundColor: 'var(--color-bg-subtle)',
                  borderRadius: 'var(--radius-md)',
                  gap: 'var(--space-3)',
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', minWidth: 0 }}>
                  <span style={{ fontSize: 'var(--font-sm)', fontWeight: 600, color: 'var(--color-text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    "{item.question}"
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--font-xs)', color: 'var(--color-text-muted)' }}>
                    <span>{item.user_role}</span>
                    <span>&bull;</span>
                    <span>{item.timestamp}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                  <span className="badge badge-neutral">{item.chart_type}</span>
                  <span className={`badge ${item.success ? 'badge-success' : 'badge-danger'}`}>
                    {item.success ? 'Verified' : 'Error'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
