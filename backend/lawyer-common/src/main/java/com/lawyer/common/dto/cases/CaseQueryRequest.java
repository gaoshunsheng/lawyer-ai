package com.lawyer.common.dto.cases;

import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import lombok.Data;

import java.math.BigDecimal;

/**
 * 案件查询条件DTO
 */
@Data
public class CaseQueryRequest {

    /**
     * 页码
     */
    private Integer page = 1;

    /**
     * 每页数量
     */
    private Integer pageSize = 20;

    /**
     * 关键词搜索（标题、案号）
     */
    private String keyword;

    /**
     * 案件类型
     */
    private CaseType caseType;

    /**
     * 案件状态
     */
    private CaseStatus caseStatus;

    /**
     * 承办律师ID
     */
    private Long lawyerId;

    /**
     * 标的金额下限
     */
    private BigDecimal claimAmountMin;

    /**
     * 标的金额上限
     */
    private BigDecimal claimAmountMax;

    /**
     * 排序字段
     */
    private String sortBy = "createdAt";

    /**
     * 排序方向
     */
    private String sortOrder = "desc";
}
