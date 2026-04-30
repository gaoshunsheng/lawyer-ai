<template>
  <div class="error-page">
    <div class="error-content">
      <el-icon :size="120" color="#f56c6c"><CircleCloseFilled /></el-icon>
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { CircleCloseFilled } from '@element-plus/icons-vue'

const router = useRouter()

function goHome() {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: $bg-page;
}

.error-content {
  text-align: center;

  h1 {
    margin: $spacing-lg 0 $spacing-sm;
    font-size: 72px;
    font-weight: 600;
    color: $text-primary;
  }

  h2 {
    margin: 0 0 $spacing-sm;
    font-size: 24px;
    color: $text-primary;
  }

  p {
    margin: 0 0 $spacing-lg;
    color: $text-secondary;
  }
}
</style>
