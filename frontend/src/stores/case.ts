import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Case, CaseQuery, CaseAnalysis } from '@/types'
import { caseApi } from '@/api/case'

export const useCaseStore = defineStore('case', () => {
  // State
  const cases = ref<Case[]>([])
  const currentCase = ref<Case | null>(null)
  const caseAnalysis = ref<CaseAnalysis | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const queryParams = ref<CaseQuery>({
    page: 1,
    size: 10,
    keyword: '',
    status: '',
    caseType: '',
  })

  // Getters
  const caseList = computed(() => cases.value)
  const caseDetail = computed(() => currentCase.value)
  const hasMore = computed(() => cases.value.length < total.value)

  // Actions
  async function fetchCases(params?: Partial<CaseQuery>) {
    if (params) {
      queryParams.value = { ...queryParams.value, ...params }
    }
    loading.value = true
    try {
      const res = await caseApi.getCaseList(queryParams.value)
      cases.value = res.data.list
      total.value = res.data.total
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchCaseDetail(id: number | string) {
    loading.value = true
    try {
      const res = await caseApi.getCaseDetail(id)
      currentCase.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function createCase(data: Partial<Case>) {
    loading.value = true
    try {
      const res = await caseApi.createCase(data)
      await fetchCases()
      return res
    } finally {
      loading.value = false
    }
  }

  async function updateCase(id: number | string, data: Partial<Case>) {
    loading.value = true
    try {
      const res = await caseApi.updateCase(id, data)
      if (currentCase.value?.id === id) {
        currentCase.value = res.data
      }
      await fetchCases()
      return res
    } finally {
      loading.value = false
    }
  }

  async function deleteCase(id: number | string) {
    loading.value = true
    try {
      const res = await caseApi.deleteCase(id)
      await fetchCases()
      return res
    } finally {
      loading.value = false
    }
  }

  async function analyzeCase(id: number | string) {
    loading.value = true
    try {
      const res = await caseApi.analyzeCase(id)
      caseAnalysis.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function predictCase(params: { caseDescription: string; caseType: string; plaintiffType: string }) {
    loading.value = true
    try {
      const res = await caseApi.predictCase(params)
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
      status: '',
      caseType: '',
    }
  }

  function clearCurrentCase() {
    currentCase.value = null
    caseAnalysis.value = null
  }

  return {
    // State
    cases,
    currentCase,
    caseAnalysis,
    loading,
    total,
    queryParams,
    // Getters
    caseList,
    caseDetail,
    hasMore,
    // Actions
    fetchCases,
    fetchCaseDetail,
    createCase,
    updateCase,
    deleteCase,
    analyzeCase,
    predictCase,
    resetQuery,
    clearCurrentCase,
  }
})
