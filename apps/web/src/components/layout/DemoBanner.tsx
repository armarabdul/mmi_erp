import React from 'react';
import { AlertCircle } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export const DemoBanner: React.FC = () => {
  const { t } = useLanguage();
  return (
    <div className="demo-banner">
      <AlertCircle size={14} />
      <span>{t('demoBanner')}</span>
    </div>
  );
};
