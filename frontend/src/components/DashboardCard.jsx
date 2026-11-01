import React from 'react';

export const DashboardCard = ({ icon: Icon, title, value, description, badge, color = "blue" }) => {
  const colorMap = {
    blue: "border-blue-500/20 bg-blue-950/20 text-blue-400",
    emerald: "border-emerald-500/20 bg-emerald-950/20 text-emerald-400",
    purple: "border-purple-500/20 bg-purple-950/20 text-purple-400",
    amber: "border-amber-500/20 bg-amber-950/20 text-amber-400",
  };

  return (
    <div className="glass-card rounded-2xl p-6 relative overflow-hidden transition-all duration-300 hover:border-slate-700">
      <div className="flex items-start justify-between">
        <div className={`p-3 rounded-xl border ${colorMap[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        {badge && (
          <span className="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-medium border border-slate-700">
            {badge}
          </span>
        )}
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-medium text-slate-400">{title}</h3>
        <p className="text-2xl font-bold text-white mt-1">{value}</p>
        {description && (
          <p className="text-xs text-slate-400 mt-2 line-clamp-2">{description}</p>
        )}
      </div>
    </div>
  );
};

export default DashboardCard;
