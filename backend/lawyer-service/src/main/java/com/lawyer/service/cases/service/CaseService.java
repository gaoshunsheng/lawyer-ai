package com.lawyer.service.cases.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.cases.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 案件服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CaseService {

    private final CaseMapper caseMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;

    /**
     * 创建案件
     */
    @Transactional(rollbackFor = Exception.class)
    public CaseInfo createCase(CaseCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        Case caseEntity = new Case();
        caseEntity.setTitle(request.getTitle());
        caseEntity.setCaseType(request.getCaseType());
        caseEntity.setCaseNumber(request.getCaseNumber());
        caseEntity.setCaseStatus(CaseStatus.PENDING);
        caseEntity.setClaimAmount(request.getClaimAmount());
        caseEntity.setDisputeFocus(request.getDisputeFocus());
        caseEntity.setDescription(request.getDescription());
        caseEntity.setLawyerId(request.getLawyerId());
        caseEntity.setAssistantId(request.getAssistantId());
        caseEntity.setFiledDate(request.getFiledDate() != null ? request.getFiledDate() : LocalDate.now());
        caseEntity.setCreatedBy(userId);
        caseEntity.setUpdatedBy(userId);

        // 处理原告信息
        if (request.getPlaintiff() != null) {
            try {
                caseEntity.setPlaintiff(objectMapper.writeValueAsString(request.getPlaintiff()));
            } catch (JsonProcessingException e) {
                log.error("序列化原告信息失败", e);
            }
        }

        // 处理被告信息
        if (request.getDefendant() != null) {
            try {
                caseEntity.setDefendant(objectMapper.writeValueAsString(request.getDefendant()));
            } catch (JsonProcessingException e) {
                log.error("序列化被告信息失败", e);
            }
        }

        // 获取当前用户的租户ID
        User user = userMapper.selectById(userId);
        if (user != null) {
            caseEntity.setTenantId(user.getTenantId());
        }

        caseMapper.insert(caseEntity);
        return convertToCaseInfo(caseEntity);
    }

    /**
     * 更新案件
     */
    @Transactional(rollbackFor = Exception.class)
    public CaseInfo updateCase(Long id, CaseUpdateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        Case caseEntity = caseMapper.selectById(id);
        if (caseEntity == null || caseEntity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.CASE_NOT_FOUND);
        }

        // 更新字段
        if (request.getTitle() != null) {
            caseEntity.setTitle(request.getTitle());
        }
        if (request.getCaseType() != null) {
            caseEntity.setCaseType(request.getCaseType());
        }
        if (request.getCaseStatus() != null) {
            caseEntity.setCaseStatus(request.getCaseStatus());
        }
        if (request.getCaseNumber() != null) {
            caseEntity.setCaseNumber(request.getCaseNumber());
        }
        if (request.getClaimAmount() != null) {
            caseEntity.setClaimAmount(request.getClaimAmount());
        }
        if (request.getDisputeFocus() != null) {
            caseEntity.setDisputeFocus(request.getDisputeFocus());
        }
        if (request.getDescription() != null) {
            caseEntity.setDescription(request.getDescription());
        }
        if (request.getLawyerId() != null) {
            caseEntity.setLawyerId(request.getLawyerId());
        }
        if (request.getAssistantId() != null) {
            caseEntity.setAssistantId(request.getAssistantId());
        }
        if (request.getClosedDate() != null) {
            caseEntity.setClosedDate(request.getClosedDate());
        }

        // 处理原告信息
        if (request.getPlaintiff() != null) {
            try {
                caseEntity.setPlaintiff(objectMapper.writeValueAsString(request.getPlaintiff()));
            } catch (JsonProcessingException e) {
                log.error("序列化原告信息失败", e);
            }
        }

        // 处理被告信息
        if (request.getDefendant() != null) {
            try {
                caseEntity.setDefendant(objectMapper.writeValueAsString(request.getDefendant()));
            } catch (JsonProcessingException e) {
                log.error("序列化被告信息失败", e);
            }
        }

        caseEntity.setUpdatedBy(userId);
        caseMapper.updateById(caseEntity);

        return convertToCaseInfo(caseEntity);
    }

    /**
     * 获取案件详情
     */
    public CaseInfo getCaseById(Long id) {
        Case caseEntity = caseMapper.selectById(id);
        if (caseEntity == null || caseEntity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.CASE_NOT_FOUND);
        }
        return convertToCaseInfo(caseEntity);
    }

    /**
     * 删除案件
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteCase(Long id) {
        Long userId = SecurityUtils.getCurrentUserId();

        Case caseEntity = caseMapper.selectById(id);
        if (caseEntity == null || caseEntity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.CASE_NOT_FOUND);
        }

        caseEntity.setIsDeleted(1);
        caseEntity.setUpdatedBy(userId);
        caseMapper.updateById(caseEntity);
    }

    /**
     * 查询案件列表
     */
    public IPage<CaseInfo> queryCases(CaseQueryRequest request, Long tenantId) {
        Page<Case> page = new Page<>(request.getPage(), request.getPageSize());

        LambdaQueryWrapper<Case> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Case::getIsDeleted, 0);

        // 租户过滤
        if (tenantId != null) {
            wrapper.eq(Case::getTenantId, tenantId);
        }

        // 关键词搜索
        if (request.getKeyword() != null && !request.getKeyword().isEmpty()) {
            wrapper.and(w -> w.like(Case::getTitle, request.getKeyword())
                    .or().like(Case::getCaseNumber, request.getKeyword()));
        }

        // 案件类型过滤
        if (request.getCaseType() != null) {
            wrapper.eq(Case::getCaseType, request.getCaseType());
        }

        // 案件状态过滤
        if (request.getCaseStatus() != null) {
            wrapper.eq(Case::getCaseStatus, request.getCaseStatus());
        }

        // 律师过滤
        if (request.getLawyerId() != null) {
            wrapper.eq(Case::getLawyerId, request.getLawyerId());
        }

        // 标的金额范围
        if (request.getClaimAmountMin() != null) {
            wrapper.ge(Case::getClaimAmount, request.getClaimAmountMin());
        }
        if (request.getClaimAmountMax() != null) {
            wrapper.le(Case::getClaimAmount, request.getClaimAmountMax());
        }

        // 排序
        if ("createdAt".equals(request.getSortBy())) {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Case::getCreatedAt);
        } else if ("updatedAt".equals(request.getSortBy())) {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Case::getUpdatedAt);
        } else if ("filedDate".equals(request.getSortBy())) {
            wrapper.orderBy(true, "desc".equals(request.getSortOrder()), Case::getFiledDate);
        }

        IPage<Case> casePage = caseMapper.selectPage(page, wrapper);

        return casePage.convert(this::convertToCaseInfo);
    }

    /**
     * 获取案件统计
     */
    public CaseStatistics getStatistics(Long tenantId) {
        CaseStatistics stats = new CaseStatistics();

        LambdaQueryWrapper<Case> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Case::getIsDeleted, 0);
        if (tenantId != null) {
            wrapper.eq(Case::getTenantId, tenantId);
        }

        // 总案件数
        stats.setTotalCases(caseMapper.selectCount(wrapper));

        // 进行中案件数
        LambdaQueryWrapper<Case> ongoingWrapper = new LambdaQueryWrapper<>();
        ongoingWrapper.eq(Case::getIsDeleted, 0)
                .notIn(Case::getCaseStatus, CaseStatus.CLOSED, CaseStatus.CANCELLED);
        if (tenantId != null) {
            ongoingWrapper.eq(Case::getTenantId, tenantId);
        }
        stats.setOngoingCases(caseMapper.selectCount(ongoingWrapper));

        // 已结案案件数
        LambdaQueryWrapper<Case> closedWrapper = new LambdaQueryWrapper<>();
        closedWrapper.eq(Case::getIsDeleted, 0)
                .eq(Case::getCaseStatus, CaseStatus.CLOSED);
        if (tenantId != null) {
            closedWrapper.eq(Case::getTenantId, tenantId);
        }
        stats.setClosedCases(caseMapper.selectCount(closedWrapper));

        // 本月新增案件数
        LocalDateTime monthStart = LocalDate.now().withDayOfMonth(1).atStartOfDay();
        LambdaQueryWrapper<Case> monthlyWrapper = new LambdaQueryWrapper<>();
        monthlyWrapper.eq(Case::getIsDeleted, 0)
                .ge(Case::getCreatedAt, monthStart);
        if (tenantId != null) {
            monthlyWrapper.eq(Case::getTenantId, tenantId);
        }
        stats.setMonthlyNewCases(caseMapper.selectCount(monthlyWrapper));

        // 按案件类型统计
        Map<String, Long> typeDistribution = new HashMap<>();
        for (CaseType type : CaseType.values()) {
            LambdaQueryWrapper<Case> typeWrapper = new LambdaQueryWrapper<>();
            typeWrapper.eq(Case::getIsDeleted, 0).eq(Case::getCaseType, type);
            if (tenantId != null) {
                typeWrapper.eq(Case::getTenantId, tenantId);
            }
            typeDistribution.put(type.getCode(), caseMapper.selectCount(typeWrapper));
        }
        stats.setCaseTypeDistribution(typeDistribution);

        // 按案件状态统计
        Map<String, Long> statusDistribution = new HashMap<>();
        for (CaseStatus status : CaseStatus.values()) {
            LambdaQueryWrapper<Case> statusWrapper = new LambdaQueryWrapper<>();
            statusWrapper.eq(Case::getIsDeleted, 0).eq(Case::getCaseStatus, status);
            if (tenantId != null) {
                statusWrapper.eq(Case::getTenantId, tenantId);
            }
            statusDistribution.put(status.getCode(), caseMapper.selectCount(statusWrapper));
        }
        stats.setCaseStatusDistribution(statusDistribution);

        return stats;
    }

    /**
     * 转换为CaseInfo
     */
    private CaseInfo convertToCaseInfo(Case caseEntity) {
        CaseInfo info = new CaseInfo();
        info.setId(caseEntity.getId());
        info.setCaseNumber(caseEntity.getCaseNumber());
        info.setCaseType(caseEntity.getCaseType());
        info.setCaseTypeName(caseEntity.getCaseType() != null ? caseEntity.getCaseType().getDescription() : null);
        info.setCaseStatus(caseEntity.getCaseStatus());
        info.setCaseStatusName(caseEntity.getCaseStatus() != null ? caseEntity.getCaseStatus().getDescription() : null);
        info.setTitle(caseEntity.getTitle());
        info.setClaimAmount(caseEntity.getClaimAmount());
        info.setDisputeFocus(caseEntity.getDisputeFocus());
        info.setLawyerId(caseEntity.getLawyerId());
        info.setAssistantId(caseEntity.getAssistantId());
        info.setTenantId(caseEntity.getTenantId());
        info.setDescription(caseEntity.getDescription());
        info.setTimeline(caseEntity.getTimeline());
        info.setAiAnalysis(caseEntity.getAiAnalysis());
        info.setFiledDate(caseEntity.getFiledDate());
        info.setClosedDate(caseEntity.getClosedDate());
        info.setCreatedAt(caseEntity.getCreatedAt());
        info.setUpdatedAt(caseEntity.getUpdatedAt());

        // 解析原告信息
        if (caseEntity.getPlaintiff() != null) {
            try {
                info.setPlaintiff(objectMapper.readValue(caseEntity.getPlaintiff(), CaseCreateRequest.PartyInfo.class));
            } catch (JsonProcessingException e) {
                log.error("解析原告信息失败", e);
            }
        }

        // 解析被告信息
        if (caseEntity.getDefendant() != null) {
            try {
                info.setDefendant(objectMapper.readValue(caseEntity.getDefendant(), CaseCreateRequest.PartyInfo.class));
            } catch (JsonProcessingException e) {
                log.error("解析被告信息失败", e);
            }
        }

        // 获取律师姓名
        if (caseEntity.getLawyerId() != null) {
            User lawyer = userMapper.selectById(caseEntity.getLawyerId());
            if (lawyer != null) {
                info.setLawyerName(lawyer.getRealName());
            }
        }

        // 获取助理姓名
        if (caseEntity.getAssistantId() != null) {
            User assistant = userMapper.selectById(caseEntity.getAssistantId());
            if (assistant != null) {
                info.setAssistantName(assistant.getRealName());
            }
        }

        return info;
    }
}
