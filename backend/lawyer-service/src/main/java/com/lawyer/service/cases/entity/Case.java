package com.lawyer.service.cases.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.lawyer.common.entity.BaseEntity;
import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/**
 * 案件实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName(value = "cases", autoResultMap = true)
public class Case extends BaseEntity {

    /**
     * 案号
     */
    private String caseNumber;

    /**
     * 案件类型
     */
    private CaseType caseType;

    /**
     * 案件状态
     */
    private CaseStatus caseStatus;

    /**
     * 案件标题
     */
    private String title;

    /**
     * 原告信息JSON
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private String plaintiff;

    /**
     * 被告信息JSON
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private String defendant;

    /**
     * 标的金额
     */
    private BigDecimal claimAmount;

    /**
     * 争议焦点
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private List<String> disputeFocus;

    /**
     * 承办律师ID
     */
    private Long lawyerId;

    /**
     * 助理律师ID
     */
    private Long assistantId;

    /**
     * 租户ID
     */
    private Long tenantId;

    /**
     * 时间线JSON
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private String timeline;

    /**
     * AI分析结果JSON
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private String aiAnalysis;

    /**
     * 案件描述
     */
    private String description;

    /**
     * 立案日期
     */
    private LocalDate filedDate;

    /**
     * 结案日期
     */
    private LocalDate closedDate;
}
