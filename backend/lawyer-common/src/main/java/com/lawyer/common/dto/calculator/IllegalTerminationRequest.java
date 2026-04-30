package com.lawyer.common.dto.calculator;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Map;

/**
 * 违法解除赔偿计算请求DTO
 */
@Data
public class IllegalTerminationRequest {

    /**
     * 入职日期
     */
    @NotNull(message = "入职日期不能为空")
    private LocalDate entryDate;

    /**
     * 解除日期
     */
    @NotNull(message = "解除日期不能为空")
    private LocalDate leaveDate;

    /**
     * 月工资标准
     */
    @NotNull(message = "月工资不能为空")
    @Min(value = 0, message = "月工资不能为负数")
    private BigDecimal monthlySalary;

    /**
     * 12个月平均工资（可选）
     */
    private BigDecimal averageSalary12m;

    /**
     * 工资构成
     */
    private SalaryComposition salaryComposition;

    /**
     * 所在城市
     */
    private String city;

    /**
     * 是否存在高薪封顶情形
     */
    private Boolean highSalaryCap = false;

    /**
     * 是否协商解除
     */
    private Boolean isNegotiated = false;

    /**
     * 已支付经济补偿金额
     */
    private BigDecimal paidCompensation;

    /**
     * 工资构成
     */
    @Data
    public static class SalaryComposition {
        private BigDecimal baseSalary;
        private BigDecimal performanceBonus;
        private BigDecimal allowance;
        private BigDecimal overtimePay;
        private BigDecimal otherPay;
    }
}
