import React from 'react';

interface ActionItem {
  id: string;
  label: string;
  icon: string;
  color?: string;
}

const actions: ActionItem[] = [
  { id: 'recharge', label: 'Recharge', icon: '💰' },
  { id: 'redeem', label: 'Redeem', icon: '🎟️' },
  { id: 'unbind', label: 'Unbind', icon: '📱' },
  { id: 'resetpass', label: 'Reset Pass', icon: '🔑' },
  { id: 'ban', label: 'Ban User', icon: '🚫', color: 'text-red-400' },
  { id: 'game_records', label: 'Game Logs', icon: '🎮' },
  { id: 'transaction_records', label: 'Trans Logs', icon: '📊' },
];

interface Props {
  onAction: (id: string) => void;
  disabled: boolean;
}

const ActionGrid: React.FC<Props> = ({ onAction, disabled }) => (
  <div className="grid grid-cols-3 gap-2 mt-4">
    {actions.map(action => (
      <button
        key={action.id}
        disabled={disabled}
        onClick={() => onAction(action.id)}
        className={`flex flex-col items-center justify-center py-4 bg-[#1e1e1e] rounded-xl border border-white/5 transition-all active:scale-95 ${disabled ? 'opacity-30 grayscale cursor-not-allowed' : 'hover:bg-[#252525] active:bg-[#007dce]/10'}`}
      >
        <span className="text-xl mb-1">{action.icon}</span>
        <span className={`text-[10px] font-bold uppercase tracking-tight ${action.color || 'text-gray-400'}`}>
          {action.label}
        </span>
      </button>
    ))}
  </div>
);

export default ActionGrid;
