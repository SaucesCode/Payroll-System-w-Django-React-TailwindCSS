export interface Employee {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  position: string;
  department?: string;
  base_salary: number;
  email?: string;
  phone_number?: string;
  is_active: boolean;
}

export interface Attendance {
  id: number;
  employee: Employee;
  employee_id: number;
  days_worked: number;
  absences: number;
  overtime_hours: number;
  holiday_worked: number;
  period_start: string;
  period_end: string;
}

export interface Payroll {
  id: number;
  employee: Employee;
  period_start: string;
  period_end: string;
  gross_salary: number;
  overtime_pay: number;
  holiday_pay: number;
  pre_tax_deductions: number;
  tax: number;
  post_tax_deductions: number;
  net_salary: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
}

export interface User {
  id: number;
  username: string;
  role: "admin" | "payroll_officer" | "employee";
  first_name?: string;
  last_name?: string;
}
