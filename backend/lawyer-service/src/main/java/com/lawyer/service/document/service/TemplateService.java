package com.lawyer.service.document.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.document.entity.DocumentTemplate;
import com.lawyer.service.document.mapper.DocumentTemplateMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.document.TemplateInfo;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 文书模板服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TemplateService {

    private final DocumentTemplateMapper templateMapper;
    private final UserMapper userMapper;

    /**
     * 获取模板详情
     */
    public TemplateInfo getTemplateById(Long id) {
        DocumentTemplate template = templateMapper.selectById(id);
        if (template == null || template.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.TEMPLATE_NOT_FOUND);
        }

        // 检查权限
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        Long tenantId = user != null ? user.getTenantId() : null;

        if (template.getTenantId() != null && !template.getTenantId().equals(tenantId) && template.getIsPublic() != 1) {
            throw new BusinessException(ResultCode.FORBIDDEN);
        }

        return convertToTemplateInfo(template);
    }

    /**
     * 获取模板列表
     */
    public IPage<TemplateInfo> queryTemplates(Integer page, Integer pageSize, String keyword,
                                               String docType, String category, Long tenantId) {
        Page<DocumentTemplate> templatePage = new Page<>(page, pageSize);

        LambdaQueryWrapper<DocumentTemplate> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(DocumentTemplate::getIsDeleted, 0);

        // 获取公开模板或当前租户的模板
        wrapper.and(w -> w.eq(DocumentTemplate::getIsPublic, 1)
                .or().eq(DocumentTemplate::getTenantId, tenantId)
                .or().isNull(DocumentTemplate::getTenantId));

        // 关键词搜索
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.like(DocumentTemplate::getName, keyword);
        }

        // 文书类型过滤
        if (docType != null && !docType.isEmpty()) {
            wrapper.eq(DocumentTemplate::getDocType, docType);
        }

        // 分类过滤
        if (category != null && !category.isEmpty()) {
            wrapper.eq(DocumentTemplate::getCategory, category);
        }

        // 按使用次数和评分排序
        wrapper.orderByDesc(DocumentTemplate::getUseCount)
                .orderByDesc(DocumentTemplate::getRating);

        IPage<DocumentTemplate> result = templateMapper.selectPage(templatePage, wrapper);

        return result.convert(this::convertToTemplateInfo);
    }

    /**
     * 创建模板
     */
    @Transactional(rollbackFor = Exception.class)
    public TemplateInfo createTemplate(TemplateInfo request) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);

        DocumentTemplate template = new DocumentTemplate();
        template.setName(request.getName());
        template.setDocType(request.getDocType());
        template.setContent(request.getContent());
        template.setVariables(request.getVariables());
        template.setCategory(request.getCategory());
        template.setDescription(request.getDescription());
        template.setIsPublic(request.getIsPublic() != null ? request.getIsPublic() : 0);
        template.setTenantId(user != null ? user.getTenantId() : null);
        template.setUseCount(0);
        template.setRating(java.math.BigDecimal.ZERO);
        template.setCreatedBy(userId);
        template.setUpdatedBy(userId);

        templateMapper.insert(template);

        return convertToTemplateInfo(template);
    }

    /**
     * 更新模板
     */
    @Transactional(rollbackFor = Exception.class)
    public TemplateInfo updateTemplate(Long id, TemplateInfo request) {
        Long userId = SecurityUtils.getCurrentUserId();

        DocumentTemplate template = templateMapper.selectById(id);
        if (template == null || template.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.TEMPLATE_NOT_FOUND);
        }

        // 检查权限
        User user = userMapper.selectById(userId);
        Long tenantId = user != null ? user.getTenantId() : null;
        if (template.getTenantId() != null && !template.getTenantId().equals(tenantId)) {
            throw new BusinessException(ResultCode.FORBIDDEN);
        }

        if (request.getName() != null) {
            template.setName(request.getName());
        }
        if (request.getDocType() != null) {
            template.setDocType(request.getDocType());
        }
        if (request.getContent() != null) {
            template.setContent(request.getContent());
        }
        if (request.getVariables() != null) {
            template.setVariables(request.getVariables());
        }
        if (request.getCategory() != null) {
            template.setCategory(request.getCategory());
        }
        if (request.getDescription() != null) {
            template.setDescription(request.getDescription());
        }
        if (request.getIsPublic() != null) {
            template.setIsPublic(request.getIsPublic());
        }

        template.setUpdatedBy(userId);
        template.setUpdatedAt(LocalDateTime.now());
        templateMapper.updateById(template);

        return convertToTemplateInfo(template);
    }

    /**
     * 删除模板
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteTemplate(Long id) {
        Long userId = SecurityUtils.getCurrentUserId();

        DocumentTemplate template = templateMapper.selectById(id);
        if (template == null || template.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.TEMPLATE_NOT_FOUND);
        }

        // 检查权限
        User user = userMapper.selectById(userId);
        Long tenantId = user != null ? user.getTenantId() : null;
        if (template.getTenantId() != null && !template.getTenantId().equals(tenantId)) {
            throw new BusinessException(ResultCode.FORBIDDEN);
        }

        template.setIsDeleted(1);
        template.setUpdatedBy(userId);
        templateMapper.updateById(template);
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
     * 转换为TemplateInfo
     */
    private TemplateInfo convertToTemplateInfo(DocumentTemplate template) {
        TemplateInfo info = new TemplateInfo();
        info.setId(template.getId());
        info.setName(template.getName());
        info.setDocType(template.getDocType());
        info.setDocTypeName(getDocTypeName(template.getDocType()));
        info.setContent(template.getContent());
        info.setVariables(template.getVariables());
        info.setCategory(template.getCategory());
        info.setDescription(template.getDescription());
        info.setIsPublic(template.getIsPublic());
        info.setTenantId(template.getTenantId());
        info.setUseCount(template.getUseCount());
        info.setRating(template.getRating());
        info.setCreatedAt(template.getCreatedAt());
        return info;
    }
}
