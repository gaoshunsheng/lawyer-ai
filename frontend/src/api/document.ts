import request from './request'
import type { Document, DocumentQuery, DocumentTemplate, ApiResponse, PageResult } from '@/types'

export const documentApi = {
  // 获取文书列表
  getDocumentList(params: DocumentQuery) {
    return request.get<PageResult<Document>>('/documents', { params })
  },

  // 获取文书详情
  getDocumentDetail(id: number | string) {
    return request.get<Document>(`/documents/${id}`)
  },

  // 创建文书
  createDocument(data: Partial<Document>) {
    return request.post<Document>('/documents', data)
  },

  // 更新文书
  updateDocument(id: number | string, data: Partial<Document>) {
    return request.put<Document>(`/documents/${id}`, data)
  },

  // 删除文书
  deleteDocument(id: number | string) {
    return request.delete(`/documents/${id}`)
  },

  // 获取模板列表
  getTemplates() {
    return request.get<DocumentTemplate[]>('/documents/templates')
  },

  // 获取模板详情
  getTemplateDetail(id: string) {
    return request.get<DocumentTemplate>(`/documents/templates/${id}`)
  },

  // AI生成文书
  generateDocument(params: { templateId: string; caseId?: number; variables: Record<string, string>; style?: string }) {
    return request.post<{ content: string; suggestions: string[] }>('/documents/generate', params)
  },

  // AI分析文书
  analyzeDocument(content: string, docType: string) {
    return request.post<{ analysis: string; issues: string[]; suggestions: string[] }>('/documents/analyze', null, {
      params: { content, docType }
    })
  },

  // 导出文书
  exportDocument(id: number | string, format: 'word' | 'pdf') {
    return request.get(`/documents/${id}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  // 获取文书版本历史
  getDocumentVersions(id: number | string) {
    return request.get(`/documents/${id}/versions`)
  },

  // 恢复到指定版本
  restoreVersion(id: number | string, versionId: number) {
    return request.post(`/documents/${id}/versions/${versionId}/restore`)
  },
}
