package com.lawyer.common.dto.calculator;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

/**
 * 计算结果响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CalculationResult {

    /**
     * 计算类型
     */
    private String calculationType;

    /**
     * 输入参数摘要
     */
    private String inputSummary;

    /**
     * 计算总金额
     */
    private BigDecimal totalAmount;

    /**
     * 计算步骤
     */
    private List<CalculationStep> steps;

    /**
     * 法律依据
     */
    private List<LegalBasis> legalBasis;

    /**
     * 注意事项
     */
    private List<String> notes;

    /**
     * 计算步骤
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CalculationStep {
        private Integer order;
        private String title;
        private String description;
        private String formula;
        private BigDecimal amount;
        private String unit;
    }

    /**
     * 法律依据
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LegalBasis {
        private String lawName;
        private String articleNumber;
        private String content;
    }
}
