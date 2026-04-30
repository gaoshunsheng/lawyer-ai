package com.lawyer.common.dto.statistics;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 案件统计报告DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CaseReport {

    /**
     * 报告标题
     */
    private String title;

    /**
     * 报告时间范围
     */
    private String timeRange;

    /**
     * 案件总数
     */
    private Long totalCases;

    /**
     * 新增案件数
     */
    private Long newCases;

    /**
     * 结案数
     */
    private Long closedCases;

    /**
     * 总标的金额
     */
    private BigDecimal totalClaimAmount;

    /**
     * 各类型案件数量
     */
    private Map<String, Long> caseTypeCount;

    /**
     * 各状态案件数量
     */
    private Map<String, Long> caseStatusCount;

    /**
     * 各律师办案数量
     */
    private List<LawyerCaseCount> lawyerCaseCounts;

    /**
     * 月度趋势
     */
    private List<MonthlyData> monthlyTrends;

    /**
     * 律师办案数量
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LawyerCaseCount {
        private Long lawyerId;
        private String lawyerName;
        private Long caseCount;
        private BigDecimal totalClaimAmount;
    }

    /**
     * 月度数据
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MonthlyData {
        private String month;
        private Long newCases;
        private Long closedCases;
        private BigDecimal claimAmount;
    }
}
