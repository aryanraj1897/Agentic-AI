import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

interface SidebarProps {
  activeTab?: string;
  activeAnalysesCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, activeAnalysesCount = 1 }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const getPath = (tabName: string) => {
    switch (tabName) {
      case "Dashboard":
        return "/DashboardScreen";
      case "Datasets":
        return "/UploadDatasetScreen";
      case "Analysis":
        return "/AnalysisSetupScreen";
      case "Reports":
        return "/ReportScreen";
      case "History":
        return "/HistoryScreen";
      case "Settings":
        return "/SettingsScreen";
      default:
        return "/DashboardScreen";
    }
  };

  const isActive = (tabName: string) => {
    if (activeTab) return activeTab === tabName;
    const path = location.pathname.toLowerCase();
    if (tabName === "Dashboard" && (path === "/" || path.includes("dashboard"))) return true;
    if (tabName === "Datasets" && path.includes("uploaddataset")) return true;
    if (tabName === "Analysis" && (path.includes("analysissetup") || path.includes("agentexecution") || path.includes("results"))) return true;
    if (tabName === "Reports" && path.includes("report")) return true;
    if (tabName === "History" && path.includes("history")) return true;
    if (tabName === "Settings" && path.includes("settings")) return true;
    return false;
  };

  const navItems = [
    { name: "Dashboard", icon: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/UEVfQuavYP/tqt3az2r_expires_30_days.png" },
    { name: "Datasets", icon: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/UEVfQuavYP/u7c8is72_expires_30_days.png" },
    { name: "Analysis", icon: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/UEVfQuavYP/3dvdpmws_expires_30_days.png", badge: activeAnalysesCount },
    { name: "Reports", icon: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/UEVfQuavYP/28gxm7am_expires_30_days.png" },
    { name: "History", icon: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/UEVfQuavYP/ur7ibzld_expires_30_days.png" },
    { name: "Settings", icon: "https://storage.googleapis.com/tagjs-prod.appspot.com/v1/UEVfQuavYP/y3guwjk8_expires_30_days.png" },
  ];

  return (
    <div className="flex flex-col items-start bg-[#153330] w-[232px] min-h-screen py-5 px-4 gap-[18px] shrink-0 border-r border-[#1C3B38]">
      <div 
        className="flex items-center py-1.5 px-2 gap-[11px] cursor-pointer hover:opacity-90 transition-opacity"
        onClick={() => navigate("/DashboardScreen")}
      >
        <button className="flex flex-col shrink-0 items-start bg-[#DCEAE6] text-left py-[5px] px-1.5 rounded-[7px] border-0 pointer-events-none">
          <span className="text-[#0A4542] text-[15px] font-bold">A²</span>
        </button>
        <div className="flex flex-col shrink-0 items-start gap-[1px]">
          <span className="text-white text-sm font-bold">Autonomous</span>
          <span className="text-[#9CB2AD] text-[9px] mr-[21px]">DATA ANALYSIS</span>
        </div>
      </div>

      <span className="text-[#78918C] text-[10px] font-bold uppercase tracking-wider">Workspace</span>

      <div className="flex flex-col self-stretch gap-1">
        {navItems.map((item) => {
          const active = isActive(item.name);
          return (
            <div
              key={item.name}
              onClick={() => navigate(getPath(item.name))}
              className={`flex items-center self-stretch py-3 px-3 rounded-[7px] cursor-pointer transition-colors ${
                active ? "bg-[#244B47] text-white" : "bg-[#153330] text-[#B8C7C3] hover:bg-[#1C3B38] hover:text-white"
              }`}
            >
              <img
                src={item.icon}
                alt={item.name}
                className="w-[17px] h-[17px] mr-[11px] rounded-[7px] object-fill"
              />
              <span className={`text-[13px] ${active ? "text-white font-medium" : "text-[#B8C7C3]"}`}>
                {item.name}
              </span>
              {item.badge !== undefined && item.badge > 0 && (
                <div className="flex flex-col shrink-0 items-start bg-[#B5654D] py-0.5 px-[7px] ml-auto rounded-[99px]">
                  <span className="text-white text-[9px] font-bold">{item.badge}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-auto self-stretch flex flex-col gap-4">
        <div className="flex flex-col items-start self-stretch bg-[#1C3B38] p-3 gap-2 rounded-[7px]">
          <div className="flex justify-between items-center self-stretch">
            <span className="text-[#B8C7C3] text-[11px]">Monthly analyses</span>
            <span className="text-white text-[10px] font-medium">34 / 50</span>
          </div>
          <div className="w-full bg-[#31534F] h-1.5 rounded-[99px] overflow-hidden">
            <div className="bg-[#79B8A9] w-[68%] h-full rounded-[99px]"></div>
          </div>
        </div>

        <div className="flex items-center self-stretch pt-2 px-1 gap-2.5">
          <button className="flex flex-col shrink-0 items-start bg-[#F3E3DC] text-left py-[9px] px-[7px] rounded-[99px] border-0">
            <span className="text-[#B5654D] text-[11px] font-bold">MK</span>
          </button>
          <div className="flex flex-1 flex-col items-start gap-0.5">
            <span className="text-white text-xs font-medium">Maya Kim</span>
            <span className="text-[#8FA7A2] text-[10px]">Senior analyst</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
