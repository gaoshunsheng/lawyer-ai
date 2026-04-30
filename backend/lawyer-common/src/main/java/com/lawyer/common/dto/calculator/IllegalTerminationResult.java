package com.lawyer.common.dto.calculator;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

/**
 * 违法解除赔偿计算结果DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IllegalTerminationResult {

    /**
     * 输入参数
     */
    private IllegalTerminationInput input;

    /**
     * 工作年限
     */
    private BigDecimal workYears;

    /**
     * 工作年限计算说明
     */
    private String workYearsDescription;

    /**
     * 计算基数
     */
    private BigDecimal calculationBase;

    /**
     * 是否适用高薪封顶
     */
    private Boolean isHighSalaryCapped;

    /**
     * 社平工资（三倍）
     */
    private BigDecimal socialAverageSalaryTriple;

    /**
     * 经济补偿金
     */
    private BigDecimal severancePay;

    /**
     * 赔偿金倍数
     */
    private Integer multiplier;

    /**
     * 赔偿金总额
     */
    private BigDecimal totalCompensation;

    /**
     * 已支付金额
     */
    private BigDecimal paidAmount;

    /**
     * 应补发金额
     */
    private BigDecimal unpaidAmount;

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

    /**
     * 输入参数
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IllegalTerminationInput {
        private String entryDate;
        private String leaveDate;
        private BigDecimal monthlySalary;
        private BigDecimal averageSalary12m;
        private String city;
        private Boolean highSalaryCap;
        private Boolean isNegotiated;
    }
}
