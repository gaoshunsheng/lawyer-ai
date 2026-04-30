import request from './request'
import type { Case, CaseQuery, CaseAnalysis, ApiResponse, PageResult } from '@/types'

export const caseApi = {
  // 获取案件列表
  getCaseList(params: CaseQuery) {
    return request.get<PageResult<Case>>('/cases', { params })
  },

  // 获取案件详情
  getCaseDetail(id: number | string) {
    return request.get<Case>(`/cases/${id}`)
  },

  // 创建案件
  createCase(data: Partial<Case>) {
    return request.post<Case>('/cases', data)
  },

  // 更新案件
  updateCase(id: number | string, data: Partial<Case>) {
    return request.put<Case>(`/cases/${id}`, data)
  },

  // 删除案件
  deleteCase(id: number | string) {
    return request.delete(`/cases/${id}`)
  },

  // 获取案件时间线
  getCaseTimeline(id: number | string) {
    return request.get(`/cases/${id}/timeline`)
  },

  // 添加时间线事件
  addTimelineEvent(id: number | string, data: { event: string; eventDate: string; description?: string }) {
    return request.post(`/cases/${id}/timeline`, data)
  },

  // 获取案件证据
  getCaseEvidence(id: number | string) {
    return request.get(`/cases/${id}/evidence`)
  },

  // 上传证据
  uploadEvidence(id: number | string, data: FormData) {
    return request.post(`/cases/${id}/evidence`, data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // AI案件分析
  analyzeCase(id: number | string) {
    return request.post<CaseAnalysis>(`/cases/${id}/analyze`)
  },

  // AI胜诉预测
  predictCase(params: { caseDescription: string; caseType: string; plaintiffType: string }) {
    return request.post<{ probability: number; analysis: string; similarCases: any[] }>('/cases/predict', params)
  },

  // 获取案件统计
  getCaseStatistics() {
    return request.get('/cases/statistics')
  },
}
