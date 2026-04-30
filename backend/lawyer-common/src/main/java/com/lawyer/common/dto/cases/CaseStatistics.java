package com.lawyer.common.dto.cases;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 案件统计DTO
 */
@Data
public class CaseStatistics {

    /**
     * 总案件数
     */
    private Long totalCases;

    /**
     * 进行中案件数
     */
    private Long ongoingCases;

    /**
     * 已结案案件数
     */
    private Long closedCases;

    /**
     * 本月新增案件数
     */
    private Long monthlyNewCases;

    /**
     * 总标的金额
     */
    private BigDecimal totalClaimAmount;

    /**
     * 按案件类型统计
     */
    private java.util.Map<String, Long> caseTypeDistribution;

    /**
     * 按案件状态统计
     */
    private java.util.Map<String, Long> caseStatusDistribution;
}
