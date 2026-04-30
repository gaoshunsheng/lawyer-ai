import request from './request'
import type { KnowledgeItem, KnowledgeQuery, ApiResponse, PageResult } from '@/types'

export const knowledgeApi = {
  // 获取知识列表
  getKnowledgeList(params: KnowledgeQuery) {
    return request.get<PageResult<KnowledgeItem>>('/knowledge', { params })
  },

  // 获取知识详情
  getKnowledgeDetail(id: number | string) {
    return request.get<KnowledgeItem>(`/knowledge/${id}`)
  },

  // 创建知识
  createKnowledge(data: Partial<KnowledgeItem>) {
    return request.post<KnowledgeItem>('/knowledge', data)
  },

  // 更新知识
  updateKnowledge(id: number | string, data: Partial<KnowledgeItem>) {
    return request.put<KnowledgeItem>(`/knowledge/${id}`, data)
  },

  // 删除知识
  deleteKnowledge(id: number | string) {
    return request.delete(`/knowledge/${id}`)
  },

  // 搜索知识
  searchKnowledge(params: { query: string; docTypes?: string[]; topK?: number; tenantId?: number }) {
    return request.post<any[]>('/knowledge/search', params)
  },

  // 上传文件
  uploadFile(data: FormData) {
    return request.post('/knowledge/upload', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 批量导入
  batchImport(data: { items: Partial<KnowledgeItem>[] }) {
    return request.post('/knowledge/batch', data)
  },

  // 获取分类列表
  getCategories() {
    return request.get<{ code: string; name: string }[]>('/knowledge/categories')
  },

  // 获取法规
  getLaws(params: { keyword?: string; category?: string; page?: number; size?: number }) {
    return request.get<PageResult<KnowledgeItem>>('/knowledge/laws', { params })
  },

  // 获取案例
  getCases(params: { keyword?: string; caseType?: string; page?: number; size?: number }) {
    return request.get<PageResult<KnowledgeItem>>('/knowledge/cases', { params })
  },
}
