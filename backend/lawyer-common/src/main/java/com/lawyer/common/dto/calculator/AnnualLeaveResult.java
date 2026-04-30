package com.lawyer.common.dto.calculator;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

/**
 * 年休假工资计算结果DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnnualLeaveResult {

    /**
     * 日工资
     */
    private BigDecimal dailyRate;

    /**
     * 累计工作年限
     */
    private BigDecimal totalWorkYears;

    /**
     * 应休年休假天数
     */
    private Integer entitledDays;

    /**
     * 应休天数说明
     */
    private String entitledDaysDescription;

    /**
     * 已休年休假天数
     */
    private BigDecimal usedDays;

    /**
     * 未休年休假天数
     */
    private BigDecimal unusedDays;

    /**
     * 未休年休假工资
     */
    private BigDecimal unpaidWages;

    /**
     * 计算倍率
     */
    private Integer multiplier;

    /**
     * 计算步骤
     */
    private List<CalculationResult.CalculationStep> steps;

    /**
     * 法律依据
     */
    private List<CalculationResult.LegalBasis> legalBasis;

    /**
     * 注意事项
     */
    private List<String> notes;
}
