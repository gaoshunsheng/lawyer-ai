package com.lawyer.api.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.lawyer.common.dto.log.OperationLogQuery;
import com.lawyer.common.dto.log.OperationLogStatistics;
import com.lawyer.common.dto.log.OperationLogVO;
import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.log.entity.OperationLog;
import com.lawyer.service.log.service.OperationLogService;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 操作日志控制器
 */
@Tag(name = "操作日志", description = "操作日志管理接口")
@RestController
@RequestMapping("/api/logs")
@RequiredArgsConstructor
public class OperationLogController {

    private final OperationLogService operationLogService;
    private final UserMapper userMapper;

    /**
     * 分页查询操作日志
     */
    @Operation(summary = "查询操作日志", description = "分页查询操作日志列表")
    @GetMapping
    public Result<IPage<OperationLogVO>> queryLogs(
            @Parameter(description = "用户ID") @RequestParam(required = false) Long userId,
            @Parameter(description = "用户名") @RequestParam(required = false) String username,
            @Parameter(description = "操作类型") @RequestParam(required = false) String operationType,
            @Parameter(description = "开始时间") @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTime,
            @Parameter(description = "结束时间") @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTime,
            @Parameter(description = "响应状态") @RequestParam(required = false) Integer responseStatus,
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") Integer page,
            @Parameter(description = "每页大小") @RequestParam(defaultValue = "20") Integer size,
            @Parameter(description = "排序字段") @RequestParam(defaultValue = "createdAt") String sortBy,
            @Parameter(description = "排序方向") @RequestParam(defaultValue = "desc") String sortOrder) {

        OperationLogQuery query = OperationLogQuery.builder()
                .userId(userId)
                .username(username)
                .operationType(operationType)
                .startTime(startTime)
                .endTime(endTime)
                .responseStatus(responseStatus)
                .page(page)
                .size(size)
                .sortBy(sortBy)
                .sortOrder(sortOrder)
                .build();

        Long tenantId = getCurrentTenantId();
        IPage<OperationLogVO> logPage = operationLogService.queryLogs(query, tenantId);
        return Result.success(logPage);
    }

    /**
     * 获取日志详情
     */
    @Operation(summary = "日志详情", description = "获取指定日志的详细信息")
    @GetMapping("/{id}")
    public Result<OperationLogVO> getLogById(@PathVariable Long id) {
        Long tenantId = getCurrentTenantId();
        OperationLogVO log = operationLogService.getLogById(id, tenantId);
        return Result.success(log);
    }

    /**
     * 删除日志
     */
    @Operation(summary = "删除日志", description = "删除指定的操作日志")
    @DeleteMapping("/{id}")
    public Result<Void> deleteLog(@PathVariable Long id) {
        Long tenantId = getCurrentTenantId();
        operationLogService.deleteLog(id, tenantId);
        return Result.success();
    }

    /**
     * 批量删除日志
     */
    @Operation(summary = "批量删除日志", description = "批量删除操作日志")
    @DeleteMapping("/batch")
    public Result<Void> deleteLogs(@RequestBody List<Long> ids) {
        Long tenantId = getCurrentTenantId();
        operationLogService.deleteLogs(ids, tenantId);
        return Result.success();
    }

    /**
     * 清理历史日志
     */
    @Operation(summary = "清理历史日志", description = "清理指定时间之前的日志")
    @DeleteMapping("/clean")
    public Result<Integer> cleanLogs(
            @Parameter(description = "保留天数") @RequestParam(defaultValue = "90") Integer retentionDays) {
        Long tenantId = getCurrentTenantId();
        LocalDateTime beforeTime = LocalDateTime.now().minusDays(retentionDays);
        int deleted = operationLogService.cleanLogsBefore(beforeTime, tenantId);
        return Result.success(deleted);
    }

    /**
     * 获取日志统计
     */
    @Operation(summary = "日志统计", description = "获取操作日志统计数据")
    @GetMapping("/statistics")
    public Result<OperationLogStatistics> getStatistics() {
        Long tenantId = getCurrentTenantId();
        OperationLogStatistics statistics = operationLogService.getStatistics(tenantId);
        return Result.success(statistics);
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
