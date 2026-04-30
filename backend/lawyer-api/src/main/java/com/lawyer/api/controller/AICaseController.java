package com.lawyer.api.controller;

import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.common.dto.ai.CaseAnalysisResponse;
import com.lawyer.common.dto.ai.CasePredictionResponse;
import com.lawyer.service.ai.service.AICaseAnalysisService;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * AI案件分析控制器
 */
@Tag(name = "AI案件分析", description = "AI案件分析接口")
@RestController
@RequestMapping("/api/ai/cases")
@RequiredArgsConstructor
public class AICaseController {

    private final AICaseAnalysisService aiCaseAnalysisService;
    private final UserMapper userMapper;

    /**
     * 案件全面分析
     */
    @Operation(summary = "案件全面分析", description = "AI对案件进行全面分析，包括优势、风险、策略")
    @PostMapping("/analyze/{caseId}")
    public Result<CaseAnalysisResponse> fullAnalysis(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        CaseAnalysisResponse response = aiCaseAnalysisService.fullAnalysis(caseId);
        return Result.success(response);
    }

    /**
     * 案件风险分析
     */
    @Operation(summary = "案件风险分析", description = "AI分析案件风险点")
    @PostMapping("/risk/{caseId}")
    public Result<CaseAnalysisResponse> riskAnalysis(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        CaseAnalysisResponse response = aiCaseAnalysisService.riskAnalysis(caseId);
        return Result.success(response);
    }

    /**
     * 案件策略建议
     */
    @Operation(summary = "案件策略建议", description = "AI提供案件策略建议")
    @PostMapping("/strategy/{caseId}")
    public Result<CaseAnalysisResponse> strategyAnalysis(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        CaseAnalysisResponse response = aiCaseAnalysisService.strategyAnalysis(caseId);
        return Result.success(response);
    }

    /**
     * 胜诉概率预测
     */
    @Operation(summary = "胜诉概率预测", description = "AI预测案件胜诉概率")
    @PostMapping("/predict/{caseId}")
    public Result<CasePredictionResponse> predictWinProbability(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        CasePredictionResponse response = aiCaseAnalysisService.predictWinProbability(caseId);
        return Result.success(response);
    }

    /**
     * 自定义案情预测
     */
    @Operation(summary = "自定义案情预测", description = "根据自定义案情预测胜诉概率")
    @PostMapping("/predict")
    public Result<CasePredictionResponse> predictByDescription(
            @Parameter(description = "案情描述") @RequestParam String caseDescription,
            @Parameter(description = "案件类型") @RequestParam(required = false) String caseType,
            @Parameter(description = "原告类型(employee/employer)") @RequestParam(required = false) String plaintiffType) {
        CasePredictionResponse response = aiCaseAnalysisService.predictByDescription(
                caseDescription, caseType, plaintiffType);
        return Result.success(response);
    }

    /**
     * 获取案件类型列表
     */
    @Operation(summary = "获取案件类型", description = "获取AI支持的案件类型列表")
    @GetMapping("/types")
    public Result<List<Map<String, Object>>> getCaseTypes() {
        List<Map<String, Object>> types = aiCaseAnalysisService.getCaseTypes();
        return Result.success(types);
    }
}
