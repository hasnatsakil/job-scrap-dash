import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  accentColor?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  title,
  value,
  subtitle,
  trend,
  trendValue,
  accentColor = 'text-blue-400',
}) => {
  const trendIcon =
    trend === 'up' ? <TrendingUp size={11} /> :
    trend === 'down' ? <TrendingDown size={11} /> :
    <Minus size={11} />;

  const trendColor =
    trend === 'up' ? 'text-green-400' :
    trend === 'down' ? 'text-red-400' :
    'text-[#71717A]';

  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-lg p-4 flex flex-col gap-3 hover:border-[#3F3F46] transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-[#71717A] uppercase tracking-wide">{title}</span>
        <div className={`${accentColor} opacity-70`}>{icon}</div>
      </div>
      <div>
        <div className="text-2xl font-semibold text-[#FAFAFA] tabular-nums leading-none">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>
        {(subtitle || trendValue) && (
          <div className="flex items-center gap-2 mt-1.5">
            {trendValue && (
              <span className={`flex items-center gap-0.5 text-xs font-medium ${trendColor}`}>
                {trendIcon}
                {trendValue}
              </span>
            )}
            {subtitle && (
              <span className="text-xs text-[#71717A]">{subtitle}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
