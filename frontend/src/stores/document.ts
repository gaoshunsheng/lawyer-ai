import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Document, DocumentQuery, DocumentTemplate } from '@/types'
import { documentApi } from '@/api/document'

export const useDocumentStore = defineStore('document', () => {
  // State
  const documents = ref<Document[]>([])
  const templates = ref<DocumentTemplate[]>([])
  const currentDocument = ref<Document | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const queryParams = ref<DocumentQuery>({
    page: 1,
    size: 10,
    keyword: '',
    docType: '',
    caseId: '',
  })

  // Getters
  const documentList = computed(() => documents.value)
  const templateList = computed(() => templates.value)
  const documentDetail = computed(() => currentDocument.value)

  // Actions
  async function fetchDocuments(params?: Partial<DocumentQuery>) {
    if (params) {
      queryParams.value = { ...queryParams.value, ...params }
    }
    loading.value = true
    try {
      const res = await documentApi.getDocumentList(queryParams.value)
      documents.value = res.data.list
      total.value = res.data.total
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplates() {
    loading.value = true
    try {
      const res = await documentApi.getTemplates()
      templates.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function fetchDocumentDetail(id: number | string) {
    loading.value = true
    try {
      const res = await documentApi.getDocumentDetail(id)
      currentDocument.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function createDocument(data: Partial<Document>) {
    loading.value = true
    try {
      const res = await documentApi.createDocument(data)
      await fetchDocuments()
      return res
    } finally {
      loading.value = false
    }
  }

  async function updateDocument(id: number | string, data: Partial<Document>) {
    loading.value = true
    try {
      const res = await documentApi.updateDocument(id, data)
      if (currentDocument.value?.id === id) {
        currentDocument.value = res.data
      }
      await fetchDocuments()
      return res
    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(id: number | string) {
    loading.value = true
    try {
      const res = await documentApi.deleteDocument(id)
      await fetchDocuments()
      return res
    } finally {
      loading.value = false
    }
  }

  async function generateDocument(params: { templateId: string; caseId?: number; variables: Record<string, string> }) {
    loading.value = true
    try {
      const res = await documentApi.generateDocument(params)
      return res
    } finally {
      loading.value = false
    }
  }

  async function analyzeDocument(content: string, docType: string) {
    loading.value = true
    try {
      const res = await documentApi.analyzeDocument(content, docType)
      return res
    } finally {
      loading.value = false
    }
  }

  async function exportDocument(id: number | string, format: 'word' | 'pdf') {
    loading.value = true
    try {
      const res = await documentApi.exportDocument(id, format)
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
      caseId: '',
    }
  }

  function clearCurrentDocument() {
    currentDocument.value = null
  }

  return {
    // State
    documents,
    templates,
    currentDocument,
    loading,
    total,
    queryParams,
    // Getters
    documentList,
    templateList,
    documentDetail,
    // Actions
    fetchDocuments,
    fetchTemplates,
    fetchDocumentDetail,
    createDocument,
    updateDocument,
    deleteDocument,
    generateDocument,
    analyzeDocument,
    exportDocument,
    resetQuery,
    clearCurrentDocument,
  }
})
