package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 案件分析请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CaseAnalysisRequest {

    /**
     * 案件ID
     */
    private Long caseId;

    /**
     * 分析类型：full-全面分析, risk-风险分析, strategy-策略建议
     */
    private String analysisType;
}
