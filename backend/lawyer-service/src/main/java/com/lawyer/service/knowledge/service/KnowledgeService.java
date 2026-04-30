package com.lawyer.service.knowledge.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.knowledge.entity.Knowledge;
import com.lawyer.service.knowledge.mapper.KnowledgeMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.knowledge.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 知识库服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class KnowledgeService {

    private final KnowledgeMapper knowledgeMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;

    /**
     * 创建知识条目
     */
    @Transactional(rollbackFor = Exception.class)
    public KnowledgeInfo createKnowledge(KnowledgeCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);

        Knowledge knowledge = new Knowledge();
        knowledge.setCategory(request.getCategory());
        knowledge.setDocType(request.getDocType());
        knowledge.setTitle(request.getTitle());
        knowledge.setContent(request.getContent());
        knowledge.setSource(request.getSource());
        knowledge.setPublishDate(request.getPublishDate());
        knowledge.setEffectiveDate(request.getEffectiveDate());
        knowledge.setExpiryDate(request.getExpiryDate());
        knowledge.setViewCount(0);
        knowledge.setFavoriteCount(0);
        knowledge.setCreatedBy(userId);
        knowledge.setUpdatedBy(userId);

        if (user != null) {
            knowledge.setTenantId(user.getTenantId());
        }

        if (request.getTags() != null) {
            try {
                knowledge.setTags(objectMapper.writeValueAsString(request.getTags()));
            } catch (JsonProcessingException e) {
                log.error("序列化标签失败", e);
            }
        }

        if (request.getMetadata() != null) {
            knowledge.setMetadata(request.getMetadata());
        }

        knowledgeMapper.insert(knowledge);

        // TODO: 同步到向量数据库

        return convertToKnowledgeInfo(knowledge);
    }

    /**
     * 更新知识条目
     */
    @Transactional(rollbackFor = Exception.class)
    public KnowledgeInfo updateKnowledge(Long id, KnowledgeCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        Knowledge knowledge = knowledgeMapper.selectById(id);
        if (knowledge == null || knowledge.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND);
        }

        if (request.getCategory() != null) {
            knowledge.setCategory(request.getCategory());
        }
        if (request.getDocType() != null) {
            knowledge.setDocType(request.getDocType());
        }
        if (request.getTitle() != null) {
            knowledge.setTitle(request.getTitle());
        }
        if (request.getContent() != null) {
            knowledge.setContent(request.getContent());
        }
        if (request.getSource() != null) {
            knowledge.setSource(request.getSource());
        }
        if (request.getPublishDate() != null) {
            knowledge.setPublishDate(request.getPublishDate());
        }
        if (request.getEffectiveDate() != null) {
            knowledge.setEffectiveDate(request.getEffectiveDate());
        }
        if (request.getExpiryDate() != null) {
            knowledge.setExpiryDate(request.getExpiryDate());
        }

        if (request.getTags() != null) {
            try {
                knowledge.setTags(objectMapper.writeValueAsString(request.getTags()));
            } catch (JsonProcessingException e) {
                log.error("序列化标签失败", e);
            }
        }

        knowledge.setUpdatedBy(userId);
        knowledgeMapper.updateById(knowledge);

        // TODO: 同步更新向量数据库

        return convertToKnowledgeInfo(knowledge);
    }

    /**
     * 获取知识条目详情
     */
    public KnowledgeInfo getKnowledgeById(Long id) {
        Knowledge knowledge = knowledgeMapper.selectById(id);
        if (knowledge == null || knowledge.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND);
        }

        // 增加查看次数
        knowledge.setViewCount(knowledge.getViewCount() + 1);
        knowledgeMapper.updateById(knowledge);

        return convertToKnowledgeInfo(knowledge);
    }

    /**
     * 删除知识条目
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteKnowledge(Long id) {
        Long userId = SecurityUtils.getCurrentUserId();

        Knowledge knowledge = knowledgeMapper.selectById(id);
        if (knowledge == null || knowledge.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND);
        }

        knowledge.setIsDeleted(1);
        knowledge.setUpdatedBy(userId);
        knowledgeMapper.updateById(knowledge);

        // TODO: 从向量数据库删除
    }

    /**
     * 搜索知识条目
     */
    public IPage<KnowledgeInfo> searchKnowledge(KnowledgeSearchRequest request, Long tenantId) {
        Page<Knowledge> page = new Page<>(request.getPage(), request.getPageSize());

        LambdaQueryWrapper<Knowledge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Knowledge::getIsDeleted, 0);

        // 租户过滤（公共知识库 + 本租户知识）
        if (tenantId != null) {
            wrapper.and(w -> w.isNull(Knowledge::getTenantId)
                    .or().eq(Knowledge::getTenantId, tenantId));
        } else {
            wrapper.isNull(Knowledge::getTenantId);
        }

        // 关键词搜索
        if (request.getKeyword() != null && !request.getKeyword().isEmpty()) {
            wrapper.and(w -> w.like(Knowledge::getTitle, request.getKeyword())
                    .or().like(Knowledge::getContent, request.getKeyword()));
        }

        // 文档类型过滤
        if (request.getDocType() != null && !request.getDocType().isEmpty()) {
            wrapper.eq(Knowledge::getDocType, request.getDocType());
        }

        // 分类过滤
        if (request.getCategory() != null && !request.getCategory().isEmpty()) {
            wrapper.eq(Knowledge::getCategory, request.getCategory());
        }

        // 有效状态过滤
        if (request.getEffective() != null && request.getEffective()) {
            LocalDate now = LocalDate.now();
            wrapper.and(w -> w.isNull(Knowledge::getExpiryDate)
                    .or().gt(Knowledge::getExpiryDate, now));
        }

        // 排序
        if ("viewCount".equals(request.getSortBy())) {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Knowledge::getViewCount);
        } else if ("publishDate".equals(request.getSortBy())) {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Knowledge::getPublishDate);
        } else {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Knowledge::getCreatedAt);
        }

        IPage<Knowledge> result = knowledgeMapper.selectPage(page, wrapper);

        return result.convert(this::convertToKnowledgeInfo);
    }

    /**
     * 获取分类列表
     */
    public List<String> getCategories(Long tenantId) {
        // 简单实现，实际可以使用GROUP BY
        List<Knowledge> list = knowledgeMapper.selectList(
                new LambdaQueryWrapper<Knowledge>()
                        .select(Knowledge::getCategory)
                        .eq(Knowledge::getIsDeleted, 0)
                        .and(w -> {
                            if (tenantId != null) {
                                w.isNull(Knowledge::getTenantId)
                                        .or().eq(Knowledge::getTenantId, tenantId);
                            } else {
                                w.isNull(Knowledge::getTenantId);
                            }
                        })
                        .groupBy(Knowledge::getCategory)
        );

        return list.stream()
                .map(Knowledge::getCategory)
                .filter(c -> c != null && !c.isEmpty())
                .distinct()
                .collect(Collectors.toList());
    }

    /**
     * 获取文档类型名称
     */
    private String getDocTypeName(String docType) {
        switch (docType) {
            case "LAW":
                return "法律法规";
            case "CASE":
                return "案例";
            case "INTERNAL":
                return "内部资料";
            default:
                return docType;
        }
    }

    /**
     * 转换为KnowledgeInfo
     */
    private KnowledgeInfo convertToKnowledgeInfo(Knowledge knowledge) {
        KnowledgeInfo info = new KnowledgeInfo();
        info.setId(knowledge.getId());
        info.setCategory(knowledge.getCategory());
        info.setDocType(knowledge.getDocType());
        info.setDocTypeName(getDocTypeName(knowledge.getDocType()));
        info.setTitle(knowledge.getTitle());
        info.setContent(knowledge.getContent());
        info.setSource(knowledge.getSource());
        info.setPublishDate(knowledge.getPublishDate());
        info.setEffectiveDate(knowledge.getEffectiveDate());
        info.setExpiryDate(knowledge.getExpiryDate());
        info.setViewCount(knowledge.getViewCount());
        info.setFavoriteCount(knowledge.getFavoriteCount());
        info.setTenantId(knowledge.getTenantId());
        info.setMetadata(knowledge.getMetadata());
        info.setCreatedAt(knowledge.getCreatedAt());
        info.setUpdatedAt(knowledge.getUpdatedAt());

        // 解析标签
        if (knowledge.getTags() != null) {
            try {
                info.setTags(objectMapper.readValue(knowledge.getTags(), new TypeReference<List<String>>() {}));
            } catch (JsonProcessingException e) {
                log.error("解析标签失败", e);
            }
        }

        return info;
    }
}
