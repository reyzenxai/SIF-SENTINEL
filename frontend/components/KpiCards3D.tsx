"use client";
import React, { useRef, useState } from "react";

interface KpiCardProps {
  title: string;
  value: string | number;
  icon: string;
  colorClass: "primary" | "error" | "secondary" | "tertiary";
  badgeText: string;
  subText?: React.ReactNode;
  pulseBadge?: boolean;
}

export function KpiCard3D({ title, value, icon, colorClass, badgeText, subText, pulseBadge }: KpiCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState("");

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = ((y - centerY) / centerY) * -5;
    const rotateY = ((x - centerX) / centerX) * 5;
    
    setTransform(`translateY(-8px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`);
  };

  const handleMouseLeave = () => {
    setTransform("translateY(0) rotateX(0) rotateY(0)");
  };

  const colorMap = {
    primary: { bg: "bg-primary/10", text: "text-primary", hover: "group-hover:bg-primary/20", glow: "bg-primary/10", badgeBg: "bg-surface-container", badgeText: "text-on-surface-variant" },
    error: { bg: "bg-error/10", text: "text-error", hover: "group-hover:bg-error/20", glow: "bg-error/10", badgeBg: "bg-error", badgeText: "text-on-error" },
    secondary: { bg: "bg-secondary/10", text: "text-secondary", hover: "group-hover:bg-secondary/20", glow: "bg-secondary/10", badgeBg: "bg-surface-container", badgeText: "text-on-surface-variant" },
    tertiary: { bg: "bg-tertiary/10", text: "text-tertiary", hover: "group-hover:bg-tertiary/20", glow: "bg-tertiary/10", badgeBg: "bg-surface-container", badgeText: "text-on-surface-variant" },
  };

  const c = colorMap[colorClass];

  return (
    <div 
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative bg-surface-container/70 backdrop-blur-xl rounded-xl p-6 shadow-sm overflow-hidden group transition-all duration-300 ease-out will-change-transform transform-style-3d cursor-pointer"
      style={{ transform }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent pointer-events-none rounded-xl"></div>
      <div className="absolute -top-[1px] -left-[1px] w-full h-full border-t border-l border-white/40 pointer-events-none rounded-xl"></div>
      
      {/* Background Glow */}
      <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full blur-2xl transition-colors duration-500 ${c.glow} ${c.hover}`}></div>
      
      <div className="flex justify-between items-start mb-4 relative z-10 translate-z-10">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${c.bg}`}>
          <span className={`material-symbols-outlined text-[20px] ${c.text}`}>{icon}</span>
        </div>
        <span className={`px-2 py-1 rounded-md text-[12px] font-bold tracking-wider ${c.badgeBg} ${c.badgeText} ${pulseBadge ? 'animate-pulse' : ''}`}>
          {badgeText}
        </span>
      </div>
      
      <div className="relative z-10 translate-z-20">
        <h3 className="text-on-surface-variant text-[14px] mb-1">{title}</h3>
        <div className="flex items-end gap-3">
          <span className="text-[48px] font-bold tracking-tight text-on-surface leading-none">{value}</span>
          {subText && (
            <div className="text-[14px] mb-2">{subText}</div>
          )}
        </div>
      </div>
    </div>
  );
}
