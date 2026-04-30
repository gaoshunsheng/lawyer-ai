package com.lawyer.api.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.knowledge.*;
import com.lawyer.common.dto.ai.KnowledgeSearchResult;
import com.lawyer.service.knowledge.service.KnowledgeService;
import com.lawyer.service.ai.service.AIKnowledgeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 知识库控制器
 */
@Tag(name = "知识库", description = "知识库检索和管理接口")
@RestController
@RequestMapping("/api/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {

    private final KnowledgeService knowledgeService;
    private final AIKnowledgeService aiKnowledgeService;
    private final UserMapper userMapper;

    /**
     * 创建知识条目
     */
    @Operation(summary = "创建知识条目", description = "添加新的知识条目到知识库")
    @PostMapping
    public Result<KnowledgeInfo> createKnowledge(@Valid @RequestBody KnowledgeCreateRequest request) {
        KnowledgeInfo knowledge = knowledgeService.createKnowledge(request);
        return Result.success(knowledge);
    }

    /**
     * 更新知识条目
     */
    @Operation(summary = "更新知识条目", description = "更新知识条目内容")
    @PutMapping("/{id}")
    public Result<KnowledgeInfo> updateKnowledge(
            @Parameter(description = "知识条目ID") @PathVariable Long id,
            @Valid @RequestBody KnowledgeCreateRequest request) {
        KnowledgeInfo knowledge = knowledgeService.updateKnowledge(id, request);
        return Result.success(knowledge);
    }

    /**
     * 获取知识条目详情
     */
    @Operation(summary = "获取知识条目详情", description = "根据ID获取知识条目详细信息")
    @GetMapping("/{id}")
    public Result<KnowledgeInfo> getKnowledgeById(@Parameter(description = "知识条目ID") @PathVariable Long id) {
        KnowledgeInfo knowledge = knowledgeService.getKnowledgeById(id);
        return Result.success(knowledge);
    }

    /**
     * 删除知识条目
     */
    @Operation(summary = "删除知识条目", description = "软删除知识条目")
    @DeleteMapping("/{id}")
    public Result<Void> deleteKnowledge(@Parameter(description = "知识条目ID") @PathVariable Long id) {
        knowledgeService.deleteKnowledge(id);
        return Result.success();
    }

    /**
     * 搜索知识条目
     */
    @Operation(summary = "搜索知识条目", description = "根据条件搜索知识库")
    @GetMapping("/search")
    public Result<IPage<KnowledgeInfo>> searchKnowledge(KnowledgeSearchRequest request) {
        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }
        IPage<KnowledgeInfo> result = knowledgeService.searchKnowledge(request, tenantId);
        return Result.success(result);
    }

    /**
     * 获取分类列表
     */
    @Operation(summary = "获取分类列表", description = "获取知识库所有分类")
    @GetMapping("/categories")
    public Result<List<String>> getCategories() {
        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }
        List<String> categories = knowledgeService.getCategories(tenantId);
        return Result.success(categories);
    }

    /**
     * AI智能检索知识
     */
    @Operation(summary = "AI智能检索", description = "使用AI向量检索知识库")
    @PostMapping("/ai/search")
    public Result<List<KnowledgeSearchResult>> aiSearchKnowledge(
            @Parameter(description = "查询文本") @RequestParam String query,
            @Parameter(description = "文档类型") @RequestParam(required = false) List<String> docTypes,
            @Parameter(description = "返回数量") @RequestParam(defaultValue = "10") Integer topK) {
        List<KnowledgeSearchResult> results = aiKnowledgeService.searchKnowledge(query, docTypes, topK);
        return Result.success(results);
    }

    /**
     * AI检索法规
     */
    @Operation(summary = "AI检索法规", description = "使用AI向量检索法规")
    @GetMapping("/ai/laws")
    public Result<List<KnowledgeSearchResult>> aiSearchLaws(
            @Parameter(description = "查询文本") @RequestParam String query,
            @Parameter(description = "返回数量") @RequestParam(defaultValue = "10") Integer topK) {
        List<KnowledgeSearchResult> results = aiKnowledgeService.searchLaws(query, topK);
        return Result.success(results);
    }

    /**
     * AI检索案例
     */
    @Operation(summary = "AI检索案例", description = "使用AI向量检索案例")
    @GetMapping("/ai/cases")
    public Result<List<KnowledgeSearchResult>> aiSearchCases(
            @Parameter(description = "查询文本") @RequestParam String query,
            @Parameter(description = "返回数量") @RequestParam(defaultValue = "10") Integer topK) {
        List<KnowledgeSearchResult> results = aiKnowledgeService.searchCases(query, topK);
        return Result.success(results);
    }

    /**
     * AI综合检索
     */
    @Operation(summary = "AI综合检索", description = "使用AI综合检索法规和案例")
    @GetMapping("/ai/comprehensive")
    public Result<List<KnowledgeSearchResult>> aiSearchComprehensive(
            @Parameter(description = "查询文本") @RequestParam String query,
            @Parameter(description = "返回数量") @RequestParam(defaultValue = "10") Integer topK) {
        List<KnowledgeSearchResult> results = aiKnowledgeService.searchComprehensive(query, topK);
        return Result.success(results);
    }

    /**
     * 存储知识到向量数据库
     */
    @Operation(summary = "存储知识到AI", description = "将知识存储到AI向量数据库")
    @PostMapping("/ai/store")
    public Result<Map<String, Object>> storeToAI(
            @Parameter(description = "文档类型") @RequestParam String docType,
            @Parameter(description = "标题") @RequestParam String title,
            @Parameter(description = "内容") @RequestParam String content,
            @Parameter(description = "分类") @RequestParam(required = false) String category) {
        Long tenantId = getCurrentTenantId();
        Map<String, Object> result = aiKnowledgeService.storeKnowledge(docType, title, content, category, tenantId);
        return Result.success(result);
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
