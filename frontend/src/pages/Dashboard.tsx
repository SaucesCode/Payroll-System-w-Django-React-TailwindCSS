// src/pages/Dashboard.tsx
import { useEffect, useState } from "react";
import api from "../api/axios";
import type { Payroll, Attendance } from "../types";

const Dashboard = () => {
  const [totalEmployees, setTotalEmployees] = useState(0);
  const [currentPayroll, setCurrentPayroll] = useState<Payroll[]>([]);
  const [recentAttendance, setRecentAttendance] = useState<Attendance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Get total employees
        const empRes = await api.get("/employees/");
        setTotalEmployees(empRes.data.count || empRes.data.length || 0);

        // Get current period payroll summary
        const payrollRes = await api.get("/payroll-summary/");
        // Note: We're using the summary endpoint we created earlier

        // Get recent attendance (last 2 periods)
        const attRes = await api.get("/attendance/?ordering=-period_start&limit=5");
        setRecentAttendance(attRes.data.results || attRes.data);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <div className="text-xl">Loading Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Welcome back! Here's what's happening this period.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-2xl shadow">
            <div className="text-sm text-gray-500">Total Employees</div>
            <div className="text-4xl font-bold text-gray-800 mt-2">{totalEmployees}</div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow">
            <div className="text-sm text-gray-500">Current Period</div>
            <div className="text-2xl font-semibold text-gray-700 mt-2">
              {new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" })}
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow">
            <div className="text-sm text-gray-500">This Period Payroll</div>
            <div className="text-4xl font-bold text-green-600 mt-2">
              ₱{currentPayroll.reduce((sum, p) => sum + p.net_salary, 0).toLocaleString()}
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow">
            <div className="text-sm text-gray-500">Avg Net Salary</div>
            <div className="text-4xl font-bold text-blue-600 mt-2">
              ₱
              {(
                currentPayroll.reduce((sum, p) => sum + p.net_salary, 0) /
                (currentPayroll.length || 1)
              ).toFixed(0)}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Attendance</h2>
            <div className="space-y-4">
              {recentAttendance.slice(0, 5).map(att => (
                <div key={att.id} className="flex justify-between items-center border-b pb-3">
                  <div>
                    <p className="font-medium">{att.employee.full_name}</p>
                    <p className="text-sm text-gray-500">
                      {att.period_start} → {att.period_end}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{att.days_worked} days</p>
                    <p className="text-sm text-red-600">{att.absences} absent</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => (window.location.href = "/employees")}
                className="p-6 bg-blue-50 hover:bg-blue-100 rounded-xl text-left transition"
              >
                <div className="text-blue-600 font-medium">Add Employee</div>
                <div className="text-sm text-gray-600 mt-1">Register new staff</div>
              </button>

              <button
                onClick={() => (window.location.href = "/attendance")}
                className="p-6 bg-green-50 hover:bg-green-100 rounded-xl text-left transition"
              >
                <div className="text-green-600 font-medium">Mark Attendance</div>
                <div className="text-sm text-gray-600 mt-1">Record today’s attendance</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
