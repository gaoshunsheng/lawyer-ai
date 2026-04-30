import request from './request'
import type { ChatSession, ChatMessage, ApiResponse } from '@/types'

export const chatApi = {
  // 发送消息（智能咨询）
  query(params: { message: string; sessionId?: string; stream?: boolean }) {
    return request.post<{ answer: string; sessionId: string; references?: any[] }>('/chat/query', params)
  },

  // 获取会话列表
  getSessions() {
    return request.get<ChatSession[]>('/chat/sessions')
  },

  // 获取会话消息
  getMessages(sessionId: string) {
    return request.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`)
  },

  // 创建新会话
  createSession(title?: string) {
    return request.post<ChatSession>('/chat/sessions', { title })
  },

  // 删除会话
  deleteSession(sessionId: string) {
    return request.delete(`/chat/sessions/${sessionId}`)
  },

  // 更新会话标题
  updateSessionTitle(sessionId: string, title: string) {
    return request.put(`/chat/sessions/${sessionId}`, { title })
  },

  // 导出会话
  exportSession(sessionId: string, format: 'txt' | 'word' | 'pdf' = 'txt') {
    return request.get(`/chat/sessions/${sessionId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },
}
