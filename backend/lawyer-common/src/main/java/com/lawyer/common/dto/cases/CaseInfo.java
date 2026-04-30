package com.lawyer.common.dto.cases;

import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 案件信息响应DTO
 */
@Data
public class CaseInfo {

    private Long id;

    private String caseNumber;

    private CaseType caseType;

    private String caseTypeName;

    private CaseStatus caseStatus;

    private String caseStatusName;

    private String title;

    /**
     * 原告信息
     */
    private CaseCreateRequest.PartyInfo plaintiff;

    /**
     * 被告信息
     */
    private CaseCreateRequest.PartyInfo defendant;

    /**
     * 标的金额
     */
    private BigDecimal claimAmount;

    /**
     * 争议焦点
     */
    private List<String> disputeFocus;

    /**
     * 承办律师ID
     */
    private Long lawyerId;

    /**
     * 承办律师姓名
     */
    private String lawyerName;

    /**
     * 助理律师ID
     */
    private Long assistantId;

    /**
     * 助理律师姓名
     */
    private String assistantName;

    /**
     * 租户ID
     */
    private Long tenantId;

    /**
     * 案件描述
     */
    private String description;

    /**
     * 时间线JSON
     */
    private String timeline;

    /**
     * AI分析结果
     */
    private String aiAnalysis;

    /**
     * 立案日期
     */
    private LocalDate filedDate;

    /**
     * 结案日期
     */
    private LocalDate closedDate;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    private LocalDateTime updatedAt;
}
