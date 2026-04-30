package com.lawyer.common.dto.cases;

import com.lawyer.common.enums.CaseType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/**
 * 创建案件请求DTO
 */
@Data
public class CaseCreateRequest {

    @NotBlank(message = "案件标题不能为空")
    @Size(max = 200, message = "案件标题长度不能超过200个字符")
    private String title;

    @NotNull(message = "案件类型不能为空")
    private CaseType caseType;

    private String caseNumber;

    /**
     * 原告信息
     */
    private PartyInfo plaintiff;

    /**
     * 被告信息
     */
    private PartyInfo defendant;

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
    @NotNull(message = "承办律师不能为空")
    private Long lawyerId;

    /**
     * 助理律师ID
     */
    private Long assistantId;

    /**
     * 立案日期
     */
    private LocalDate filedDate;

    /**
     * 当事人信息
     */
    @Data
    public static class PartyInfo {
        private String name;
        private String type;  // 个人/企业
        private String idNumber;
        private String phone;
        private String address;
        private String legalPerson;  // 法定代表人
        private String contactPerson;  // 联系人
    }
}
