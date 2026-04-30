<template>
  <div class="document-form-container">
    <el-row :gutter="20">
      <!-- 编辑区域 -->
      <el-col :xs="24" :lg="18">
        <el-card class="editor-card">
          <template #header>
            <div class="editor-header">
              <el-input
                v-model="documentForm.title"
                placeholder="请输入文书标题"
                class="title-input"
              />
              <div class="editor-actions">
                <el-button @click="handleSaveDraft">保存草稿</el-button>
                <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
                <el-dropdown @command="handleExport">
                  <el-button>
                    导出<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="word">导出Word</el-dropdown-item>
                      <el-dropdown-item command="pdf">导出PDF</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>

          <!-- 工具栏 -->
          <div class="editor-toolbar">
            <el-button-group>
              <el-button size="small" @click="insertTemplate('law')">
                <el-icon><Document /></el-icon> 插入法条
              </el-button>
              <el-button size="small" @click="insertTemplate('case')">
                <el-icon><Files /></el-icon> 插入案例
              </el-button>
              <el-button size="small" @click="insertTemplate('calculate')">
                <el-icon><Calculator /></el-icon> 插入计算
              </el-button>
            </el-button-group>
            <el-button size="small" @click="showAIAssistant = true">
              <el-icon><MagicStick /></el-icon> AI辅助
            </el-button>
          </div>

          <!-- 编辑器 -->
          <div class="editor-content">
            <el-input
              v-model="documentForm.content"
              type="textarea"
              :rows="25"
              placeholder="请输入文书内容..."
              resize="none"
            />
          </div>

          <!-- 字数统计 -->
          <div class="editor-footer">
            <span>字数: {{ contentLength }}</span>
            <span>关联案件: {{ relatedCase?.title || '未关联' }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧面板 -->
      <el-col :xs="24" :lg="6">
        <!-- 基本信息 -->
        <el-card class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-form label-width="80px" size="small">
            <el-form-item label="文书类型">
              <el-select v-model="documentForm.docType" placeholder="请选择" style="width: 100%">
                <el-option label="仲裁申请书" value="arbitration_application" />
                <el-option label="起诉状" value="complaint" />
                <el-option label="答辩状" value="answer" />
                <el-option label="律师函" value="lawyer_letter" />
                <el-option label="和解协议" value="settlement_agreement" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="关联案件">
              <el-input
                v-model="relatedCase?.title"
                placeholder="选择关联案件"
                readonly
                @click="showCaseSelect = true"
              />
            </el-form-item>
            <el-form-item label="文书状态">
              <el-tag :type="getStatusType(documentForm.status)">
                {{ getStatusLabel(documentForm.status) }}
              </el-tag>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- AI建议 -->
        <el-card v-if="aiSuggestions.length" class="suggestion-card">
          <template #header>
            <div class="suggestion-header">
              <span>AI建议</span>
              <el-button text size="small" @click="refreshSuggestions">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="suggestion-list">
            <div
              v-for="(suggestion, index) in aiSuggestions"
              :key="index"
              class="suggestion-item"
              @click="applySuggestion(suggestion)"
            >
              <el-icon class="suggestion-icon"><InfoFilled /></el-icon>
              <span class="suggestion-text">{{ suggestion.text }}</span>
              <el-button text size="small">采纳</el-button>
            </div>
          </div>
        </el-card>

        <!-- 历史版本 -->
        <el-card class="history-card">
          <template #header>
            <span>历史版本</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="version in versions"
              :key="version.id"
              :timestamp="version.time"
              placement="top"
            >
              <div class="version-item">
                <span>{{ version.user }}</span>
                <el-button text size="small" @click="viewVersion(version)">查看</el-button>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI助手对话框 -->
    <el-dialog v-model="showAIAssistant" title="AI文书助手" width="600px" destroy-on-close>
      <div class="ai-assistant">
        <el-form label-width="80px">
          <el-form-item label="生成方式">
            <el-radio-group v-model="aiMode">
              <el-radio label="template">使用模板</el-radio>
              <el-radio label="case">根据案件</el-radio>
              <el-radio label="custom">自定义生成</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="aiMode === 'template'" label="选择模板">
            <el-select v-model="selectedTemplate" placeholder="请选择文书模板" style="width: 100%">
              <el-option label="劳动仲裁申请书" value="arbitration_application" />
              <el-option label="民事起诉状" value="complaint" />
              <el-option label="民事答辩状" value="answer" />
              <el-option label="律师函" value="lawyer_letter" />
            </el-select>
          </el-form-item>

          <el-form-item v-if="aiMode === 'template'" label="变量填充">
            <div class="variable-list">
              <el-input v-for="variable in templateVariables" :key="variable.key" v-model="variable.value" :placeholder="variable.label" class="variable-input" />
            </div>
          </el-form-item>

          <el-form-item v-if="aiMode === 'custom'" label="生成要求">
            <el-input
              v-model="customPrompt"
              type="textarea"
              :rows="4"
              placeholder="请描述您想要生成的文书内容和要求..."
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showAIAssistant = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="generateDocument">
          生成文书
        </el-button>
      </template>
    </el-dialog>

    <!-- 案件选择对话框 -->
    <el-dialog v-model="showCaseSelect" title="选择关联案件" width="600px" destroy-on-close>
      <el-input v-model="caseSearchKeyword" placeholder="搜索案件..." class="search-input" />
      <el-table :data="caseList" style="width: 100%" @row-click="selectCase">
        <el-table-column prop="caseNumber" label="案号" width="180" />
        <el-table-column prop="title" label="案件名称" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { ElMessage } from 'element-plus'
import {
  Document,
  Files,
  Calculator,
  MagicStick,
  ArrowDown,
  Refresh,
  InfoFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const documentStore = useDocumentStore()

const saving = ref(false)
const generating = ref(false)
const showAIAssistant = ref(false)
const showCaseSelect = ref(false)
const caseSearchKeyword = ref('')
const aiMode = ref('template')
const selectedTemplate = ref('')
const customPrompt = ref('')

const documentForm = reactive({
  title: '',
  content: '',
  docType: '',
  caseId: null as number | null,
  status: 'draft'
})

const relatedCase = ref<any>(null)

const templateVariables = ref([
  { key: 'applicant', label: '申请人姓名', value: '' },
  { key: 'applicantId', label: '申请人身份证号', value: '' },
  { key: 'respondent', label: '被申请人', value: '' },
  { key: 'claims', label: '仲裁请求', value: '' },
  { key: 'facts', label: '事实与理由', value: '' }
])

const aiSuggestions = ref([
  { id: 1, text: '建议在仲裁请求中明确加班费的计算基数，有利于主张' },
  { id: 2, text: '事实与理由部分建议补充公司规章制度未经过民主程序的相关表述' },
  { id: 3, text: '检测到年休假工资计算可能存在误差，建议核实' }
])

const versions = ref([
  { id: 1, user: '李律师', time: '2024-01-15 14:30' },
  { id: 2, user: '李律师', time: '2024-01-15 10:20' },
  { id: 3, user: '系统', time: '2024-01-14 16:45' }
])

const caseList = ref([
  { id: 1, caseNumber: '(2024)沪0101民初12345号', title: '张三 vs 某科技公司', status: 'arbitration', statusText: '仲裁阶段' },
  { id: 2, caseNumber: '(2024)沪0105民初6789号', title: '李四 vs 某贸易公司', status: 'first_instance', statusText: '一审阶段' }
])

const contentLength = computed(() => documentForm.content.length)

function handleSaveDraft() {
  documentForm.status = 'draft'
  handleSave()
}

async function handleSave() {
  saving.value = true
  try {
    if (route.params.id) {
      await documentStore.updateDocument(route.params.id as string, documentForm)
    } else {
      await documentStore.createDocument(documentForm)
    }
    ElMessage.success('保存成功')
    router.push('/document/list')
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function handleExport(format: string) {
  ElMessage.info(`导出${format.toUpperCase()}功能开发中`)
}

function insertTemplate(type: string) {
  if (type === 'law') {
    documentForm.content += '\n【法条引用】\n《劳动合同法》第XX条规定：...\n'
  } else if (type === 'case') {
    documentForm.content += '\n【案例参考】\n(2023)沪01民终12345号案件中，...\n'
  } else if (type === 'calculate') {
    documentForm.content += '\n【赔偿计算】\n违法解除赔偿金 = 工作年限 × 月工资 × 2\n'
  }
}

function refreshSuggestions() {
  ElMessage.success('已刷新AI建议')
}

function applySuggestion(suggestion: any) {
  ElMessage.success('已采纳建议')
}

async function generateDocument() {
  generating.value = true
  try {
    // 调用AI生成
    await new Promise(resolve => setTimeout(resolve, 2000))
    documentForm.content = `劳动人事争议仲裁申请书

申请人：张三，男，汉族，1985年3月出生，住上海市浦东新区...
被申请人：某科技公司
住所地：上海市浦东新区张江高科技园区...

仲裁请求：
一、请求裁决被申请人支付违法解除劳动合同赔偿金人民币132,000元；
二、请求裁决被申请人支付加班费人民币XX元；
三、请求裁决被申请人支付年休假工资人民币XX元。

事实与理由：
申请人于2020年6月1日入职被申请人处，担任软件工程师一职...

此致
上海市浦东新区劳动人事争议仲裁委员会

申请人：张三
2024年1月15日`
    showAIAssistant.value = false
    ElMessage.success('文书生成成功')
  } catch (error: any) {
    ElMessage.error(error.message || '生成失败')
  } finally {
    generating.value = false
  }
}

function selectCase(row: any) {
  relatedCase.value = row
  documentForm.caseId = row.id
  showCaseSelect.value = false
}

function viewVersion(version: any) {
  ElMessage.info('查看历史版本')
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

async function fetchDocumentDetail() {
  if (!route.params.id) return

  try {
    await documentStore.fetchDocumentDetail(route.params.id as string)
    if (documentStore.currentDocument) {
      Object.assign(documentForm, {
        title: documentStore.currentDocument.title,
        content: documentStore.currentDocument.content,
        docType: documentStore.currentDocument.docType,
        caseId: documentStore.currentDocument.caseId,
        status: documentStore.currentDocument.status
      })
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取文书详情失败')
  }
}

onMounted(() => {
  // 检查是否从模板创建
  if (route.query.templateId) {
    showAIAssistant.value = true
    selectedTemplate.value = route.query.templateId as string
  }
  fetchDocumentDetail()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.document-form-container {
  .editor-card {
    .editor-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title-input {
        flex: 1;
        margin-right: $spacing-md;

        :deep(.el-input__inner) {
          font-size: $font-size-lg;
          font-weight: 600;
        }
      }

      .editor-actions {
        display: flex;
        gap: $spacing-sm;
      }
    }

    .editor-toolbar {
      display: flex;
      justify-content: space-between;
      padding: $spacing-sm 0;
      border-bottom: 1px solid $border-lighter;
      margin-bottom: $spacing-md;
    }

    .editor-content {
      min-height: 500px;

      :deep(.el-textarea__inner) {
        font-family: 'Microsoft YaHei', sans-serif;
        line-height: 1.8;
        font-size: $font-size-base;
      }
    }

    .editor-footer {
      display: flex;
      justify-content: space-between;
      padding-top: $spacing-sm;
      border-top: 1px solid $border-lighter;
      margin-top: $spacing-md;
      font-size: $font-size-xs;
      color: $text-secondary;
    }
  }

  .info-card,
  .suggestion-card,
  .history-card {
    margin-bottom: $spacing-md;
  }

  .suggestion-card {
    .suggestion-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .suggestion-list {
      .suggestion-item {
        display: flex;
        align-items: flex-start;
        padding: $spacing-sm;
        border-radius: $border-radius;
        cursor: pointer;
        transition: background-color $transition-timing;

        &:hover {
          background-color: $bg-hover;
        }

        .suggestion-icon {
          color: $primary-color;
          margin-right: $spacing-sm;
          margin-top: 2px;
        }

        .suggestion-text {
          flex: 1;
          font-size: $font-size-sm;
          color: $text-regular;
          line-height: 1.5;
        }
      }
    }
  }

  .history-card {
    .version-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .ai-assistant {
    .variable-list {
      display: grid;
      gap: $spacing-sm;

      .variable-input {
        margin-bottom: $spacing-xs;
      }
    }
  }

  .search-input {
    margin-bottom: $spacing-md;
  }
}

@media (max-width: 1200px) {
  .document-form-container {
    .editor-card {
      .editor-header {
        flex-direction: column;
        align-items: flex-start;

        .title-input {
          margin-right: 0;
          margin-bottom: $spacing-sm;
          width: 100%;
        }

        .editor-actions {
          width: 100%;
          justify-content: flex-end;
        }
      }
    }
  }
}
</style>
