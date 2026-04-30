package com.lawyer.api.controller;

import com.lawyer.common.result.Result;
import com.lawyer.common.dto.cases.EvidenceCreateRequest;
import com.lawyer.common.dto.cases.EvidenceInfo;
import com.lawyer.service.cases.service.EvidenceService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 证据管理控制器
 */
@Tag(name = "证据管理", description = "证据的增删改查接口")
@RestController
@RequestMapping("/api/evidences")
@RequiredArgsConstructor
public class EvidenceController {

    private final EvidenceService evidenceService;

    /**
     * 创建证据
     */
    @Operation(summary = "创建证据", description = "上传新的证据")
    @PostMapping
    public Result<EvidenceInfo> createEvidence(@Valid @RequestBody EvidenceCreateRequest request) {
        EvidenceInfo evidence = evidenceService.createEvidence(request);
        return Result.success(evidence);
    }

    /**
     * 更新证据
     */
    @Operation(summary = "更新证据", description = "更新证据信息")
    @PutMapping("/{id}")
    public Result<EvidenceInfo> updateEvidence(
            @Parameter(description = "证据ID") @PathVariable Long id,
            @Valid @RequestBody EvidenceCreateRequest request) {
        EvidenceInfo evidence = evidenceService.updateEvidence(id, request);
        return Result.success(evidence);
    }

    /**
     * 获取证据详情
     */
    @Operation(summary = "获取证据详情", description = "根据ID获取证据详细信息")
    @GetMapping("/{id}")
    public Result<EvidenceInfo> getEvidenceById(@Parameter(description = "证据ID") @PathVariable Long id) {
        EvidenceInfo evidence = evidenceService.getEvidenceById(id);
        return Result.success(evidence);
    }

    /**
     * 获取案件的证据列表
     */
    @Operation(summary = "获取案件的证据列表", description = "根据案件ID获取所有证据")
    @GetMapping("/case/{caseId}")
    public Result<List<EvidenceInfo>> getEvidencesByCaseId(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        List<EvidenceInfo> evidences = evidenceService.getEvidencesByCaseId(caseId);
        return Result.success(evidences);
    }

    /**
     * 删除证据
     */
    @Operation(summary = "删除证据", description = "软删除证据")
    @DeleteMapping("/{id}")
    public Result<Void> deleteEvidence(@Parameter(description = "证据ID") @PathVariable Long id) {
        evidenceService.deleteEvidence(id);
        return Result.success();
    }
}
