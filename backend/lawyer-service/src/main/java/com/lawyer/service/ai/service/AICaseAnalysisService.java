package com.lawyer.service.ai.service;

import com.lawyer.common.dto.ai.*;
import com.lawyer.common.client.AIServiceClient;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AI案件分析服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AICaseAnalysisService {

    private final AIServiceClient aiServiceClient;
    private final CaseMapper caseMapper;

    /**
     * 案件全面分析
     *
     * @param caseId 案件ID
     * @return 分析结果
     */
    public CaseAnalysisResponse fullAnalysis(Long caseId) {
        CaseAnalysisRequest request = CaseAnalysisRequest.builder()
                .caseId(caseId)
                .analysisType("full")
                .build();

        return aiServiceClient.analyzeCase(request);
    }

    /**
     * 案件风险分析
     *
     * @param caseId 案件ID
     * @return 分析结果
     */
    public CaseAnalysisResponse riskAnalysis(Long caseId) {
        CaseAnalysisRequest request = CaseAnalysisRequest.builder()
                .caseId(caseId)
                .analysisType("risk")
                .build();

        return aiServiceClient.analyzeCase(request);
    }

    /**
     * 案件策略建议
     *
     * @param caseId 案件ID
     * @return 分析结果
     */
    public CaseAnalysisResponse strategyAnalysis(Long caseId) {
        CaseAnalysisRequest request = CaseAnalysisRequest.builder()
                .caseId(caseId)
                .analysisType("strategy")
                .build();

        return aiServiceClient.analyzeCase(request);
    }

    /**
     * 胜诉预测
     *
     * @param caseId 案件ID
     * @return 预测结果
     */
    public CasePredictionResponse predictWinProbability(Long caseId) {
        Case caseEntity = caseMapper.selectById(caseId);
        if (caseEntity == null) {
            return null;
        }

        // 构建案情描述
        String caseDescription = buildCaseDescription(caseEntity);
        String caseType = caseEntity.getCaseType() != null ? caseEntity.getCaseType().getCode() : null;
        String plaintiffType = determinePlaintiffType(caseEntity);

        CasePredictionRequest request = CasePredictionRequest.builder()
                .caseDescription(caseDescription)
                .caseType(caseType)
                .plaintiffType(plaintiffType)
                .build();

        return aiServiceClient.predictCase(request);
    }

    /**
     * 自定义案情预测
     *
     * @param caseDescription 案情描述
     * @param caseType        案件类型
     * @param plaintiffType   原告类型
     * @return 预测结果
     */
    public CasePredictionResponse predictByDescription(String caseDescription, String caseType, String plaintiffType) {
        CasePredictionRequest request = CasePredictionRequest.builder()
                .caseDescription(caseDescription)
                .caseType(caseType)
                .plaintiffType(plaintiffType)
                .build();

        return aiServiceClient.predictCase(request);
    }

    /**
     * 获取案件类型列表
     *
     * @return 案件类型列表
     */
    public List<Map<String, Object>> getCaseTypes() {
        return aiServiceClient.getCaseTypes();
    }

    /**
     * 构建案情描述
     */
    private String buildCaseDescription(Case caseEntity) {
        StringBuilder sb = new StringBuilder();

        sb.append("案件类型：").append(caseEntity.getCaseType() != null ? caseEntity.getCaseType().getName() : "未知").append("；");
        sb.append("案件状态：").append(caseEntity.getCaseStatus() != null ? caseEntity.getCaseStatus().getName() : "未知").append("；");

        if (caseEntity.getClaimAmount() != null) {
            sb.append("标的金额：").append(caseEntity.getClaimAmount()).append("元；");
        }

        if (caseEntity.getDescription() != null) {
            sb.append("案情简介：").append(caseEntity.getDescription()).append("；");
        }

        // 当事人信息
        if (caseEntity.getPlaintiff() != null) {
            sb.append("申请人/原告：").append(caseEntity.getPlaintiff().get("name")).append("；");
        }
        if (caseEntity.getDefendant() != null) {
            sb.append("被申请人/被告：").append(caseEntity.getDefendant().get("name")).append("；");
        }

        return sb.toString();
    }

    /**
     * 判断原告类型
     */
    private String determinePlaintiffType(Case caseEntity) {
        // 根据案件信息判断原告是劳动者还是用人单位
        // 这里简单处理，实际应根据具体业务逻辑判断
        if (caseEntity.getPlaintiff() != null) {
            String plaintiffRole = (String) caseEntity.getPlaintiff().get("role");
            if ("employee".equals(plaintiffRole)) {
                return "employee";
            } else if ("employer".equals(plaintiffRole)) {
                return "employer";
            }
        }
        return "employee"; // 默认劳动者
    }
}
