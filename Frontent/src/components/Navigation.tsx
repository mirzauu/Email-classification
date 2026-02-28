import { ShoppingCart, LogOut, User, Link as LinkIcon } from "lucide-react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Navigation = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    navigate("/login");
  };

  return (
    <nav className="bg-background px-8 py-6">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <h1 className="text-foreground text-xl font-normal">superpower</h1>

        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 bg-nav-pill rounded-full px-8 py-3 flex items-center gap-8">
          <Link
            to="/"
            className={`text-sm hover:text-white/80 transition-colors ${location.pathname === "/" ? "text-white" : "text-white/40"
              }`}
          >
            Home
          </Link>
          <Link
            to="/finance"
            className={`text-sm hover:text-white/80 transition-colors ${location.pathname === "/finance" ? "text-white" : "text-white/40"
              }`}
          >
            Finance
          </Link>
          <Link
            to="/team"
            className={`text-sm hover:text-white/80 transition-colors ${location.pathname === "/team" ? "text-white" : "text-white/40"
              }`}
          >
            Team
          </Link>
          <Link
            to="/concierge"
            className={`text-sm hover:text-white/80 transition-colors ${location.pathname === "/concierge" ? "text-white" : "text-white/40"
              }`}
          >
            Concierge
          </Link>
          <Link
            to="/services"
            className={`text-sm hover:text-white/80 transition-colors ${location.pathname === "/services" ? "text-white" : "text-white/40"
              }`}
          >
            Services
          </Link>
          <Link
            to="/settings"
            className={`text-sm hover:text-white/80 transition-colors ${location.pathname === "/settings" ? "text-white" : "text-white/40"
              }`}
          >
            Settings
          </Link>
        </div>

        <div className="flex items-center gap-6">
          <span className="text-muted-foreground text-sm cursor-pointer hover:text-foreground transition-colors">Invite Friend</span>
          <ShoppingCart className="w-5 h-5 text-foreground cursor-pointer hover:text-foreground/80 transition-colors" />

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 cursor-pointer hover:ring-2 hover:ring-primary/20 transition-all active:scale-95" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-card/95 backdrop-blur-sm border-border/50">
              <div className="flex items-center gap-2 p-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-500" />
                <div className="flex flex-col">
                  <span className="text-sm font-medium">Max Marchione</span>
                  <span className="text-xs text-muted-foreground">Premium Account</span>
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer" onClick={() => navigate("/settings")}>
                <User className="mr-2 h-4 w-4" />
                <span>Settings & Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={handleLogout}
                className="cursor-pointer text-destructive focus:text-destructive focus:bg-destructive/10"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>Logout</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
