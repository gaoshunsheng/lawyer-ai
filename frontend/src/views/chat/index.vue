<template>
  <div class="chat-container">
    <!-- 会话列表 -->
    <div class="session-list">
      <div class="session-header">
        <h3>会话记录</h3>
        <el-button type="primary" size="small" @click="handleNewSession">
          <el-icon><Plus /></el-icon>
          新建会话
        </el-button>
      </div>

      <div class="session-search">
        <el-input
          v-model="sessionSearch"
          placeholder="搜索会话"
          prefix-icon="Search"
          clearable
        />
      </div>

      <div class="sessions">
        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="session-item"
          :class="{ active: currentSessionId === session.id }"
          @click="handleSelectSession(session)"
        >
          <div class="session-content">
            <div class="session-title">{{ session.title || '新会话' }}</div>
            <div class="session-time">{{ formatTime(session.updatedAt) }}</div>
          </div>
          <el-dropdown @command="handleSessionCommand($event, session)">
            <el-icon class="session-more"><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="rename">重命名</el-dropdown-item>
                <el-dropdown-item command="export">导出</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-area">
      <!-- 消息列表 -->
      <div ref="messageListRef" class="message-list">
        <div v-if="!currentSessionId" class="empty-chat">
          <el-icon :size="64"><ChatDotSquare /></el-icon>
          <h3>智能法律咨询助手</h3>
          <p>我可以帮助您解答劳动法相关的问题，包括：</p>
          <div class="quick-questions">
            <el-tag
              v-for="question in quickQuestions"
              :key="question"
              class="quick-tag"
              @click="handleQuickQuestion(question)"
            >
              {{ question }}
            </el-tag>
          </div>
        </div>

        <template v-else>
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-item"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar v-if="message.role === 'user'" :size="36">
                {{ userStore.userInfo?.name?.charAt(0) || 'U' }}
              </el-avatar>
              <el-avatar v-else :size="36" class="ai-avatar">
                <el-icon><Service /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-name">
                  {{ message.role === 'user' ? '我' : 'AI助手' }}
                </span>
                <span class="message-time">{{ formatTime(message.createdAt) }}</span>
              </div>
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              <!-- 引用内容 -->
              <div v-if="message.references && message.references.length" class="references">
                <div class="references-title">相关法规/案例：</div>
                <div
                  v-for="(ref, index) in message.references"
                  :key="index"
                  class="reference-item"
                >
                  <el-icon><Document /></el-icon>
                  <span>{{ ref.title }}</span>
                </div>
              </div>
              <!-- 操作按钮 -->
              <div v-if="message.role === 'assistant'" class="message-actions">
                <el-button text size="small" @click="handleCopy(message.content)">
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
                <el-button text size="small" @click="handleCreateDocument(message)">
                  <el-icon><Document /></el-icon>
                  生成文书
                </el-button>
              </div>
            </div>
          </div>
        </template>

        <div v-if="sending" class="message-item assistant">
          <div class="message-avatar">
            <el-avatar :size="36" class="ai-avatar">
              <el-icon><Service /></el-icon>
            </el-avatar>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-tools">
          <el-upload
            :show-file-list="false"
            :before-upload="handleUpload"
            accept=".pdf,.doc,.docx,.txt"
          >
            <el-button text>
              <el-icon><Paperclip /></el-icon>
              附件
            </el-button>
          </el-upload>
        </div>
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入您的法律问题..."
            resize="none"
            @keydown.enter.ctrl="handleSend"
          />
          <el-button
            type="primary"
            :loading="sending"
            :disabled="!inputMessage.trim()"
            @click="handleSend"
          >
            <el-icon><Promotion /></el-icon>
            发送
          </el-button>
        </div>
        <div class="input-hint">
          按 Ctrl + Enter 发送消息
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  Plus,
  MoreFilled,
  ChatDotSquare,
  Service,
  Document,
  CopyDocument,
  Paperclip,
  Promotion
} from '@element-plus/icons-vue'
import type { ChatSession } from '@/types'

const chatStore = useChatStore()
const userStore = useUserStore()

const sessionSearch = ref('')
const inputMessage = ref('')
const sending = ref(false)
const messageListRef = ref<HTMLElement>()

const quickQuestions = [
  '违法解除如何认定？',
  '加班费怎么计算？',
  '年休假工资如何赔偿？',
  '工伤认定条件有哪些？'
]

// 计算属性
const currentSessionId = computed(() => chatStore.currentSessionId)
const messages = computed(() => chatStore.currentMessages)
const sessions = computed(() => chatStore.sessionList)

const filteredSessions = computed(() => {
  if (!sessionSearch.value) return sessions.value
  const keyword = sessionSearch.value.toLowerCase()
  return sessions.value.filter(s => s.title?.toLowerCase().includes(keyword))
})

// 方法
async function handleNewSession() {
  try {
    await chatStore.createSession()
    ElMessage.success('创建新会话成功')
  } catch (error: any) {
    ElMessage.error(error.message || '创建会话失败')
  }
}

function handleSelectSession(session: ChatSession) {
  chatStore.setCurrentSession(session)
}

async function handleSessionCommand(command: string, session: ChatSession) {
  switch (command) {
    case 'rename':
      // TODO: 实现重命名
      ElMessage.info('重命名功能开发中')
      break
    case 'export':
      // TODO: 实现导出
      ElMessage.info('导出功能开发中')
      break
    case 'delete':
      try {
        await chatStore.deleteSession(session.id)
        ElMessage.success('删除成功')
      } catch (error: any) {
        ElMessage.error(error.message || '删除失败')
      }
      break
  }
}

