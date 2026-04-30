<template>
  <div class="template-container">
    <!-- 模板分类 -->
    <div class="template-categories">
      <el-radio-group v-model="selectedCategory" @change="handleCategoryChange">
        <el-radio-button label="all">全部模板</el-radio-button>
        <el-radio-button label="arbitration">仲裁文书</el-radio-button>
        <el-radio-button label="litigation">诉讼文书</el-radio-button>
        <el-radio-button label="letter">函件文书</el-radio-button>
        <el-radio-button label="agreement">协议文书</el-radio-button>
        <el-radio-button label="other">其他文书</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 模板列表 -->
    <div class="template-grid">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-card"
        @click="handleSelectTemplate(template)"
      >
        <div class="template-icon">
          <el-icon :size="40"><Document /></el-icon>
        </div>
        <div class="template-info">
          <h3 class="template-name">{{ template.name }}</h3>
          <p class="template-desc">{{ template.description }}</p>
          <div class="template-meta">
            <el-tag size="small" :type="getCategoryTag(template.category)">
              {{ getCategoryLabel(template.category) }}
            </el-tag>
            <span class="use-count">使用 {{ template.useCount }} 次</span>
          </div>
        </div>
        <div class="template-actions">
          <el-button type="primary" size="small" @click.stop="handleUseTemplate(template)">
            使用模板
          </el-button>
          <el-button size="small" @click.stop="handlePreviewTemplate(template)">
            预览
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="filteredTemplates.length === 0" description="暂无模板" />

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" :title="previewTemplate?.name" width="800px" destroy-on-close>
      <div class="template-preview">
        <div class="preview-section">
          <h4>模板说明</h4>
          <p>{{ previewTemplate?.description }}</p>
        </div>
        <div class="preview-section">
          <h4>适用场景</h4>
          <p>{{ previewTemplate?.usage }}</p>
        </div>
        <div class="preview-section">
          <h4>所需变量</h4>
          <el-tag
            v-for="variable in previewTemplate?.variables"
            :key="variable"
            class="variable-tag"
          >
            {{ variable }}
          </el-tag>
        </div>
        <div class="preview-section">
          <h4>模板内容预览</h4>
          <div class="content-preview" v-html="previewTemplate?.preview"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleUseTemplate(previewTemplate!)">
          使用此模板
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDocumentStore } from '@/stores/document'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import type { DocumentTemplate } from '@/types'

const router = useRouter()
const documentStore = useDocumentStore()

const selectedCategory = ref('all')
const previewVisible = ref(false)
const previewTemplate = ref<DocumentTemplate | null>(null)

// 模板数据
const templates = ref<DocumentTemplate[]>([
  {
    id: 'arbitration_application',
    name: '劳动仲裁申请书',
    description: '适用于劳动者申请劳动仲裁，包含仲裁请求、事实与理由等必备内容',
    category: 'arbitration',
    useCount: 1256,
    usage: '劳动者与用人单位发生劳动争议，向劳动人事争议仲裁委员会申请仲裁时使用',
    variables: ['申请人姓名', '申请人身份证号', '被申请人名称', '仲裁请求', '事实与理由'],
    preview: '<h3>劳动人事争议仲裁申请书</h3><p>申请人：{{申请人姓名}}，身份证号：{{申请人身份证号}}</p><p>被申请人：{{被申请人名称}}</p><p><strong>仲裁请求：</strong></p><p>{{仲裁请求}}</p><p><strong>事实与理由：</strong></p><p>{{事实与理由}}</p>'
  },
  {
    id: 'complaint',
    name: '民事起诉状',
    description: '劳动争议一审诉讼起诉状，包含诉讼请求、事实与理由等内容',
    category: 'litigation',
    useCount: 892,
    usage: '劳动争议案件向人民法院提起诉讼时使用',
    variables: ['原告姓名', '原告身份证号', '被告名称', '诉讼请求', '事实与理由'],
    preview: '<h3>民事起诉状</h3><p>原告：{{原告姓名}}，身份证号：{{原告身份证号}}</p><p>被告：{{被告名称}}</p><p><strong>诉讼请求：</strong></p><p>{{诉讼请求}}</p>'
  },
  {
    id: 'answer',
    name: '民事答辩状',
    description: '劳动争议案件答辩状，针对原告起诉进行答辩',
    category: 'litigation',
    useCount: 567,
    usage: '作为被告对原告的起诉进行答辩时使用',
    variables: ['答辩人', '原告', '答辩意见', '证据清单'],
    preview: '<h3>民事答辩状</h3><p>答辩人：{{答辩人}}</p><p>因原告{{原告}}起诉答辩人劳动争议一案，现提出如下答辩意见：</p>'
  },
  {
    id: 'lawyer_letter',
    name: '律师函',
    description: '律师函模板，用于催告、通知等法律事务',
    category: 'letter',
    useCount: 1567,
    usage: '需要通过律师发出正式法律函件时使用',
    variables: ['发函律师', '收函人', '函件内容', '法律依据', '期限要求'],
    preview: '<h3>律师函</h3><p>{{收函人}}：</p><p>{{发函律师}}律师事务所接受委托，就相关事宜致函如下：</p>'
  },
  {
    id: 'settlement_agreement',
    name: '和解协议书',
    description: '劳动争议和解协议模板，适用于双方协商和解',
    category: 'agreement',
    useCount: 423,
    usage: '劳动者与用人单位协商解决劳动争议时使用',
    variables: ['甲方', '乙方', '协议内容', '赔偿金额', '履行期限'],
    preview: '<h3>和解协议书</h3><p>甲方：{{甲方}}</p><p>乙方：{{乙方}}</p><p>双方就劳动争议一事，经协商达成如下协议：</p>'
  },
  {
    id: 'evidence_list',
    name: '证据清单',
    description: '劳动争议案件证据清单模板，用于整理提交证据',
    category: 'other',
    useCount: 756,
    usage: '向仲裁委或法院提交证据时使用',
    variables: ['当事人', '案号', '证据列表'],
    preview: '<h3>证据清单</h3><p>当事人：{{当事人}}</p><p>案号：{{案号}}</p><table><tr><th>序号</th><th>证据名称</th><th>证明目的</th><th>页数</th></tr></table>'
  },
  {
    id: 'agency_opinion',
    name: '代理词',
    description: '劳动争议案件代理词模板，用于庭审代理发言',
    category: 'litigation',
    useCount: 345,
    usage: '律师代理劳动争议案件庭审时使用',
    variables: ['代理人', '当事人', '代理意见', '法律依据'],
    preview: '<h3>代理词</h3><p>尊敬的审判长、审判员：</p><p>{{代理人}}接受{{当事人}}的委托，作为其代理人，现发表如下代理意见：</p>'
  },
  {
    id: 'work_injury_application',
    name: '工伤认定申请书',
    description: '工伤认定申请模板，适用于申请工伤认定',
    category: 'other',
    useCount: 234,
    usage: '劳动者或用人单位向人力资源和社会保障局申请工伤认定时使用',
    variables: ['申请人', '受伤职工', '事故经过', '伤害部位', '诊断结论'],
    preview: '<h3>工伤认定申请书</h3><p>申请人：{{申请人}}</p><p>受伤职工：{{受伤职工}}</p><p><strong>事故经过：</strong></p><p>{{事故经过}}</p>'
  }
])

