package com.lawyer.common.dto.statistics;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 系统统计概览DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SystemStatistics {

    /**
     * 案件统计
     */
    private CaseStatistics caseStatistics;

    /**
     * 文书统计
     */
    private DocumentStatistics documentStatistics;

    /**
     * 用户统计
     */
    private UserStatistics userStatistics;

    /**
     * 知识库统计
     */
    private KnowledgeStatistics knowledgeStatistics;

    /**
     * 案件统计
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CaseStatistics {
        private Long totalCases;
        private Long ongoingCases;
        private Long closedCases;
        private Long thisMonthNewCases;
        private Long thisWeekNewCases;
        private BigDecimal totalClaimAmount;
        private BigDecimal thisMonthClaimAmount;
        private Map<String, Long> caseTypeDistribution;
        private Map<String, Long> caseStatusDistribution;
        private List<TrendData> monthlyTrend;
    }

    /**
     * 文书统计
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DocumentStatistics {
        private Long totalDocuments;
        private Long draftDocuments;
        private Long reviewDocuments;
        private Long finalDocuments;
        private Long thisMonthCreated;
        private Map<String, Long> docTypeDistribution;
        private List<TrendData> monthlyTrend;
    }

    /**
     * 用户统计
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserStatistics {
        private Long totalUsers;
        private Long activeUsers;
        private Long thisMonthActive;
        private Map<String, Long> roleDistribution;
    }

    /**
     * 知识库统计
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class KnowledgeStatistics {
        private Long totalKnowledge;
        private Long lawCount;
        private Long caseCount;
        private Long internalCount;
        private Long thisMonthViewed;
        private Map<String, Long> categoryDistribution;
    }

    /**
     * 趋势数据
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TrendData {
        private String date;
        private Long count;
        private BigDecimal amount;
    }
}
