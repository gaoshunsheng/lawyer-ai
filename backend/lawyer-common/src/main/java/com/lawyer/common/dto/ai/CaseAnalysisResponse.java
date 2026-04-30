package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 案件分析响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CaseAnalysisResponse {

    /**
     * 案件ID
     */
    private Long caseId;

    /**
     * 案件摘要
     */
    private String summary;

    /**
     * 优势点
     */
    private List<Map<String, Object>> advantages;

    /**
     * 风险点
     */
    private List<Map<String, Object>> risks;

    /**
     * 策略建议
     */
    private List<Map<String, Object>> strategies;

    /**
     * 类似案例
     */
    private List<Map<String, Object>> similarCases;

    /**
     * 胜诉概率
     */
    private Double winProbability;

    /**
     * 法律依据
     */
    private List<Map<String, Object>> legalBasis;
}
