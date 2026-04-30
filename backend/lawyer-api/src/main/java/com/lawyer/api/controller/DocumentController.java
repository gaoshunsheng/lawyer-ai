package com.lawyer.api.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.document.*;
import com.lawyer.common.dto.ai.DocumentGenerateResponse;
import com.lawyer.service.document.service.DocumentService;
import com.lawyer.service.ai.service.AIDocumentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 文书管理控制器
 */
@Tag(name = "文书管理", description = "文书的增删改查接口")
@RestController
@RequestMapping("/api/documents")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;
    private final AIDocumentService aiDocumentService;
    private final UserMapper userMapper;

    /**
     * 创建文书
     */
    @Operation(summary = "创建文书", description = "根据模板创建新文书")
    @PostMapping
    public Result<DocumentInfo> createDocument(@Valid @RequestBody DocumentCreateRequest request) {
        DocumentInfo document = documentService.createDocument(request);
        return Result.success(document);
    }

    /**
     * 更新文书
     */
    @Operation(summary = "更新文书", description = "更新文书内容或状态")
    @PutMapping("/{id}")
    public Result<DocumentInfo> updateDocument(
            @Parameter(description = "文书ID") @PathVariable Long id,
            @Valid @RequestBody DocumentUpdateRequest request) {
        DocumentInfo document = documentService.updateDocument(id, request);
        return Result.success(document);
    }

    /**
     * 获取文书详情
     */
    @Operation(summary = "获取文书详情", description = "根据ID获取文书详细信息")
    @GetMapping("/{id}")
    public Result<DocumentInfo> getDocumentById(@Parameter(description = "文书ID") @PathVariable Long id) {
        DocumentInfo document = documentService.getDocumentById(id);
        return Result.success(document);
    }

    /**
     * 删除文书
     */
    @Operation(summary = "删除文书", description = "软删除文书")
    @DeleteMapping("/{id}")
    public Result<Void> deleteDocument(@Parameter(description = "文书ID") @PathVariable Long id) {
        documentService.deleteDocument(id);
        return Result.success();
    }

    /**
     * 查询文书列表
     */
    @Operation(summary = "查询文书列表", description = "根据条件分页查询文书列表")
    @GetMapping
    public Result<IPage<DocumentInfo>> queryDocuments(DocumentQueryRequest request) {
        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }
        IPage<DocumentInfo> page = documentService.queryDocuments(request, tenantId);
        return Result.success(page);
    }

    /**
     * 获取案件的文书列表
     */
    @Operation(summary = "获取案件的文书列表", description = "根据案件ID获取所有相关文书")
    @GetMapping("/case/{caseId}")
    public Result<IPage<DocumentInfo>> getDocumentsByCaseId(
            @Parameter(description = "案件ID") @PathVariable Long caseId,
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") Integer page,
            @Parameter(description = "每页数量") @RequestParam(defaultValue = "20") Integer pageSize) {
        DocumentQueryRequest request = new DocumentQueryRequest();
        request.setCaseId(caseId);
        request.setPage(page);
        request.setPageSize(pageSize);

        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }
        IPage<DocumentInfo> result = documentService.queryDocuments(request, tenantId);
        return Result.success(result);
    }

    /**
     * AI生成文书
     */
    @Operation(summary = "AI生成文书", description = "使用AI根据模板和案件信息生成文书")
    @PostMapping("/ai/generate")
    public Result<DocumentGenerateResponse> aiGenerateDocument(
            @Parameter(description = "模板ID") @RequestParam String templateId,
            @Parameter(description = "案件ID") @RequestParam(required = false) Long caseId,
            @Parameter(description = "文书风格") @RequestParam(required = false, defaultValue = "formal") String style,
            @RequestBody(required = false) Map<String, Object> variables) {
        DocumentGenerateResponse response = aiDocumentService.generateDocument(templateId, caseId, variables, style);
        return Result.success(response);
    }

    /**
     * AI生成仲裁申请书
     */
    @Operation(summary = "AI生成仲裁申请书", description = "根据案件信息自动生成仲裁申请书")
    @PostMapping("/ai/arbitration/{caseId}")
    public Result<DocumentGenerateResponse> generateArbitrationApplication(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        DocumentGenerateResponse response = aiDocumentService.generateArbitrationApplication(caseId);
        return Result.success(response);
    }

    /**
     * AI生成起诉状
     */
    @Operation(summary = "AI生成起诉状", description = "根据案件信息自动生成起诉状")
    @PostMapping("/ai/complaint/{caseId}")
    public Result<DocumentGenerateResponse> generateComplaint(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        DocumentGenerateResponse response = aiDocumentService.generateComplaint(caseId);
        return Result.success(response);
    }

    /**
     * AI生成答辩状
     */
    @Operation(summary = "AI生成答辩状", description = "根据案件信息自动生成答辩状")
    @PostMapping("/ai/defense/{caseId}")
    public Result<DocumentGenerateResponse> generateDefenseStatement(
            @Parameter(description = "案件ID") @PathVariable Long caseId) {
        DocumentGenerateResponse response = aiDocumentService.generateDefenseStatement(caseId);
        return Result.success(response);
    }

    /**
     * AI生成律师函
     */
    @Operation(summary = "AI生成律师函", description = "根据信息生成律师函")
    @PostMapping("/ai/lawyer-letter")
    public Result<DocumentGenerateResponse> generateLawyerLetter(
            @RequestBody Map<String, Object> variables) {
        DocumentGenerateResponse response = aiDocumentService.generateLawyerLetter(variables);
        return Result.success(response);
    }

    /**
     * AI分析文书
     */
    @Operation(summary = "AI分析文书", description = "使用AI分析文书内容并给出建议")
    @PostMapping("/ai/analyze")
    public Result<Map<String, Object>> analyzeDocument(
            @Parameter(description = "文书内容") @RequestParam String content,
            @Parameter(description = "文书类型") @RequestParam(required = false) String docType) {
        Map<String, Object> result = aiDocumentService.analyzeDocument(content, docType);
        return Result.success(result);
    }

    /**
     * 获取AI文书模板列表
     */
    @Operation(summary = "获取AI文书模板", description = "获取AI支持的文书模板列表")
    @GetMapping("/ai/templates")
    public Result<List<Map<String, Object>>> getAITemplates() {
        List<Map<String, Object>> templates = aiDocumentService.getDocumentTemplates();
        return Result.success(templates);
    }
}
