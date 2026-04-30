package com.lawyer.api.controller;

import com.lawyer.common.result.Result;
import com.lawyer.common.dto.cases.TimelineEvent;
import com.lawyer.common.dto.cases.TimelineEventCreateRequest;
import com.lawyer.service.cases.service.TimelineService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 时间线管理控制器
 */
@Tag(name = "时间线管理", description = "案件时间线事件管理接口")
@RestController
@RequestMapping("/api/timeline")
@RequiredArgsConstructor
public class TimelineController {

    private final TimelineService timelineService;

    /**
     * 添加时间线事件
     */
    @Operation(summary = "添加时间线事件", description = "为案件添加时间线事件")
    @PostMapping
    public Result<TimelineEvent> addEvent(@Valid @RequestBody TimelineEventCreateRequest request) {
        TimelineEvent event = timelineService.addEvent(request);
        return Result.success(event);
    }

    /**
     * 批量添加时间线事件
     */
    @Operation(summary = "批量添加时间线事件", description = "批量添加多个时间线事件")
    @PostMapping("/batch/{caseId}")
    public Result<List<TimelineEvent>> addEvents(
            @Parameter(description = "案件ID") @PathVariable Long caseId,
            @RequestBody List<TimelineEventCreateRequest> events) {
        List<TimelineEvent> result = timelineService.addEvents(caseId, events);
        return Result.success(result);
    }

    /**
     * 更新时间线事件
     */
    @Operation(summary = "更新时间线事件", description = "更新时间线事件信息")
    @PutMapping("/{id}")
    public Result<TimelineEvent> updateEvent(
            @Parameter(description = "事件ID") @PathVariable Long id,
            @Valid @RequestBody TimelineEventCreateRequest request) {
        TimelineEvent event = timelineService.updateEvent(id, request);
        return Result.success(event);
    }

    /**
     * 删除时间线事件
     */
    @Operation(summary = "删除时间线事件", description = "删除指定的时间线事件")
    @DeleteMapping("/{id}")
    public Result<Void> deleteEvent(@Parameter(description = "事件ID") @PathVariable Long id) {
        timelineService.deleteEvent(id);
        return Result.success();
    }

    /**
     * 获取案件时间线
     */
    @Operation(summary = "获取案件时间线", description = "获取指定案件的所有时间线事件")
    @GetMapping("/case/{caseId}")
    public Result<List<TimelineEvent>> getCaseTimeline(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        List<TimelineEvent> timeline = timelineService.getCaseTimeline(caseId);
        return Result.success(timeline);
    }
}
