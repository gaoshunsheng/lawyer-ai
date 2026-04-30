package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 胜诉预测响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CasePredictionResponse {

    /**
     * 胜诉概率
     */
    private Double probability;

    /**
     * 置信度
     */
    private Double confidence;

    /**
     * 影响因素
     */
    private List<Map<String, Object>> factors;

    /**
     * 类似案例
     */
    private List<Map<String, Object>> similarCases;

    /**
     * 建议
     */
    private List<String> recommendations;
}
