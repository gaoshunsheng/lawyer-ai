import request from './request'
import type { ApiResponse } from '@/types'

// 赔偿计算参数
export interface CompensationParams {
  type: 'illegal_termination' | 'overtime' | 'annual_leave' | 'work_injury'
  entryDate: string
  leaveDate: string
  salary: number
  salaryComponents?: {
    base: number
    performance: number
    allowance: number
    bonus: number
  }
  averageSalary?: number
  city?: string
  // 加班费相关
  overtimeHours?: number
  overtimeType?: 'weekday' | 'weekend' | 'holiday'
  // 年休假相关
  annualLeaveDays?: number
  usedLeaveDays?: number
  // 工伤相关
  injuryLevel?: number
  disabilityLevel?: number
}

// 赔偿计算结果
export interface CompensationResult {
  type: string
  items: {
    name: string
    amount: number
    formula: string
    basis: string
  }[]
  totalAmount: number
  calculationDetails: string
  legalBasis: string[]
}

export const calculatorApi = {
  // 计算赔偿
  calculate(params: CompensationParams) {
    return request.post<CompensationResult>('/calculator/compensation', params)
  },

  // 获取城市平均工资
  getAverageSalary(city: string) {
    return request.get<{ city: string; averageSalary: number; year: number }>('/calculator/average-salary', {
      params: { city }
    })
  },

  // 计算违法解除赔偿
  calculateIllegalTermination(params: {
    entryDate: string
    leaveDate: string
    salary: number
    averageSalary?: number
    isHighSalaryCapped?: boolean
  }) {
    return request.post<CompensationResult>('/calculator/illegal-termination', params)
  },

  // 计算加班费
  calculateOvertime(params: {
    salary: number
    overtimeHours: number
    overtimeType: 'weekday' | 'weekend' | 'holiday'
  }) {
    return request.post<CompensationResult>('/calculator/overtime', params)
  },

  // 计算年休假工资
  calculateAnnualLeave(params: {
    salary: number
    annualLeaveDays: number
    usedLeaveDays: number
    workYears: number
  }) {
    return request.post<CompensationResult>('/calculator/annual-leave', params)
  },

  // 计算工伤赔偿
  calculateWorkInjury(params: {
    salary: number
    injuryLevel: number
    disabilityLevel?: number
    city: string
  }) {
    return request.post<CompensationResult>('/calculator/work-injury', params)
  },

  // 获取历史计算记录
  getHistory(params?: { page?: number; size?: number }) {
    return request.get('/calculator/history', { params })
  },
}
