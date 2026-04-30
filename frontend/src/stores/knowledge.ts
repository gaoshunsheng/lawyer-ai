import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { KnowledgeItem, KnowledgeQuery } from '@/types'
import { knowledgeApi } from '@/api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  // State
  const knowledgeList = ref<KnowledgeItem[]>([])
  const currentKnowledge = ref<KnowledgeItem | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const queryParams = ref<KnowledgeQuery>({
    page: 1,
    size: 10,
    keyword: '',
    docType: '',
    category: '',
  })

  // Getters
  const list = computed(() => knowledgeList.value)
  const detail = computed(() => currentKnowledge.value)

  // Actions
  async function fetchKnowledgeList(params?: Partial<KnowledgeQuery>) {
    if (params) {
      queryParams.value = { ...queryParams.value, ...params }
    }
    loading.value = true
    try {
      const res = await knowledgeApi.getKnowledgeList(queryParams.value)
      knowledgeList.value = res.data.list
      total.value = res.data.total
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchKnowledgeDetail(id: number | string) {
    loading.value = true
    try {
      const res = await knowledgeApi.getKnowledgeDetail(id)
      currentKnowledge.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function searchKnowledge(params: { query: string; docTypes?: string[]; topK?: number }) {
    loading.value = true
    try {
      const res = await knowledgeApi.searchKnowledge(params)
      return res
    } finally {
      loading.value = false
    }
  }

  async function createKnowledge(data: Partial<KnowledgeItem>) {
    loading.value = true
    try {
      const res = await knowledgeApi.createKnowledge(data)
      await fetchKnowledgeList()
      return res
    } finally {
      loading.value = false
    }
  }

  async function updateKnowledge(id: number | string, data: Partial<KnowledgeItem>) {
    loading.value = true
    try {
      const res = await knowledgeApi.updateKnowledge(id, data)
      if (currentKnowledge.value?.id === id) {
        currentKnowledge.value = res.data
      }
      await fetchKnowledgeList()
      return res
    } finally {
      loading.value = false
    }
  }

  async function deleteKnowledge(id: number | string) {
    loading.value = true
    try {
      const res = await knowledgeApi.deleteKnowledge(id)
      await fetchKnowledgeList()
      return res
    } finally {
      loading.value = false
    }
  }

  function resetQuery() {
    queryParams.value = {
      page: 1,
      size: 10,
      keyword: '',
      docType: '',
      category: '',
    }
  }

  function clearCurrentKnowledge() {
    currentKnowledge.value = null
  }

  return {
    // State
    knowledgeList,
    currentKnowledge,
    loading,
    total,
    queryParams,
    // Getters
    list,
    detail,
    // Actions
    fetchKnowledgeList,
    fetchKnowledgeDetail,
    searchKnowledge,
    createKnowledge,
    updateKnowledge,
    deleteKnowledge,
    resetQuery,
    clearCurrentKnowledge,
  }
})
