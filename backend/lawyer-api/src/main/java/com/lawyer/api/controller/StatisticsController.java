package com.lawyer.api.controller;

import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.statistics.CaseReport;
import com.lawyer.common.dto.statistics.SystemStatistics;
import com.lawyer.service.statistics.service.StatisticsService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * 统计分析控制器
 */
@Tag(name = "统计分析", description = "系统数据统计和分析接口")
@RestController
@RequestMapping("/api/statistics")
@RequiredArgsConstructor
public class StatisticsController {

    private final StatisticsService statisticsService;
    private final UserMapper userMapper;

    /**
     * 获取系统统计概览
     */
    @Operation(summary = "系统统计概览", description = "获取系统整体统计数据")
    @GetMapping("/overview")
    public Result<SystemStatistics> getOverview() {
        Long tenantId = getCurrentTenantId();
        SystemStatistics statistics = statisticsService.getSystemStatistics(tenantId);
        return Result.success(statistics);
    }

    /**
     * 获取案件统计
     */
    @Operation(summary = "案件统计", description = "获取案件相关统计数据")
    @GetMapping("/cases")
    public Result<SystemStatistics.CaseStatistics> getCaseStatistics() {
        Long tenantId = getCurrentTenantId();
        SystemStatistics.CaseStatistics statistics = statisticsService.getCaseStatistics(tenantId);
        return Result.success(statistics);
    }

    /**
     * 获取文书统计
     */
    @Operation(summary = "文书统计", description = "获取文书相关统计数据")
    @GetMapping("/documents")
    public Result<SystemStatistics.DocumentStatistics> getDocumentStatistics() {
        Long tenantId = getCurrentTenantId();
        SystemStatistics.DocumentStatistics statistics = statisticsService.getDocumentStatistics(tenantId);
        return Result.success(statistics);
    }

    /**
     * 获取用户统计
     */
    @Operation(summary = "用户统计", description = "获取用户相关统计数据")
    @GetMapping("/users")
    public Result<SystemStatistics.UserStatistics> getUserStatistics() {
        Long tenantId = getCurrentTenantId();
        SystemStatistics.UserStatistics statistics = statisticsService.getUserStatistics(tenantId);
        return Result.success(statistics);
    }

    /**
     * 获取知识库统计
     */
    @Operation(summary = "知识库统计", description = "获取知识库相关统计数据")
    @GetMapping("/knowledge")
    public Result<SystemStatistics.KnowledgeStatistics> getKnowledgeStatistics() {
        Long tenantId = getCurrentTenantId();
        SystemStatistics.KnowledgeStatistics statistics = statisticsService.getKnowledgeStatistics(tenantId);
        return Result.success(statistics);
    }

    /**
     * 获取案件报告
     */
    @Operation(summary = "案件报告", description = "获取指定时间范围的案件统计报告")
    @GetMapping("/cases/report")
    public Result<CaseReport> getCaseReport(
            @Parameter(description = "开始日期") @RequestParam(required = false) String startDate,
            @Parameter(description = "结束日期") @RequestParam(required = false) String endDate) {
        Long tenantId = getCurrentTenantId();
        CaseReport report = statisticsService.getCaseReport(tenantId, startDate, endDate);
        return Result.success(report);
    }

    /**
     * 获取当前租户ID
     */
    private Long getCurrentTenantId() {
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                return user.getTenantId();
            }
        }
        return null;
    }
}
