import request from './request'
import type { ApiResponse } from '@/types'

// 统计数据类型
export interface StatisticsData {
  caseStatistics: {
    total: number
    byStatus: { status: string; count: number }[]
    byType: { type: string; count: number }[]
    byMonth: { month: string; count: number }[]
  }
  documentStatistics: {
    total: number
    byType: { type: string; count: number }[]
    byMonth: { month: string; count: number }[]
  }
  consultationStatistics: {
    total: number
    byMonth: { month: string; count: number }[]
  }
  winRateStatistics: {
    overall: number
    byType: { type: string; rate: number }[]
  }
}

export const statisticsApi = {
  // 获取总体统计
  getOverview() {
    return request.get<StatisticsData>('/statistics/overview')
  },

  // 获取案件统计
  getCaseStatistics(params?: { startDate?: string; endDate?: string }) {
    return request.get('/statistics/cases', { params })
  },

  // 获取文书统计
  getDocumentStatistics(params?: { startDate?: string; endDate?: string }) {
    return request.get('/statistics/documents', { params })
  },

  // 获取咨询统计
  getConsultationStatistics(params?: { startDate?: string; endDate?: string }) {
    return request.get('/statistics/consultations', { params })
  },

  // 获取胜诉率统计
  getWinRateStatistics(params?: { caseType?: string }) {
    return request.get('/statistics/win-rate', { params })
  },

  // 获取工作台数据
  getDashboardData() {
    return request.get<{
      todoList: any[]
      recentCases: any[]
      recentDocuments: any[]
      upcomingEvents: any[]
      statistics: {
        totalCases: number
        activeCases: number
        totalDocuments: number
        monthConsultations: number
      }
    }>('/statistics/dashboard')
  },

  // 导出统计报表
  exportReport(params: { type: string; startDate: string; endDate: string; format: 'excel' | 'pdf' }) {
    return request.get('/statistics/export', {
      params,
      responseType: 'blob'
    })
  },
}
