import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { ChartMetadata } from '../../types';
import { useLanguage } from '../../context/LanguageContext';

interface EChartComponentProps {
  metadata: ChartMetadata;
  height?: string | number;
}

export const EChartComponent: React.FC<EChartComponentProps> = ({ metadata, height = 340 }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const { language } = useLanguage();

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, undefined, {
        renderer: 'svg',
      });
    }

    const { chart_type, title, x_axis_key, y_axis_key, data } = metadata;
    const isAr = language === 'ar';

    // Palette of enterprise colors
    const colors = ['#2563EB', '#0D9488', '#D97706', '#8B5CF6', '#EC4899', '#3B82F6', '#10B981'];

    let option: echarts.EChartsOption = {};

    if (chart_type === 'pie' || chart_type === 'donut') {
      const pieData = data.map((item, idx) => ({
        name: String(item[x_axis_key || 'name'] || `Item ${idx + 1}`),
        value: Number(item[y_axis_key || 'value'] || 0),
      }));

      option = {
        title: {
          text: title,
          left: isAr ? 'right' : 'left',
          textStyle: {
            fontSize: 14,
            fontWeight: 600,
            color: '#0F172A',
            fontFamily: isAr ? 'Cairo' : 'Inter',
          },
        },
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            const val = typeof params.value === 'number' ? params.value.toLocaleString() : params.value;
            return `<b>${params.name}</b><br/>${val} (${params.percent}%)`;
          },
        },
        legend: {
          orient: 'horizontal',
          bottom: 0,
          textStyle: {
            color: '#475569',
            fontFamily: isAr ? 'Cairo' : 'Inter',
          },
        },
        color: colors,
        series: [
          {
            name: title,
            type: 'pie',
            radius: chart_type === 'donut' ? ['45%', '70%'] : '65%',
            center: ['50%', '48%'],
            avoidLabelOverlap: true,
            itemStyle: {
              borderRadius: 4,
              borderColor: '#ffffff',
              borderWidth: 2,
            },
            label: {
              show: false,
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 12,
                fontWeight: 'bold',
              },
            },
            data: pieData,
          },
        ],
      };
    } else {
      // Bar, Line, or Area
      const categories = data.map((d, i) => String(d[x_axis_key || ''] ?? `R${i + 1}`));
      const values = data.map((d) => Number(d[y_axis_key || ''] ?? 0));

      const isLine = chart_type === 'line' || chart_type === 'area';

      option = {
        title: {
          text: title,
          left: isAr ? 'right' : 'left',
          textStyle: {
            fontSize: 14,
            fontWeight: 600,
            color: '#0F172A',
            fontFamily: isAr ? 'Cairo' : 'Inter',
          },
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
          },
          formatter: (params: any) => {
            if (!params || !params[0]) return '';
            const p = params[0];
            const formatted = typeof p.value === 'number' ? p.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : p.value;
            return `<b>${p.name}</b><br/>${p.seriesName || 'Value'}: ${formatted} OMR`;
          },
        },
        grid: {
          top: 48,
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLine: { lineStyle: { color: '#E2E8F0' } },
          axisLabel: {
            color: '#64748B',
            fontFamily: isAr ? 'Cairo' : 'Inter',
            interval: 0,
            rotate: categories.length > 6 ? 25 : 0,
            fontSize: 11,
          },
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#F1F5F9' } },
          axisLabel: {
            color: '#64748B',
            formatter: (val: number) => {
              if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
              if (val >= 1000) return `${(val / 1000).toFixed(0)}k`;
              return String(val);
            },
          },
        },
        series: [
          {
            name: title,
            type: isLine ? 'line' : 'bar',
            smooth: isLine,
            data: values,
            barMaxWidth: 38,
            itemStyle: {
              color: isLine ? '#2563EB' : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#3B82F6' },
                { offset: 1, color: '#1E40AF' },
              ]),
              borderRadius: isLine ? 0 : [4, 4, 0, 0],
            },
            areaStyle: chart_type === 'area' ? {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(59, 130, 246, 0.4)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0.02)' },
              ]),
            } : undefined,
          },
        ],
      };
    }

    chartInstance.current.setOption(option, true);

    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [metadata, language]);

  return (
    <div
      ref={chartRef}
      style={{
        width: '100%',
        height: typeof height === 'number' ? `${height}px` : height,
      }}
    />
  );
};
