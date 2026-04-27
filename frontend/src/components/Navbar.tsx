import { Zap, Store, LogOut } from "lucide-react";

interface NavbarProps {
  merchantName: string;
  onLogout: () => void;
}

export default function Navbar({ merchantName, onLogout }: NavbarProps) {
  return (
    <nav className="h-[52px] shrink-0 flex items-center gap-4 px-6 bg-elevated border-b border-border-default">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 bg-accent rounded-md flex items-center justify-center">
          <Zap size={13} className="text-white" />
        </div>
        <span className="text-sm font-bold text-text-primary">Playto Pay</span>
      </div>

      {/* Divider */}
      <div className="w-px h-4 bg-border-strong" />
      <span className="text-xs text-text-dim">Dashboard</span>

      {/* Right side */}
      <div className="ml-auto flex items-center justify-center gap-3">
        <span className="flex items-center gap-1.5 text-xs text-text-muted">
          <Store size={12} className="text-text-dim" />
          {merchantName}
        </span>
        <button
          onClick={onLogout}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-text-subtle border border-border-strong rounded-md hover:border-text-dim transition-colors cursor-pointer"
        >
          <LogOut size={11} />
          Logout
        </button>
      </div>
      
    </nav>
  );
}
