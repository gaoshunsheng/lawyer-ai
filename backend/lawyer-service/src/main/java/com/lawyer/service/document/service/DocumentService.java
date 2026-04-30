package com.lawyer.service.document.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.lawyer.common.enums.DocumentStatus;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import com.lawyer.service.document.entity.Document;
import com.lawyer.service.document.entity.DocumentTemplate;
import com.lawyer.service.document.mapper.DocumentMapper;
import com.lawyer.service.document.mapper.DocumentTemplateMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.document.*;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * 文书服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DocumentService {

    private final DocumentMapper documentMapper;
    private final DocumentTemplateMapper templateMapper;
    private final CaseMapper caseMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;

    /**
     * 创建文书
     */
    @Transactional(rollbackFor = Exception.class)
    public DocumentInfo createDocument(DocumentCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        // 获取模板
        DocumentTemplate template = templateMapper.selectById(request.getTemplateId());
        if (template == null || template.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.TEMPLATE_NOT_FOUND);
        }

        // 获取用户租户ID
        User user = userMapper.selectById(userId);
        Long tenantId = user != null ? user.getTenantId() : null;

        // 检查模板权限
        if (template.getTenantId() != null && !template.getTenantId().equals(tenantId) && template.getIsPublic() != 1) {
            throw new BusinessException(ResultCode.FORBIDDEN);
        }

        Document document = new Document();
        document.setTemplateId(request.getTemplateId());
        document.setCaseId(request.getCaseId());
        document.setTitle(request.getTitle());
        document.setDocType(template.getDocType());
        document.setVersion(1);
        document.setStatus(DocumentStatus.DRAFT);
        document.setCreatedBy(userId);
        document.setUpdatedBy(userId);
        document.setTenantId(tenantId);

        // 根据模板和变量生成内容
        String content = generateContent(template.getContent(), request.getVariables());
        document.setContent(content);

        documentMapper.insert(document);

        // 更新模板使用次数
        template.setUseCount(template.getUseCount() + 1);
        templateMapper.updateById(template);

        return convertToDocumentInfo(document);
    }

    /**
     * 更新文书
     */
    @Transactional(rollbackFor = Exception.class)
    public DocumentInfo updateDocument(Long id, DocumentUpdateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        Document document = documentMapper.selectById(id);
        if (document == null || document.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.DOCUMENT_NOT_FOUND);
        }

        if (request.getTitle() != null) {
            document.setTitle(request.getTitle());
        }
        if (request.getContent() != null) {
            document.setContent(request.getContent());
            document.setVersion(document.getVersion() + 1);
        }
        if (request.getStatus() != null) {
            document.setStatus(request.getStatus());
        }

        document.setUpdatedBy(userId);
        document.setUpdatedAt(LocalDateTime.now());
        documentMapper.updateById(document);

        return convertToDocumentInfo(document);
    }

    /**
     * 获取文书详情
     */
    public DocumentInfo getDocumentById(Long id) {
        Document document = documentMapper.selectById(id);
        if (document == null || document.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.DOCUMENT_NOT_FOUND);
        }
        return convertToDocumentInfo(document);
    }

    /**
     * 删除文书
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteDocument(Long id) {
        Long userId = SecurityUtils.getCurrentUserId();

        Document document = documentMapper.selectById(id);
        if (document == null || document.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.DOCUMENT_NOT_FOUND);
        }

        document.setIsDeleted(1);
        document.setUpdatedBy(userId);
        documentMapper.updateById(document);
    }

    /**
     * 查询文书列表
     */
    public IPage<DocumentInfo> queryDocuments(DocumentQueryRequest request, Long tenantId) {
        Page<Document> page = new Page<>(request.getPage(), request.getPageSize());

        LambdaQueryWrapper<Document> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Document::getIsDeleted, 0);

        // 租户过滤
        if (tenantId != null) {
            wrapper.eq(Document::getTenantId, tenantId);
        }

        // 关键词搜索
        if (request.getKeyword() != null && !request.getKeyword().isEmpty()) {
            wrapper.like(Document::getTitle, request.getKeyword());
        }

        // 案件过滤
        if (request.getCaseId() != null) {
            wrapper.eq(Document::getCaseId, request.getCaseId());
        }

        // 文书类型过滤
        if (request.getDocType() != null && !request.getDocType().isEmpty()) {
            wrapper.eq(Document::getDocType, request.getDocType());
        }

        // 状态过滤
        if (request.getStatus() != null) {
            wrapper.eq(Document::getStatus, request.getStatus());
        }

        // 创建人过滤
        if (request.getCreatedBy() != null) {
            wrapper.eq(Document::getCreatedBy, request.getCreatedBy());
        }

        // 排序
        if ("createdAt".equals(request.getSortBy())) {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Document::getCreatedAt);
        } else if ("updatedAt".equals(request.getSortBy())) {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Document::getUpdatedAt);
        }

        IPage<Document> documentPage = documentMapper.selectPage(page, wrapper);

        return documentPage.convert(this::convertToDocumentInfo);
    }

    /**
     * 根据模板生成文书内容
     */
    private String generateContent(String templateContent, Map<String, Object> variables) {
        if (templateContent == null) {
            return "";
        }

        if (variables == null || variables.isEmpty()) {
            return templateContent;
        }

        String content = templateContent;
        // 替换 {{variable}} 格式的变量
        for (Map.Entry<String, Object> entry : variables.entrySet()) {
            String placeholder = "{{" + entry.getKey() + "}}";
            String value = entry.getValue() != null ? entry.getValue().toString() : "";
            content = content.replace(placeholder, value);
        }

        return content;
    }

    /**
     * 获取文书类型名称
     */
    private String getDocTypeName(String docType) {
        Map<String, String> typeNames = Map.of(
                "ARBITRATION_APPLICATION", "劳动仲裁申请书",
                "CIVIL_COMPLAINT", "民事起诉状",
                "DEFENSE_STATEMENT", "答辩状",
                "LAWYER_LETTER", "律师函",
                "SETTLEMENT_AGREEMENT", "和解协议",
                "EVIDENCE_LIST", "证据清单",
                "AGENCY_ARGUMENT", "代理词",
                "EXECUTION_APPLICATION", "强制执行申请书",
                "POWER_OF_ATTORNEY", "授权委托书",
                "OTHER", "其他"
        );
        return typeNames.getOrDefault(docType, docType);
    }

    /**
     * 转换为DocumentInfo
     */
    private DocumentInfo convertToDocumentInfo(Document document) {
        DocumentInfo info = new DocumentInfo();
        info.setId(document.getId());
        info.setCaseId(document.getCaseId());
        info.setDocType(document.getDocType());
        info.setDocTypeName(getDocTypeName(document.getDocType()));
        info.setTitle(document.getTitle());
        info.setContent(document.getContent());
        info.setTemplateId(document.getTemplateId());
        info.setVersion(document.getVersion());
        info.setStatus(document.getStatus());
        info.setStatusName(document.getStatus() != null ? document.getStatus().getDescription() : null);
        info.setAiSuggestions(document.getAiSuggestions());
        info.setTenantId(document.getTenantId());
        info.setCreatedBy(document.getCreatedBy());
        info.setCreatedAt(document.getCreatedAt());
        info.setUpdatedAt(document.getUpdatedAt());

        // 获取案件标题
        if (document.getCaseId() != null) {
            Case caseEntity = caseMapper.selectById(document.getCaseId());
            if (caseEntity != null) {
                info.setCaseTitle(caseEntity.getTitle());
            }
        }

        // 获取模板名称
        if (document.getTemplateId() != null) {
            DocumentTemplate template = templateMapper.selectById(document.getTemplateId());
            if (template != null) {
                info.setTemplateName(template.getName());
            }
        }

        // 获取创建人姓名
        if (document.getCreatedBy() != null) {
            User user = userMapper.selectById(document.getCreatedBy());
            if (user != null) {
                info.setCreatedByName(user.getRealName());
            }
        }

        return info;
    }
}