const filteredTemplates = computed(() => {
  if (selectedCategory.value === 'all') {
    return templates.value
  }
  return templates.value.filter(t => t.category === selectedCategory.value)
})

function handleCategoryChange() {
  // 分类变化时可以加载不同的模板
}

function handleSelectTemplate(template: DocumentTemplate) {
  previewTemplate.value = template
  previewVisible.value = true
}

function handlePreviewTemplate(template: DocumentTemplate) {
  previewTemplate.value = template
  previewVisible.value = true
}

function handleUseTemplate(template: DocumentTemplate) {
  router.push({
    path: '/document/create',
    query: { templateId: template.id }
  })
}

function getCategoryTag(category: string) {
  const tags: Record<string, string> = {
    arbitration: 'danger',
    litigation: 'warning',
    letter: 'success',
    agreement: 'info',
    other: ''
  }
  return tags[category] || ''
}

function getCategoryLabel(category: string) {
  const labels: Record<string, string> = {
    arbitration: '仲裁文书',
    litigation: '诉讼文书',
    letter: '函件文书',
    agreement: '协议文书',
    other: '其他文书'
  }
  return labels[category] || category
}

onMounted(() => {
  // 可以从后端加载模板列表
  // documentStore.fetchTemplates()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.template-container {
  .template-categories {
    margin-bottom: $spacing-lg;
  }

  .template-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: $spacing-lg;
  }

  .template-card {
    background: $bg-color;
    border-radius: $border-radius;
    padding: $spacing-lg;
    box-shadow: $box-shadow-light;
    transition: all $transition-duration $transition-timing;
    cursor: pointer;

    &:hover {
      transform: translateY(-4px);
      box-shadow: $box-shadow;

      .template-actions {
        opacity: 1;
      }
    }

    .template-icon {
      width: 60px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: $border-radius;
      color: #fff;
      margin-bottom: $spacing-md;
    }

    .template-info {
      .template-name {
        margin: 0 0 $spacing-sm;
        font-size: $font-size-lg;
        color: $text-primary;
      }

      .template-desc {
        margin: 0 0 $spacing-sm;
        font-size: $font-size-sm;
        color: $text-secondary;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .template-meta {
        display: flex;
        align-items: center;
        gap: $spacing-sm;

        .use-count {
          font-size: $font-size-xs;
          color: $text-placeholder;
        }
      }
    }

    .template-actions {
      margin-top: $spacing-md;
      padding-top: $spacing-md;
      border-top: 1px solid $border-lighter;
      display: flex;
      gap: $spacing-sm;
      opacity: 0;
      transition: opacity $transition-timing;
    }
  }
}

.template-preview {
  .preview-section {
    margin-bottom: $spacing-lg;

    h4 {
      margin: 0 0 $spacing-sm;
      color: $text-primary;
    }

    p {
      margin: 0;
      color: $text-regular;
      line-height: 1.6;
    }

    .variable-tag {
      margin-right: $spacing-xs;
      margin-bottom: $spacing-xs;
    }

    .content-preview {
      padding: $spacing-md;
      background: $bg-page;
      border-radius: $border-radius;
      line-height: 1.8;
    }
  }
}

@media (max-width: 768px) {
  .template-container {
    .template-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
