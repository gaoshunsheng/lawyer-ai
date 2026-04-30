package com.lawyer.common.dto.calculator;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;

/**
 * 加班费计算请求DTO
 */
@Data
public class OvertimePayRequest {

    /**
     * 月工资标准
     */
    @NotNull(message = "月工资不能为空")
    @Min(value = 0, message = "月工资不能为负数")
    private BigDecimal monthlySalary;

    /**
     * 工作日加班小时数
     */
    @Min(value = 0, message = "加班小时数不能为负数")
    private BigDecimal workdayHours = BigDecimal.ZERO;

    /**
     * 休息日加班小时数
     */
    @Min(value = 0, message = "加班小时数不能为负数")
    private BigDecimal weekendHours = BigDecimal.ZERO;

    /**
     * 法定节假日加班小时数
     */
    @Min(value = 0, message = "加班小时数不能为负数")
    private BigDecimal holidayHours = BigDecimal.ZERO;

    /**
     * 每月工作天数（默认21.75天）
     */
    private BigDecimal workDaysPerMonth = new BigDecimal("21.75");

    /**
     * 每天工作小时数（默认8小时）
     */
    private BigDecimal workHoursPerDay = new BigDecimal("8");

    /**
     * 是否已安排补休（仅休息日）
     */
    private Boolean hasCompensatoryLeave = false;
}
