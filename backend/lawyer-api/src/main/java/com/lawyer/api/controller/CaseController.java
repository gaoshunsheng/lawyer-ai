package com.lawyer.api.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.lawyer.common.annotation.Log;
import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.log.entity.OperationLog;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.cases.*;
import com.lawyer.service.cases.service.CaseService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * 案件管理控制器
 */
@Tag(name = "案件管理", description = "案件信息的增删改查接口")
@RestController
@RequestMapping("/api/cases")
@RequiredArgsConstructor
public class CaseController {

    private final CaseService caseService;
    private final UserMapper userMapper;

    /**
     * 创建案件
     */
    @Operation(summary = "创建案件", description = "创建新的案件")
    @Log(operationType = Log.OperationType.CREATE, description = "创建案件")
    @PostMapping
    public Result<CaseInfo> createCase(@Valid @RequestBody CaseCreateRequest request) {
        CaseInfo caseInfo = caseService.createCase(request);
        return Result.success(caseInfo);
    }

    /**
     * 更新案件
     */
    @Operation(summary = "更新案件", description = "更新案件信息")
    @Log(operationType = Log.OperationType.UPDATE, description = "更新案件")
    @PutMapping("/{id}")
    public Result<CaseInfo> updateCase(
            @Parameter(description = "案件ID") @PathVariable Long id,
            @Valid @RequestBody CaseUpdateRequest request) {
        CaseInfo caseInfo = caseService.updateCase(id, request);
        return Result.success(caseInfo);
    }

    /**
     * 获取案件详情
     */
    @Operation(summary = "获取案件详情", description = "根据ID获取案件详细信息")
    @Log(operationType = Log.OperationType.VIEW, description = "查看案件详情")
    @GetMapping("/{id}")
    public Result<CaseInfo> getCaseById(@Parameter(description = "案件ID") @PathVariable Long id) {
        CaseInfo caseInfo = caseService.getCaseById(id);
        return Result.success(caseInfo);
    }

    /**
     * 删除案件
     */
    @Operation(summary = "删除案件", description = "软删除案件")
    @Log(operationType = Log.OperationType.DELETE, description = "删除案件")
    @DeleteMapping("/{id}")
    public Result<Void> deleteCase(@Parameter(description = "案件ID") @PathVariable Long id) {
        caseService.deleteCase(id);
        return Result.success();
    }

    /**
     * 查询案件列表
     */
    @Operation(summary = "查询案件列表", description = "根据条件分页查询案件列表")
    @GetMapping
    public Result<IPage<CaseInfo>> queryCases(CaseQueryRequest request) {
        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }
        IPage<CaseInfo> page = caseService.queryCases(request, tenantId);
        return Result.success(page);
    }

    /**
     * 获取案件统计
     */
    @Operation(summary = "获取案件统计", description = "获取案件统计数据")
    @GetMapping("/statistics")
    public Result<CaseStatistics> getStatistics() {
        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }
        CaseStatistics stats = caseService.getStatistics(tenantId);
        return Result.success(stats);
    }
}
