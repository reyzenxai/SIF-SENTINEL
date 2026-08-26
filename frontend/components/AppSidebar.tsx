import Link from "next/link";
import { usePathname } from "next/navigation";

export function AppSidebar() {
  const pathname = usePathname();

  const links = [
    { name: "Dashboard", href: "/dashboard", icon: "dashboard" },
    { name: "Risk Mapping", href: "#", icon: "map" },
    { name: "AI Analytics", href: "#", icon: "psychology" },
    { name: "Incident Reports", href: "/reports", icon: "description" },
    { name: "Safety Controls", href: "#", icon: "emergency_home" },
  ];

  return (
    <aside className="fixed left-0 top-0 h-full w-72 bg-surface-container-lowest z-50 flex flex-col shadow-[1px_0_10px_rgba(0,0,0,0.02)]">
      <div className="px-container-margin py-stack-md flex items-center gap-3">
        <span className="material-symbols-outlined text-primary text-3xl">shield</span>
        <span className="font-title-lg text-[18px] font-semibold text-primary tracking-tight">SIF Sentinel</span>
      </div>
      <nav className="flex-1 px-4 mt-stack-md space-y-1">
        {links.map((link) => {
          const isActive = pathname === link.href || (pathname?.startsWith(link.href) && link.href !== "#" && link.href !== "/");
          return (
            <Link
              key={link.name}
              href={link.href}
              className={`flex items-center px-4 py-3 rounded-xl transition-all group ${
                isActive
                  ? "bg-primary-container text-on-primary-container font-semibold"
                  : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface"
              }`}
            >
              <span className="material-symbols-outlined mr-3">{link.icon}</span>
              <span className="text-[14px]">{link.name}</span>
            </Link>
          );
        })}
      </nav>
      <div className="px-6 py-stack-md border-t border-outline-variant">
        <div className="flex items-center gap-3 p-3 rounded-xl bg-surface-container-low">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-on-primary text-[18px]">person</span>
          </div>
          <div className="overflow-hidden">
            <p className="text-[14px] font-semibold text-on-surface truncate">Safety Officer</p>
            <p className="text-[12px] uppercase tracking-wider text-on-surface-variant">Admin</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
