<template>
  <div class="user-management-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="全部角色" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="主办律师" value="lawyer" />
            <el-option label="律师助理" value="assistant" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon> 添加用户
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-card>
      <el-table :data="userList" style="width: 100%">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="disabled"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginAt" label="最后登录" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" text size="small" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :total="total"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 用户编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '添加用户'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="userForm" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="主办律师" value="lawyer" />
            <el-option label="律师助理" value="assistant" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-input v-model="userForm.department" placeholder="请输入部门" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const searchForm = reactive({
  username: '',
  name: '',
  role: '',
  status: ''
})

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(50)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()

const userForm = reactive({
  id: null as number | null,
  username: '',
  password: '',
  name: '',
  email: '',
  phone: '',
  role: '',
  department: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const userList = ref([
  { id: 1, username: 'admin', name: '管理员', email: 'admin@example.com', phone: '13800138001', role: 'admin', department: '管理部', status: 'active', lastLoginAt: '2024-01-15 10:30' },
  { id: 2, username: 'lawyer001', name: '李律师', email: 'lawyer001@example.com', phone: '13800138002', role: 'lawyer', department: '劳动法团队', status: 'active', lastLoginAt: '2024-01-15 09:20' },
  { id: 3, username: 'lawyer002', name: '王律师', email: 'lawyer002@example.com', phone: '13800138003', role: 'lawyer', department: '劳动法团队', status: 'active', lastLoginAt: '2024-01-14 16:45' },
  { id: 4, username: 'assistant001', name: '张助理', email: 'assistant001@example.com', phone: '13800138004', role: 'assistant', department: '劳动法团队', status: 'active', lastLoginAt: '2024-01-14 14:30' },
  { id: 5, username: 'lawyer003', name: '赵律师', email: 'lawyer003@example.com', phone: '13800138005', role: 'lawyer', department: '公司法团队', status: 'disabled', lastLoginAt: '2024-01-10 11:00' }
])

function handleSearch() {
  ElMessage.info('搜索功能')
}

function handleReset() {
  Object.assign(searchForm, { username: '', name: '', role: '', status: '' })
}

function handlePageChange(page: number) {
  currentPage.value = page
}

function handleCreate() {
  isEdit.value = false
  Object.assign(userForm, {
    id: null,
    username: '',
    password: '',
    name: '',
    email: '',
    phone: '',
    role: '',
    department: ''
  })
  dialogVisible.value = true
}

function handleEdit(row: any) {
  isEdit.value = true
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    name: row.name,
    email: row.email,
    phone: row.phone,
    role: row.role,
    department: row.department
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success(isEdit.value ? '修改成功' : '添加成功')
    dialogVisible.value = false
  } finally {
    saving.value = false
  }
}

function handleStatusChange(row: any) {
  ElMessage.success(`已${row.status === 'active' ? '启用' : '禁用'}用户`)
}

async function handleResetPassword(row: any) {
  try {
    await ElMessageBox.confirm(`确定要重置用户 "${row.name}" 的密码吗？`, '提示', { type: 'warning' })
    ElMessage.success('密码已重置为默认密码')
  } catch {
    // 取消
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.name}" 吗？`, '提示', { type: 'warning' })
    ElMessage.success('删除成功')
  } catch {
    // 取消
  }
}

function getRoleType(role: string) {
  const types: Record<string, string> = {
    admin: 'danger',
    lawyer: 'primary',
    assistant: 'info'
  }
  return types[role] || 'info'
}

function getRoleLabel(role: string) {
  const labels: Record<string, string> = {
    admin: '管理员',
    lawyer: '主办律师',
    assistant: '律师助理'
  }
  return labels[role] || role
}

onMounted(() => {
  // 加载用户列表
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.user-management-container {
  .search-card {
    margin-bottom: $spacing-md;
  }

  .action-bar {
    margin-bottom: $spacing-md;
  }

  .pagination {
    margin-top: $spacing-md;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
