package com.lawyer.common.dto.cases;

import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/**
 * 更新案件请求DTO
 */
@Data
public class CaseUpdateRequest {

    @Size(max = 200, message = "案件标题长度不能超过200个字符")
    private String title;

    private CaseType caseType;

    private CaseStatus caseStatus;

    private String caseNumber;

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
     * 案件描述
     */
    private String description;

    /**
     * 承办律师ID
     */
    private Long lawyerId;

    /**
     * 助理律师ID
     */
    private Long assistantId;

    /**
     * 结案日期
     */
    private LocalDate closedDate;
}
