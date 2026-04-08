// src/App.tsx
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";

// Layout
import MainLayout from "./components/layout/MainLayout";

// // Pages (we'll create these next)
// import Dashboard from "./pages/Dashboard";
// import EmployeesPage from "./pages/EmployeesPage";
// import AttendancePage from "./pages/AttendancePage";
// import PayrollPage from "./pages/PayrollPage";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<Login />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            {/* <Route index element={<Dashboard />} />
            <Route path="employees" element={<EmployeesPage />} />
            <Route path="attendance" element={<AttendancePage />} />
            <Route path="payroll" element={<PayrollPage />} /> */}
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
