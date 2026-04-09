// src/pages/PayrollPage.tsx
import { useState, useEffect, useCallback } from 'react';
import api from '../api/axios';
import type { Payroll, Employee } from '../types';
import { Plus } from 'lucide-react';
import { showToast } from '../utils/toast';

const PayrollPage = () => {
  const [payrolls, setPayrolls] = useState<Payroll[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generating, setGenerating] = useState(false);

  const [formData, setFormData] = useState({
    employee_id: '',
    period_start: '',
    period_end: '',
  });

  // Improved fetch function
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [payRes, empRes, sumRes] = await Promise.all([
        api.get('/payroll/?ordering=-period_start'),
        api.get('/employees/'),
        api.get('/payroll-summary/')
      ]);
      
      setPayrolls(payRes.data.results || payRes.data);
      setEmployees(empRes.data.results || empRes.data);
      setSummary(sumRes.data);
    } catch (error) {
      showToast.error('Failed to load payroll data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const loadCurrentPeriod = () => {
    const today = new Date();
    let start, end;

    if (today.getDate() <= 15) {
      start = new Date(today.getFullYear(), today.getMonth(), 1);
      end = new Date(today.getFullYear(), today.getMonth(), 15);
    } else {
      start = new Date(today.getFullYear(), today.getMonth(), 16);
      end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    }

    setFormData({
      employee_id: '',
      period_start: start.toISOString().split('T')[0],
      period_end: end.toISOString().split('T')[0],
    });
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);

    try {
      const payload: any = {
        period_start: formData.period_start,
        period_end: formData.period_end,
      };

      if (formData.employee_id) {
        payload.employee_id = parseInt(formData.employee_id);
      }

      const response = await api.post('/payroll/', payload);
      
      showToast.success('Payroll generated successfully!');
      setShowGenerateModal(false);
      
      // Force refresh data immediately
      await fetchData();
      
    } catch (error: any) {
      showToast.error(error.response?.data?.detail || 'Failed to generate payroll');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-lg">Loading Payroll...</div>;

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Payroll</h1>
            <p className="text-gray-600">Bi-weekly payroll management</p>
          </div>
          <button
            onClick={() => {
              loadCurrentPeriod();
              setShowGenerateModal(true);
            }}
            className="flex items-center gap-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            <Plus size={20} />
            Generate Payroll
          </button>
        </div>

        {/* Summary Card */}
        {summary && (
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-3xl p-8 mb-8">
            <h2 className="text-xl mb-6">
              Summary: {summary.period_start} to {summary.period_end}
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
              <div>
                <p className="text-blue-100 text-sm">Employees</p>
                <p className="text-4xl font-bold">{summary.total_employees}</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm">Total Gross</p>
                <p className="text-4xl font-bold">₱{Number(summary.total_gross_salary).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm">Total Net</p>
                <p className="text-4xl font-bold text-green-200">₱{Number(summary.total_net_salary).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm">Avg Net</p>
                <p className="text-4xl font-bold">₱{Number(summary.average_net_salary).toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}

        {/* Payroll Table */}
        <div className="bg-white rounded-2xl shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left">Period</th>
                <th className="px-6 py-4 text-left">Employee</th>
                <th className="px-6 py-4 text-right">Gross</th>
                <th className="px-6 py-4 text-right">Overtime</th>
                <th className="px-6 py-4 text-right">Holiday Pay</th>
                <th className="px-6 py-4 text-right">Net Salary</th>
              </tr>
            </thead>
            <tbody>
              {payrolls.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-500">
                    No payroll records yet. Click "Generate Payroll" to create one.
                  </td>
                </tr>
              ) : (
                payrolls.map((pay) => (
                  <tr key={pay.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4">{pay.period_start} → {pay.period_end}</td>
                    <td className="px-6 py-4 font-medium">{pay.employee.full_name}</td>
                    <td className="px-6 py-4 text-right">₱{pay.gross_salary.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right text-amber-600">₱{pay.overtime_pay.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right text-orange-600">₱{pay.holiday_pay.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right font-bold text-green-600">₱{pay.net_salary.toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Generate Modal - Same as before */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-6">Generate Payroll</h2>
            
            <form onSubmit={handleGenerate} className="space-y-5">
              <div>
                <label className="block text-sm font-medium mb-1">Employee</label>
                <select
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                  className="w-full border rounded-lg px-4 py-3"
                >
                  <option value="">All Active Employees</option>
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
                  <input type="date" value={formData.period_start} onChange={(e) => setFormData({...formData, period_start: e.target.value})} className="w-full border rounded-lg px-4 py-3" required />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Period End</label>
                  <input type="date" value={formData.period_end} onChange={(e) => setFormData({...formData, period_end: e.target.value})} className="w-full border rounded-lg px-4 py-3" required />
                </div>
              </div>

              <div className="flex gap-4 pt-6">
                <button type="button" onClick={() => setShowGenerateModal(false)} className="flex-1 py-3 border rounded-lg">Cancel</button>
                <button type="submit" disabled={generating} className="flex-1 py-3 bg-green-600 text-white rounded-lg disabled:opacity-70">
                  {generating ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PayrollPage;