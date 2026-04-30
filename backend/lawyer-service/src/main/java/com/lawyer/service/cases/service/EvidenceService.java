package com.lawyer.service.cases.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.entity.Evidence;
import com.lawyer.service.cases.mapper.CaseMapper;
import com.lawyer.service.cases.mapper.EvidenceMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.cases.EvidenceCreateRequest;
import com.lawyer.common.dto.cases.EvidenceInfo;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 证据服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class EvidenceService {

    private final EvidenceMapper evidenceMapper;
    private final CaseMapper caseMapper;
    private final UserMapper userMapper;

    /**
     * 创建证据
     */
    @Transactional(rollbackFor = Exception.class)
    public EvidenceInfo createEvidence(EvidenceCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        // 检查案件是否存在
        Case caseEntity = caseMapper.selectById(request.getCaseId());
        if (caseEntity == null || caseEntity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.CASE_NOT_FOUND);
        }

        Evidence evidence = new Evidence();
        evidence.setCaseId(request.getCaseId());
        evidence.setName(request.getName());
        evidence.setType(request.getType());
        evidence.setDescription(request.getDescription());
        evidence.setFileUrl(request.getFileUrl());
        evidence.setFileType(request.getFileType());
        evidence.setFileSize(request.getFileSize());
        evidence.setUploadTime(LocalDateTime.now());
        evidence.setChainOrder(request.getChainOrder());
        evidence.setChainDescription(request.getChainDescription());
        evidence.setCreatedBy(userId);
        evidence.setUpdatedBy(userId);

        // 获取租户ID
        User user = userMapper.selectById(userId);
        if (user != null) {
            evidence.setTenantId(user.getTenantId());
        }

        evidenceMapper.insert(evidence);
        return convertToEvidenceInfo(evidence);
    }

    /**
     * 更新证据
     */
    @Transactional(rollbackFor = Exception.class)
    public EvidenceInfo updateEvidence(Long id, EvidenceCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        Evidence evidence = evidenceMapper.selectById(id);
        if (evidence == null || evidence.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND);
        }

        if (request.getName() != null) {
            evidence.setName(request.getName());
        }
        if (request.getType() != null) {
            evidence.setType(request.getType());
        }
        if (request.getDescription() != null) {
            evidence.setDescription(request.getDescription());
        }
        if (request.getFileUrl() != null) {
            evidence.setFileUrl(request.getFileUrl());
        }
        if (request.getFileType() != null) {
            evidence.setFileType(request.getFileType());
        }
        if (request.getFileSize() != null) {
            evidence.setFileSize(request.getFileSize());
        }
        if (request.getChainOrder() != null) {
            evidence.setChainOrder(request.getChainOrder());
        }
        if (request.getChainDescription() != null) {
            evidence.setChainDescription(request.getChainDescription());
        }

        evidence.setUpdatedBy(userId);
        evidenceMapper.updateById(evidence);

        return convertToEvidenceInfo(evidence);
    }

    /**
     * 获取证据详情
     */
    public EvidenceInfo getEvidenceById(Long id) {
        Evidence evidence = evidenceMapper.selectById(id);
        if (evidence == null || evidence.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND);
        }
        return convertToEvidenceInfo(evidence);
    }

    /**
     * 获取案件的证据列表
     */
    public List<EvidenceInfo> getEvidencesByCaseId(Long caseId) {
        LambdaQueryWrapper<Evidence> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Evidence::getCaseId, caseId)
                .eq(Evidence::getIsDeleted, 0)
                .orderByAsc(Evidence::getChainOrder)
                .orderByDesc(Evidence::getCreatedAt);

        List<Evidence> evidences = evidenceMapper.selectList(wrapper);
        return evidences.stream()
                .map(this::convertToEvidenceInfo)
                .collect(Collectors.toList());
    }

    /**
     * 删除证据
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteEvidence(Long id) {
        Long userId = SecurityUtils.getCurrentUserId();

        Evidence evidence = evidenceMapper.selectById(id);
        if (evidence == null || evidence.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND);
        }

        evidence.setIsDeleted(1);
        evidence.setUpdatedBy(userId);
        evidenceMapper.updateById(evidence);
    }

    /**
     * 转换为EvidenceInfo
     */
    private EvidenceInfo convertToEvidenceInfo(Evidence evidence) {
        EvidenceInfo info = new EvidenceInfo();
        info.setId(evidence.getId());
        info.setCaseId(evidence.getCaseId());
        info.setName(evidence.getName());
        info.setType(evidence.getType());
        info.setDescription(evidence.getDescription());
        info.setFileUrl(evidence.getFileUrl());
        info.setFileType(evidence.getFileType());
        info.setFileSize(evidence.getFileSize());
        info.setUploadTime(evidence.getUploadTime());
        info.setChainOrder(evidence.getChainOrder());
        info.setChainDescription(evidence.getChainDescription());
        info.setTenantId(evidence.getTenantId());
        info.setCreatedAt(evidence.getCreatedAt());
        info.setUpdatedAt(evidence.getUpdatedAt());
        return info;
    }
}