async function handleSend() {
  if (!inputMessage.value.trim() || sending.value) return

  const message = inputMessage.value.trim()
  inputMessage.value = ''
  sending.value = true

  try {
    await chatStore.sendMessage({
      message,
      sessionId: currentSessionId.value || undefined,
      stream: false
    })
    await nextTick()
    scrollToBottom()
  } catch (error: any) {
    ElMessage.error(error.message || '发送失败')
  } finally {
    sending.value = false
  }
}

function handleQuickQuestion(question: string) {
  inputMessage.value = question
  handleSend()
}

function handleUpload(file: File) {
  ElMessage.info('文件上传功能开发中')
  return false
}

function handleCopy(content: string) {
  navigator.clipboard.writeText(content)
  ElMessage.success('已复制到剪贴板')
}

function handleCreateDocument(message: any) {
  ElMessage.info('生成文书功能开发中')
}

function formatMessage(content: string) {
  // 简单的 markdown 渲染
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

function formatTime(date: string) {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}

function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

onMounted(() => {
  chatStore.fetchSessions()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.chat-container {
  display: flex;
  height: calc(100vh - #{$header-height} - #{$footer-height} - #{$spacing-md * 2});
  background: $bg-color;
  border-radius: $border-radius;
  overflow: hidden;
}

.session-list {
  width: 280px;
  border-right: 1px solid $border-lighter;
  display: flex;
  flex-direction: column;

  .session-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-md;
    border-bottom: 1px solid $border-lighter;

    h3 {
      margin: 0;
      font-size: $font-size-md;
    }
  }

  .session-search {
    padding: $spacing-sm $spacing-md;
  }

  .sessions {
    flex: 1;
    overflow-y: auto;
  }

  .session-item {
    display: flex;
    align-items: center;
    padding: $spacing-md;
    cursor: pointer;
    transition: background-color $transition-timing;

    &:hover {
      background-color: $bg-hover;
    }

    &.active {
      background-color: rgba($primary-color, 0.1);
    }

    .session-content {
      flex: 1;
      overflow: hidden;

      .session-title {
        font-size: $font-size-base;
        color: $text-primary;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .session-time {
        font-size: $font-size-xs;
        color: $text-placeholder;
        margin-top: 4px;
      }
    }

    .session-more {
      color: $text-placeholder;
      cursor: pointer;
      padding: 4px;
      border-radius: $border-radius-small;

      &:hover {
        background-color: $bg-hover;
        color: $text-regular;
      }
    }
  }
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;

  .message-list {
    flex: 1;
    overflow-y: auto;
    padding: $spacing-lg;

    .empty-chat {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: $text-secondary;

      h3 {
        margin: $spacing-md 0;
        color: $text-primary;
      }

      .quick-questions {
        display: flex;
        flex-wrap: wrap;
        gap: $spacing-sm;
        margin-top: $spacing-lg;

        .quick-tag {
          cursor: pointer;
          transition: all $transition-timing;

          &:hover {
            background-color: $primary-color;
            color: #fff;
          }
        }
      }
    }

    .message-item {
      display: flex;
      margin-bottom: $spacing-lg;

      &.user {
        flex-direction: row-reverse;

        .message-content {
          align-items: flex-end;
        }

        .message-text {
          background-color: $primary-color;
          color: #fff;
        }
      }

      .message-avatar {
        flex-shrink: 0;
        margin: 0 $spacing-md;

        .ai-avatar {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
      }

      .message-content {
        display: flex;
        flex-direction: column;
        max-width: 70%;

        .message-header {
          display: flex;
          align-items: center;
          gap: $spacing-sm;
          margin-bottom: 4px;

          .message-name {
            font-size: $font-size-sm;
            color: $text-regular;
          }

          .message-time {
            font-size: $font-size-xs;
            color: $text-placeholder;
          }
        }

        .message-text {
          padding: $spacing-md;
          border-radius: $border-radius;
          background-color: $bg-page;
          line-height: 1.6;
          word-break: break-word;
        }

        .references {
          margin-top: $spacing-sm;
          padding: $spacing-sm;
          background: rgba($primary-color, 0.05);
          border-radius: $border-radius;
          font-size: $font-size-sm;

          .references-title {
            font-weight: 500;
            color: $text-regular;
            margin-bottom: 4px;
          }

          .reference-item {
            display: flex;
            align-items: center;
            gap: 4px;
            color: $primary-color;
            cursor: pointer;

            &:hover {
              text-decoration: underline;
            }
          }
        }

        .message-actions {
          margin-top: $spacing-sm;
          display: flex;
          gap: $spacing-sm;
        }
      }
    }

    .typing-indicator {
      display: flex;
      gap: 4px;
      padding: $spacing-md;

      span {
        width: 8px;
        height: 8px;
        background-color: $text-placeholder;
        border-radius: 50%;
        animation: typing 1.4s infinite both;

        &:nth-child(2) {
          animation-delay: 0.2s;
        }

        &:nth-child(3) {
          animation-delay: 0.4s;
        }
      }
    }
  }

  .input-area {
    border-top: 1px solid $border-lighter;
    padding: $spacing-md;

    .input-tools {
      display: flex;
      gap: $spacing-sm;
      margin-bottom: $spacing-sm;
    }

    .input-wrapper {
      display: flex;
      gap: $spacing-md;

      .el-textarea {
        flex: 1;
      }
    }

    .input-hint {
      font-size: $font-size-xs;
      color: $text-placeholder;
      margin-top: $spacing-xs;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}
</style>
