<template>
  <div class="document-list-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="文书名称/内容"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="文书类型">
          <el-select v-model="searchForm.docType" placeholder="全部类型" clearable>
            <el-option label="仲裁申请书" value="arbitration_application" />
            <el-option label="起诉状" value="complaint" />
            <el-option label="答辩状" value="answer" />
            <el-option label="律师函" value="lawyer_letter" />
            <el-option label="和解协议" value="settlement_agreement" />
            <el-option label="证据清单" value="evidence_list" />
            <el-option label="代理词" value="agency_opinion" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联案件">
          <el-input
            v-model="searchForm.caseId"
            placeholder="案件ID"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建文书
      </el-button>
      <el-button @click="goToTemplate">
        <el-icon><Tickets /></el-icon>
        文书模板
      </el-button>
    </div>

    <!-- 文书列表 -->
    <el-card class="table-card">
      <el-table v-loading="loading" :data="documentList" style="width: 100%">
        <el-table-column prop="title" label="文书名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="docType" label="文书类型" width="140">
          <template #default="{ row }">
            <el-tag :type="getDocTypeTag(row.docType)">
              {{ getDocTypeLabel(row.docType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="caseName" label="关联案件" width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="创建人" width="100" />
        <el-table-column prop="updatedAt" label="更新时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="primary" text size="small" @click="handlePreview(row)">
              预览
            </el-button>
            <el-dropdown @command="handleCommand($event, row)">
              <el-button type="primary" text size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="export-word">导出Word</el-dropdown-item>
                  <el-dropdown-item command="export-pdf">导出PDF</el-dropdown-item>
                  <el-dropdown-item command="analyze">AI分析</el-dropdown-item>
                  <el-dropdown-item command="history">历史版本</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="文书预览" width="800px" destroy-on-close>
      <div class="document-preview" v-html="previewContent"></div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleExportFromPreview('word')">
          导出Word
        </el-button>
        <el-button type="primary" @click="handleExportFromPreview('pdf')">
          导出PDF
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Tickets, ArrowDown } from '@element-plus/icons-vue'
import type { Document } from '@/types'

const router = useRouter()
const documentStore = useDocumentStore()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  docType: '',
  caseId: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 状态
const loading = ref(false)
const documentList = ref<Document[]>([])
const previewVisible = ref(false)
const previewContent = ref('')
const currentDocument = ref<Document | null>(null)

// 方法
async function fetchData() {
  loading.value = true
  try {
    await documentStore.fetchDocuments({
      ...searchForm,
      page: pagination.page,
      size: pagination.size
    })
    documentList.value = documentStore.documentList
    pagination.total = documentStore.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  Object.assign(searchForm, {
    keyword: '',
    docType: '',
    caseId: ''
  })
  handleSearch()
}

function handleCreate() {
  router.push('/document/create')
}

function goToTemplate() {
  router.push('/document/template')
}

function handleEdit(row: Document) {
  router.push(`/document/edit/${row.id}`)
}

async function handlePreview(row: Document) {
  currentDocument.value = row
  previewContent.value = row.content || '<p>暂无内容</p>'
  previewVisible.value = true
}

async function handleCommand(command: string, row: Document) {
  currentDocument.value = row
  switch (command) {
    case 'export-word':
      await handleExport(row, 'word')
      break
    case 'export-pdf':
      await handleExport(row, 'pdf')
      break
    case 'analyze':
      handleAnalyze(row)
      break
    case 'history':
      handleHistory(row)
      break
    case 'delete':
      await handleDelete(row)
      break
  }
}

async function handleExport(row: Document, format: 'word' | 'pdf') {
  try {
    const res = await documentStore.exportDocument(row.id, format)
    // 创建下载链接
    const blob = new Blob([res as any], {
      type: format === 'word' ? 'application/msword' : 'application/pdf'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${row.title}.${format === 'word' ? 'docx' : 'pdf'}`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

function handleAnalyze(row: Document) {
  ElMessage.info('AI分析功能开发中')
}

function handleHistory(row: Document) {
  ElMessage.info('历史版本功能开发中')
}

async function handleDelete(row: Document) {
  try {
    await ElMessageBox.confirm('确定要删除该文书吗？删除后无法恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await documentStore.deleteDocument(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

function handleExportFromPreview(format: 'word' | 'pdf') {
  if (currentDocument.value) {
    handleExport(currentDocument.value, format)
  }
}

function handleSizeChange(size: number) {
  pagination.size = size
  fetchData()
}

function handleCurrentChange(page: number) {
  pagination.page = page
  fetchData()
}

function getDocTypeTag(type: string) {
  const types: Record<string, string> = {
    arbitration_application: 'danger',
    complaint: 'warning',
    answer: 'primary',
    lawyer_letter: 'success',
    settlement_agreement: 'info',
    evidence_list: '',
    agency_opinion: 'warning',
    other: 'info'
  }
  return types[type] || 'info'
}

function getDocTypeLabel(type: string) {
  const labels: Record<string, string> = {
    arbitration_application: '仲裁申请书',
    complaint: '起诉状',
    answer: '答辩状',
    lawyer_letter: '律师函',
    settlement_agreement: '和解协议',
    evidence_list: '证据清单',
    agency_opinion: '代理词',
    other: '其他'
  }
  return labels[type] || type
}

function getStatusType(status: string) {
  const types: Record<string, string> = {
    draft: 'info',
    reviewing: 'warning',
    finalized: 'success'
  }
  return types[status] || 'info'
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    draft: '草稿',
    reviewing: '审核中',
    finalized: '已定稿'
  }
  return labels[status] || status
}

function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.document-list-container {
  .search-card {
    margin-bottom: $spacing-md;
  }

  .action-bar {
    margin-bottom: $spacing-md;
  }

  .table-card {
    .pagination {
      margin-top: $spacing-md;
      display: flex;
      justify-content: flex-end;
    }
  }

  .document-preview {
    max-height: 60vh;
    overflow-y: auto;
    padding: $spacing-lg;
    background: $bg-page;
    border-radius: $border-radius;
    line-height: 1.8;
  }
}
</style>
