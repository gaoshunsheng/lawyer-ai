package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 胜诉预测请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CasePredictionRequest {

    /**
     * 案情描述
     */
    private String caseDescription;

    /**
     * 案件类型
     */
    private String caseType;

    /**
     * 原告类型：employee-劳动者, employer-用人单位
     */
    private String plaintiffType;
}
