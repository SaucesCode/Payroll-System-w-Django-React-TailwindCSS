// src/pages/AttendancePage.tsx
import { useState, useEffect } from "react";
import api from "../api/axios";
import type { Attendance, Employee } from "../types";
import { Plus, Calendar } from "lucide-react";

const AttendancePage = () => {
  const [attendances, setAttendances] = useState<Attendance[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState({
    period_start: "",
    period_end: "",
  });

  const [formData, setFormData] = useState({
    employee_id: "",
    absences: 0,
    overtime_hours: 0,
    holiday_worked: 0,
  });

  const fetchData = async () => {
    try {
      const [attRes, empRes] = await Promise.all([
        api.get("/attendance/?ordering=-period_start"),
        api.get("/employees/"),
      ]);

      setAttendances(attRes.data.results || attRes.data);
      setEmployees(empRes.data.results || empRes.data);
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Auto fill current bi-weekly period
  const loadCurrentPeriod = () => {
    const today = new Date();
    let start, end;

    if (today.getDate() <= 15) {
      start = new Date(today.getFullYear(), today.getMonth(), 1);
      end = new Date(today.getFullYear(), today.getMonth(), 15);
    } else {
      start = new Date(today.getFullYear(), today.getMonth(), 16);
      end = new Date(today.getFullYear(), today.getMonth() + 1, 0); // Last day of month
    }

    setSelectedPeriod({
      period_start: start.toISOString().split("T")[0],
      period_end: end.toISOString().split("T")[0],
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/attendance/", {
        ...formData,
        period_start: selectedPeriod.period_start,
        period_end: selectedPeriod.period_end,
      });

      setShowModal(false);
      setFormData({ employee_id: "", absences: 0, overtime_hours: 0, holiday_worked: 0 });
      fetchData();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to save attendance");
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Attendance</h1>
            <p className="text-gray-600">Bi-weekly attendance records</p>
          </div>
          <button
            onClick={() => {
              loadCurrentPeriod();
              setShowModal(true);
            }}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-3 rounded-lg hover:bg-blue-700"
          >
            <Plus size={20} />
            Record Attendance
          </button>
        </div>

        {/* Attendance Table */}
        <div className="bg-white rounded-2xl shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left">Period</th>
                <th className="px-6 py-4 text-left">Employee</th>
                <th className="px-6 py-4 text-center">Days Worked</th>
                <th className="px-6 py-4 text-center">Absences</th>
                <th className="px-6 py-4 text-center">Overtime (hrs)</th>
                <th className="px-6 py-4 text-center">Holiday Worked</th>
              </tr>
            </thead>
            <tbody>
              {attendances.map(att => (
                <tr key={att.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      {att.period_start} → {att.period_end}
                    </div>
                  </td>
                  <td className="px-6 py-4 font-medium">{att.employee.full_name}</td>
                  <td className="px-6 py-4 text-center font-semibold text-green-600">
                    {att.days_worked}
                  </td>
                  <td className="px-6 py-4 text-center text-red-600 font-medium">
                    {att.absences}
                  </td>
                  <td className="px-6 py-4 text-center">{att.overtime_hours}</td>
                  <td className="px-6 py-4 text-center text-amber-600">
                    {att.holiday_worked}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Attendance Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-6">Record Attendance</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1">Employee</label>
                <select
                  value={formData.employee_id}
                  onChange={e => setFormData({ ...formData, employee_id: e.target.value })}
                  className="w-full border rounded-lg px-4 py-3"
                  required
                >
                  <option value="">Select Employee</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>
                      {emp.full_name} ({emp.employee_id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Period Start</label>
                  <input
                    type="date"
                    value={selectedPeriod.period_start}
                    onChange={e =>
                      setSelectedPeriod({ ...selectedPeriod, period_start: e.target.value })
                    }
                    className="w-full border rounded-lg px-4 py-3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Period End</label>
                  <input
                    type="date"
                    value={selectedPeriod.period_end}
                    onChange={e =>
                      setSelectedPeriod({ ...selectedPeriod, period_end: e.target.value })
                    }
                    className="w-full border rounded-lg px-4 py-3"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Absences</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.absences}
                    onChange={e =>
                      setFormData({ ...formData, absences: parseInt(e.target.value) || 0 })
                    }
                    className="w-full border rounded-lg px-4 py-3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Overtime (hrs)</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={formData.overtime_hours}
                    onChange={e =>
                      setFormData({
                        ...formData,
                        overtime_hours: parseFloat(e.target.value) || 0,
                      })
                    }
                    className="w-full border rounded-lg px-4 py-3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Holiday Worked</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.holiday_worked}
                    onChange={e =>
                      setFormData({
                        ...formData,
                        holiday_worked: parseInt(e.target.value) || 0,
                      })
                    }
                    className="w-full border rounded-lg px-4 py-3"
                  />
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-3 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save Attendance
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AttendancePage;
