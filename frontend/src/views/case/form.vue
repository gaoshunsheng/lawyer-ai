<template>
  <div class="case-form-container">
    <el-card>
      <template #header>
        <span class="card-title">{{ isEdit ? '编辑案件' : '创建案件' }}</span>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="case-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="案件名称" prop="title">
              <el-input v-model="form.title" placeholder="请输入案件名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="案号" prop="caseNumber">
              <el-input v-model="form.caseNumber" placeholder="请输入案号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="案件类型" prop="caseType">
              <el-select v-model="form.caseType" placeholder="请选择案件类型" style="width: 100%">
                <el-option label="违法解除" value="illegal_termination" />
                <el-option label="工伤赔偿" value="work_injury" />
                <el-option label="加班费争议" value="overtime" />
                <el-option label="年休假工资" value="annual_leave" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="案件状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择案件状态" style="width: 100%">
                <el-option label="待处理" value="pending" />
                <el-option label="仲裁阶段" value="arbitration" />
                <el-option label="一审阶段" value="first_instance" />
                <el-option label="二审阶段" value="second_instance" />
                <el-option label="已结案" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">当事人信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="原告/申请人" prop="plaintiff">
              <el-input v-model="form.plaintiff" placeholder="请输入原告/申请人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="被告/被申请人" prop="defendant">
              <el-input v-model="form.defendant" placeholder="请输入被告/被申请人" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="当事人角色" prop="plaintiffType">
              <el-radio-group v-model="form.plaintiffType">
                <el-radio label="employee">劳动者</el-radio>
                <el-radio label="employer">用人单位</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标的金额" prop="claimAmount">
              <el-input-number
                v-model="form.claimAmount"
                :min="0"
                :precision="2"
                placeholder="请输入标的金额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">案件详情</el-divider>

        <el-form-item label="争议焦点" prop="disputeFocus">
          <el-select
            v-model="form.disputeFocus"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入争议焦点"
            style="width: 100%"
          >
            <el-option label="是否构成违法解除" value="是否构成违法解除" />
            <el-option label="赔偿金计算标准" value="赔偿金计算标准" />
            <el-option label="加班费是否应支持" value="加班费是否应支持" />
            <el-option label="年休假工资" value="年休假工资" />
            <el-option label="工伤认定" value="工伤认定" />
            <el-option label="伤残等级" value="伤残等级" />
          </el-select>
        </el-form-item>

        <el-form-item label="案件描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述案件情况"
          />
        </el-form-item>

        <el-divider content-position="left">其他信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="办案律师" prop="lawyerId">
              <el-select v-model="form.lawyerId" placeholder="请选择办案律师" style="width: 100%">
                <el-option label="李律师" :value="1" />
                <el-option label="王律师" :value="2" />
                <el-option label="张律师" :value="3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="立案日期" prop="filingDate">
              <el-date-picker
                v-model="form.filingDate"
                type="date"
                placeholder="选择立案日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="form.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '创建案件' }}
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCaseStore } from '@/stores/case'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const route = useRoute()
const router = useRouter()
const caseStore = useCaseStore()

const formRef = ref<FormInstance>()
const saving = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  caseNumber: '',
  caseType: '',
  status: 'pending',
  plaintiff: '',
  defendant: '',
  plaintiffType: 'employee',
  claimAmount: 0,
  disputeFocus: [] as string[],
  description: '',
  lawyerId: null as number | null,
  filingDate: '',
  remarks: ''
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入案件名称', trigger: 'blur' }],
  caseNumber: [{ required: true, message: '请输入案号', trigger: 'blur' }],
  caseType: [{ required: true, message: '请选择案件类型', trigger: 'change' }],
  plaintiff: [{ required: true, message: '请输入原告/申请人', trigger: 'blur' }],
  defendant: [{ required: true, message: '请输入被告/被申请人', trigger: 'blur' }],
  claimAmount: [{ required: true, message: '请输入标的金额', trigger: 'blur' }]
}

async function fetchCaseDetail() {
  if (!isEdit.value) return

  try {
    const id = route.params.id as string
    await caseStore.fetchCaseDetail(id)
    if (caseStore.caseDetail) {
      Object.assign(form, {
        title: caseStore.caseDetail.title,
        caseNumber: caseStore.caseDetail.caseNumber,
        caseType: caseStore.caseDetail.caseType,
        status: caseStore.caseDetail.status,
        plaintiff: caseStore.caseDetail.plaintiff,
        defendant: caseStore.caseDetail.defendant,
        plaintiffType: caseStore.caseDetail.plaintiffType || 'employee',
        claimAmount: caseStore.caseDetail.claimAmount,
        disputeFocus: caseStore.caseDetail.disputeFocus || [],
        description: caseStore.caseDetail.description || '',
        lawyerId: caseStore.caseDetail.lawyerId,
        filingDate: caseStore.caseDetail.filingDate,
        remarks: caseStore.caseDetail.remarks || ''
      })
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取案件详情失败')
  }
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await caseStore.updateCase(route.params.id as string, form)
      ElMessage.success('修改成功')
    } else {
      await caseStore.createCase(form)
      ElMessage.success('创建成功')
    }
    router.push('/case/list')
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  router.back()
}

onMounted(() => {
  fetchCaseDetail()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.case-form-container {
  .card-title {
    font-size: $font-size-lg;
    font-weight: 600;
  }

  .case-form {
    max-width: 900px;
  }

  .el-divider {
    margin: $spacing-lg 0;
  }
}
</style>
