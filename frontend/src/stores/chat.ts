import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatSession, ChatMessage } from '@/types'
import { chatApi } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // State
  const sessions = ref<ChatSession[]>([])
  const currentSession = ref<ChatSession | null>(null)
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const sending = ref(false)

  // Getters
  const sessionList = computed(() => sessions.value)
  const currentMessages = computed(() => messages.value)
  const currentSessionId = computed(() => currentSession.value?.id)

  // Actions
  async function fetchSessions() {
    loading.value = true
    try {
      const res = await chatApi.getSessions()
      sessions.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchMessages(sessionId: string) {
    loading.value = true
    try {
      const res = await chatApi.getMessages(sessionId)
      messages.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function createSession(title?: string) {
    loading.value = true
    try {
      const res = await chatApi.createSession(title)
      currentSession.value = res.data
      messages.value = []
      await fetchSessions()
      return res
    } finally {
      loading.value = false
    }
  }

  async function deleteSession(sessionId: string) {
    loading.value = true
    try {
      const res = await chatApi.deleteSession(sessionId)
      await fetchSessions()
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
      return res
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(params: { message: string; sessionId?: string; stream?: boolean }) {
    sending.value = true
    try {
      // 添加用户消息
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        sessionId: params.sessionId || '',
        role: 'user',
        content: params.message,
        createdAt: new Date().toISOString(),
      }
      messages.value.push(userMessage)

      // 发送请求
      const res = await chatApi.query({
        message: params.message,
        sessionId: params.sessionId,
        stream: params.stream ?? false,
      })

      // 添加AI回复
      if (res.data) {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sessionId: res.data.sessionId,
          role: 'assistant',
          content: res.data.answer,
          references: res.data.references,
          createdAt: new Date().toISOString(),
        }
        messages.value.push(aiMessage)

        // 更新当前会话
        if (!currentSession.value && res.data.sessionId) {
          currentSession.value = {
            id: res.data.sessionId,
            title: params.message.slice(0, 50),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
        }
      }

      return res
    } finally {
      sending.value = false
    }
  }

  function setCurrentSession(session: ChatSession | null) {
    currentSession.value = session
    if (session) {
      fetchMessages(session.id)
    } else {
      messages.value = []
    }
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    // State
    sessions,
    currentSession,
    messages,
    loading,
    sending,
    // Getters
    sessionList,
    currentMessages,
    currentSessionId,
    // Actions
    fetchSessions,
    fetchMessages,
    createSession,
    deleteSession,
    sendMessage,
    setCurrentSession,
    clearMessages,
  }
})
