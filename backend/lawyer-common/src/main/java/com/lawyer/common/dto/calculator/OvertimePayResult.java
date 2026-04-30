package com.lawyer.common.dto.calculator;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

/**
 * 加班费计算结果DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OvertimePayResult {

    /**
     * 小时工资
     */
    private BigDecimal hourlyRate;

    /**
     * 工作日加班费
     */
    private OvertimePayDetail workdayOvertime;

    /**
     * 休息日加班费
     */
    private OvertimePayDetail weekendOvertime;

    /**
     * 法定节假日加班费
     */
    private OvertimePayDetail holidayOvertime;

    /**
     * 加班费总额
     */
    private BigDecimal totalOvertimePay;

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
     * 加班费明细
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OvertimePayDetail {
        /**
         * 加班小时数
         */
        private BigDecimal hours;

        /**
         * 计算倍率
         */
        private BigDecimal rate;

        /**
         * 倍率说明
         */
        private String rateDescription;

        /**
         * 金额
         */
        private BigDecimal amount;
    }
}
