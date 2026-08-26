export function AppHeader() {
  return (
    <header className="fixed top-0 left-72 right-0 h-16 bg-surface/70 backdrop-blur-xl z-40 flex items-center px-container-margin justify-between shadow-[0_1px_8px_rgba(0,0,0,0.04)]">
      <div className="relative w-96">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">search</span>
        <input 
          className="w-full bg-surface-container/50 border border-white/40 rounded-full py-2 pl-10 pr-4 text-[14px] focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all" 
          placeholder="Search telemetry..." 
          type="text"
        />
      </div>
      <div className="flex items-center gap-stack-md">
        <div className="flex items-center bg-surface-container/50 border border-white/40 rounded-full p-1 gap-1 backdrop-blur-sm">
          <button className="w-8 h-8 flex items-center justify-center rounded-full bg-primary text-on-primary shadow-sm transition-all duration-300" title="Light Mode">
            <span className="material-symbols-outlined text-[18px]">light_mode</span>
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-full text-on-surface-variant hover:bg-surface-container-high transition-all duration-300" title="Dark Mode">
            <span className="material-symbols-outlined text-[18px]">dark_mode</span>
          </button>
        </div>
        <button className="p-2 rounded-full hover:bg-surface-container-high transition-colors relative">
          <span className="material-symbols-outlined text-on-surface-variant">notifications</span>
          <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full"></span>
        </button>
        <button className="p-2 rounded-full hover:bg-surface-container-high transition-colors">
          <span className="material-symbols-outlined text-on-surface-variant">settings</span>
        </button>
      </div>
    </header>
  );
}
