package com.lawyer.api.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.document.TemplateInfo;
import com.lawyer.service.document.service.TemplateService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * 文书模板控制器
 */
@Tag(name = "文书模板", description = "文书模板的管理接口")
@RestController
@RequestMapping("/api/templates")
@RequiredArgsConstructor
public class TemplateController {

    private final TemplateService templateService;
    private final UserMapper userMapper;

    /**
     * 获取模板详情
     */
    @Operation(summary = "获取模板详情", description = "根据ID获取模板详细信息")
    @GetMapping("/{id}")
    public Result<TemplateInfo> getTemplateById(@Parameter(description = "模板ID") @PathVariable Long id) {
        TemplateInfo template = templateService.getTemplateById(id);
        return Result.success(template);
    }

    /**
     * 查询模板列表
     */
    @Operation(summary = "查询模板列表", description = "根据条件分页查询模板列表")
    @GetMapping
    public Result<IPage<TemplateInfo>> queryTemplates(
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") Integer page,
            @Parameter(description = "每页数量") @RequestParam(defaultValue = "20") Integer pageSize,
            @Parameter(description = "关键词") @RequestParam(required = false) String keyword,
            @Parameter(description = "文书类型") @RequestParam(required = false) String docType,
            @Parameter(description = "分类") @RequestParam(required = false) String category) {

        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }

        IPage<TemplateInfo> result = templateService.queryTemplates(page, pageSize, keyword, docType, category, tenantId);
        return Result.success(result);
    }

    /**
     * 创建模板
     */
    @Operation(summary = "创建模板", description = "创建新的文书模板")
    @PostMapping
    public Result<TemplateInfo> createTemplate(@Valid @RequestBody TemplateInfo request) {
        TemplateInfo template = templateService.createTemplate(request);
        return Result.success(template);
    }

    /**
     * 更新模板
     */
    @Operation(summary = "更新模板", description = "更新模板内容")
    @PutMapping("/{id}")
    public Result<TemplateInfo> updateTemplate(
            @Parameter(description = "模板ID") @PathVariable Long id,
            @Valid @RequestBody TemplateInfo request) {
        TemplateInfo template = templateService.updateTemplate(id, request);
        return Result.success(template);
    }

    /**
     * 删除模板
     */
    @Operation(summary = "删除模板", description = "软删除模板")
    @DeleteMapping("/{id}")
    public Result<Void> deleteTemplate(@Parameter(description = "模板ID") @PathVariable Long id) {
        templateService.deleteTemplate(id);
        return Result.success();
    }
}
