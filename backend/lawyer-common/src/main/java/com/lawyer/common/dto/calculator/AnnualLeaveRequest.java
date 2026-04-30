package com.lawyer.common.dto.calculator;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;

/**
 * 年休假工资计算请求DTO
 */
@Data
public class AnnualLeaveRequest {

    /**
     * 月工资标准
     */
    @NotNull(message = "月工资不能为空")
    @DecimalMin(value = "0", message = "月工资不能为负数")
    private BigDecimal monthlySalary;

    /**
     * 累计工作年限
     */
    @NotNull(message = "累计工作年限不能为空")
    @DecimalMin(value = "0", message = "工作年限不能为负数")
    private BigDecimal totalWorkYears;

    /**
     * 未休年休假天数
     */
    @NotNull(message = "未休年休假天数不能为空")
    @DecimalMin(value = "0", message = "未休天数不能为负数")
    private BigDecimal unusedDays;

    /**
     * 已休年休假天数
     */
    @DecimalMin(value = "0", message = "已休天数不能为负数")
    private BigDecimal usedDays = BigDecimal.ZERO;

    /**
     * 每月工作天数（默认21.75天）
     */
    private BigDecimal workDaysPerMonth = new BigDecimal("21.75");

    /**
     * 是否因个人原因不休年假
     */
    private Boolean personalReason = false;
}
