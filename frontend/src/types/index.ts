// 通用类型
export interface Result<T = any> {
  code: number
  message: string
  data: T
}

export interface PageResult<T = any> {
  records: T[]
  total: number
  size: number
  current: number
  pages: number
}

export interface Pagination {
  page: number
  pageSize: number
}

// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  phone: string
  realName: string
  role: string
  status: number
  avatar?: string
  tenantId?: number
  createdAt: string
  updatedAt: string
}

export interface LoginForm {
  username: string
  password: string
  rememberMe?: boolean
}

export interface LoginResult {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
  username: string
  realName: string
  role: string
}

// 案件相关类型
export type CaseStatus = 'PENDING' | 'ARBITRATION' | 'FIRST_INSTANCE' | 'SECOND_INSTANCE' | 'EXECUTION' | 'CLOSED' | 'CANCELLED'
export type CaseType = 'LABOR_DISPUTE' | 'WORK_INJURY' | 'SOCIAL_INSURANCE' | 'OTHER'

export interface Case {
  id: number
  caseNumber: string
  caseType: CaseType
  caseStatus: CaseStatus
  plaintiff: Record<string, any>
  defendant: Record<string, any>
  claimAmount: number
  disputeFocus: string[]
  description: string
  lawyerId: number
  lawyerName: string
  timeline: TimelineEvent[]
  createdAt: string
  updatedAt: string
}

export interface TimelineEvent {
  id: number
  caseId: number
  eventType: string
  title: string
  description: string
  eventTime: string
  attachments: string[]
}

// 文书相关类型
export type DocumentStatus = 'DRAFT' | 'REVIEW' | 'FINAL'

export interface Document {
  id: number
  caseId: number
  title: string
  docType: string
  content: string
  status: DocumentStatus
  version: number
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface DocumentTemplate {
  id: number
  name: string
  docType: string
  description: string
  content: string
  variables: string[]
}

// AI相关类型
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

export interface ChatRequest {
  message: string
  sessionId?: string
  context?: Record<string, any>
}

export interface ChatResponse {
  sessionId: string
  reply: string
  sources?: SourceInfo[]
  suggestedQuestions?: string[]
}

export interface SourceInfo {
  type: string
  title: string
  score: number
}

export interface DocumentGenerateRequest {
  templateId: string
  caseId?: number
  variables: Record<string, any>
  style?: string
}

export interface CaseAnalysis {
  caseId: number
  summary: string
  advantages: any[]
  risks: any[]
  strategies: any[]
  winProbability: number
  legalBasis: any[]
}

// 统计相关类型
export interface Statistics {
  caseStatistics: CaseStatistics
  documentStatistics: DocumentStatistics
  userStatistics: UserStatistics
}

export interface CaseStatistics {
  totalCases: number
  ongoingCases: number
  closedCases: number
  thisMonthNewCases: number
  thisWeekNewCases: number
  totalClaimAmount: number
  thisMonthClaimAmount: number
  caseTypeDistribution: Record<string, number>
  caseStatusDistribution: Record<string, number>
  monthlyTrend: TrendData[]
}

export interface DocumentStatistics {
  totalDocuments: number
  draftDocuments: number
  reviewDocuments: number
  finalDocuments: number
  thisMonthCreated: number
  docTypeDistribution: Record<string, number>
  monthlyTrend: TrendData[]
}

export interface UserStatistics {
  totalUsers: number
  activeUsers: number
  thisMonthActive: number
  roleDistribution: Record<string, number>
}

export interface TrendData {
  date: string
  count: number
  amount: number
}
