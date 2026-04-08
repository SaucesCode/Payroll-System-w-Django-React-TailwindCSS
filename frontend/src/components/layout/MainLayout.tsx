// src/components/layout/MainLayout.tsx
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { LogOut, Users, Clock, DollarSign, Home } from "lucide-react";

const MainLayout = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { path: "/", label: "Dashboard", icon: Home },
    { path: "/employees", label: "Employees", icon: Users },
    { path: "/attendance", label: "Attendance", icon: Clock },
    { path: "/payroll", label: "Payroll", icon: DollarSign },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">PayrollPro</h1>
          <p className="text-sm text-gray-500">Management System</p>
        </div>

        <div className="flex-1 p-4">
          <nav className="space-y-1">
            {navItems.map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-600 font-medium"
                      : "hover:bg-gray-100 text-gray-700"
                  }`
                }
              >
                <item.icon size={20} />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="p-4 border-t">
          <div className="flex items-center gap-3 mb-4 px-4">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
              {user?.username?.[0]?.toUpperCase() || "U"}
            </div>
            <div>
              <p className="font-medium text-sm">{user?.username}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
          </div>

          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
};

export default MainLayout;
