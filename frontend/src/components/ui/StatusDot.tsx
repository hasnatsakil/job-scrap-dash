import React from 'react';

type StatusType = 'green' | 'yellow' | 'red' | 'gray';

interface StatusDotProps {
  status: StatusType;
  pulse?: boolean;
  label?: string;
  size?: 'sm' | 'md';
}

const colorMap: Record<StatusType, { dot: string; glow: string; text: string }> = {
  green: { dot: 'bg-green-500', glow: 'shadow-[0_0_6px_1px_rgba(34,197,94,0.4)]', text: 'text-green-400' },
  yellow: { dot: 'bg-yellow-500', glow: 'shadow-[0_0_6px_1px_rgba(234,179,8,0.4)]', text: 'text-yellow-400' },
  red: { dot: 'bg-red-500', glow: 'shadow-[0_0_6px_1px_rgba(239,68,68,0.4)]', text: 'text-red-400' },
  gray: { dot: 'bg-zinc-600', glow: '', text: 'text-zinc-500' },
};

const StatusDot: React.FC<StatusDotProps> = ({ status, pulse = false, label, size = 'sm' }) => {
  const colors = colorMap[status];
  const dotSize = size === 'sm' ? 'w-2 h-2' : 'w-2.5 h-2.5';

  return (
    <div className="flex items-center gap-2">
      <div className={`${dotSize} rounded-full shrink-0 ${colors.dot} ${colors.glow} ${pulse ? 'animate-pulse' : ''}`} />
      {label && <span className={`text-xs font-medium ${colors.text}`}>{label}</span>}
    </div>
  );
};

export default StatusDot;
