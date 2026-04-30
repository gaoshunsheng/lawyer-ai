package com.lawyer.service.cases.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import com.lawyer.service.cases.entity.TimelineEventEntity;
import com.lawyer.service.cases.mapper.TimelineEventMapper;
import com.lawyer.common.dto.cases.TimelineEvent;
import com.lawyer.common.dto.cases.TimelineEventCreateRequest;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 时间线服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TimelineService {

    private final TimelineEventMapper timelineEventMapper;
    private final CaseMapper caseMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;

    // 事件类型
    public static final String EVENT_TYPE_CASE_CREATE = "case_create";
    public static final String EVENT_TYPE_CASE_UPDATE = "case_update";
    public static final String EVENT_TYPE_EVIDENCE_ADD = "evidence_add";
    public static final String EVENT_TYPE_DOCUMENT_CREATE = "document_create";
    public static final String EVENT_TYPE_DOCUMENT_SUBMIT = "document_submit";
    public static final String EVENT_TYPE_HEARING = "hearing";
    public static final String EVENT_TYPE_JUDGMENT = "judgment";
    public static final String EVENT_TYPE_OTHER = "other";

    /**
     * 添加时间线事件
     */
    @Transactional(rollbackFor = Exception.class)
    public TimelineEvent addEvent(TimelineEventCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        // 验证案件存在
        Case caseEntity = caseMapper.selectById(request.getCaseId());
        if (caseEntity == null || caseEntity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.CASE_NOT_FOUND);
        }

        TimelineEventEntity entity = new TimelineEventEntity();
        entity.setCaseId(request.getCaseId());
        entity.setEventType(request.getEventType());
        entity.setTitle(request.getTitle());
        entity.setDescription(request.getDescription());
        entity.setEventTime(request.getEventTime());
        entity.setSortOrder(request.getSortOrder() != null ? request.getSortOrder() : 0);
        entity.setAttachments(request.getAttachments());
        entity.setCreatedBy(userId);
        entity.setUpdatedBy(userId);

        timelineEventMapper.insert(entity);

        return convertToDto(entity);
    }

    /**
     * 批量添加时间线事件
     */
    @Transactional(rollbackFor = Exception.class)
    public List<TimelineEvent> addEvents(Long caseId, List<TimelineEventCreateRequest> events) {
        return events.stream()
                .map(event -> {
                    event.setCaseId(caseId);
                    return addEvent(event);
                })
                .collect(Collectors.toList());
    }

    /**
     * 更新时间线事件
     */
    @Transactional(rollbackFor = Exception.class)
    public TimelineEvent updateEvent(Long id, TimelineEventCreateRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();

        TimelineEventEntity entity = timelineEventMapper.selectById(id);
        if (entity == null || entity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND, "时间线事件不存在");
        }

        if (request.getEventType() != null) {
            entity.setEventType(request.getEventType());
        }
        if (request.getTitle() != null) {
            entity.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            entity.setDescription(request.getDescription());
        }
        if (request.getEventTime() != null) {
            entity.setEventTime(request.getEventTime());
        }
        if (request.getSortOrder() != null) {
            entity.setSortOrder(request.getSortOrder());
        }
        if (request.getAttachments() != null) {
            entity.setAttachments(request.getAttachments());
        }
        entity.setUpdatedBy(userId);

        timelineEventMapper.updateById(entity);

        return convertToDto(entity);
    }

    /**
     * 删除时间线事件
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteEvent(Long id) {
        Long userId = SecurityUtils.getCurrentUserId();

        TimelineEventEntity entity = timelineEventMapper.selectById(id);
        if (entity == null || entity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND, "时间线事件不存在");
        }

        entity.setIsDeleted(1);
        entity.setUpdatedBy(userId);
        timelineEventMapper.updateById(entity);
    }

    /**
     * 获取案件时间线
     */
    public List<TimelineEvent> getCaseTimeline(Long caseId) {
        LambdaQueryWrapper<TimelineEventEntity> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(TimelineEventEntity::getCaseId, caseId)
                .eq(TimelineEventEntity::getIsDeleted, 0)
                .orderByAsc(TimelineEventEntity::getEventTime)
                .orderByAsc(TimelineEventEntity::getSortOrder);

        List<TimelineEventEntity> events = timelineEventMapper.selectList(wrapper);
        return events.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * 添加案件创建事件
     */
    @Transactional(rollbackFor = Exception.class)
    public void addCaseCreateEvent(Long caseId, String caseTitle) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        String userName = user != null ? user.getRealName() : "系统";

        TimelineEventEntity entity = new TimelineEventEntity();
        entity.setCaseId(caseId);
        entity.setEventType(EVENT_TYPE_CASE_CREATE);
        entity.setTitle("案件创建");
        entity.setDescription(String.format("%s 创建了案件【%s】", userName, caseTitle));
        entity.setEventTime(LocalDateTime.now());
        entity.setCreatedBy(userId);
        entity.setUpdatedBy(userId);

        timelineEventMapper.insert(entity);
    }

    /**
     * 添加案件状态变更事件
     */
    @Transactional(rollbackFor = Exception.class)
    public void addCaseStatusChangeEvent(Long caseId, String oldStatus, String newStatus) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        String userName = user != null ? user.getRealName() : "系统";

        TimelineEventEntity entity = new TimelineEventEntity();
        entity.setCaseId(caseId);
        entity.setEventType(EVENT_TYPE_CASE_UPDATE);
        entity.setTitle("案件状态变更");
        entity.setDescription(String.format("%s 将案件状态从【%s】变更为【%s】", userName, oldStatus, newStatus));
        entity.setEventTime(LocalDateTime.now());
        entity.setCreatedBy(userId);
        entity.setUpdatedBy(userId);

        timelineEventMapper.insert(entity);
    }

    /**
     * 添加证据添加事件
     */
    @Transactional(rollbackFor = Exception.class)
    public void addEvidenceEvent(Long caseId, String evidenceName) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        String userName = user != null ? user.getRealName() : "系统";

        TimelineEventEntity entity = new TimelineEventEntity();
        entity.setCaseId(caseId);
        entity.setEventType(EVENT_TYPE_EVIDENCE_ADD);
        entity.setTitle("添加证据");
        entity.setDescription(String.format("%s 添加了证据【%s】", userName, evidenceName));
        entity.setEventTime(LocalDateTime.now());
        entity.setCreatedBy(userId);
        entity.setUpdatedBy(userId);

        timelineEventMapper.insert(entity);
    }

    /**
     * 添加文书创建事件
     */
    @Transactional(rollbackFor = Exception.class)
    public void addDocumentEvent(Long caseId, String documentName, String action) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        String userName = user != null ? user.getRealName() : "系统";

        TimelineEventEntity entity = new TimelineEventEntity();
        entity.setCaseId(caseId);
        entity.setEventType(EVENT_TYPE_DOCUMENT_CREATE);
        entity.setTitle("文书操作");
        entity.setDescription(String.format("%s %s了文书【%s】", userName, action, documentName));
        entity.setEventTime(LocalDateTime.now());
        entity.setCreatedBy(userId);
        entity.setUpdatedBy(userId);

        timelineEventMapper.insert(entity);
    }

    /**
     * 转换为DTO
     */
    private TimelineEvent convertToDto(TimelineEventEntity entity) {
        TimelineEvent dto = new TimelineEvent();
        dto.setId(entity.getId());
        dto.setCaseId(entity.getCaseId());
        dto.setEventType(entity.getEventType());
        dto.setEventTypeName(getEventTypeName(entity.getEventType()));
        dto.setTitle(entity.getTitle());
        dto.setDescription(entity.getDescription());
        dto.setEventTime(entity.getEventTime());
        dto.setSortOrder(entity.getSortOrder());
        dto.setAttachments(entity.getAttachments());
        dto.setCreatedAt(entity.getCreatedAt());

        if (entity.getCreatedBy() != null) {
            User user = userMapper.selectById(entity.getCreatedBy());
            if (user != null) {
                dto.setCreatedByName(user.getRealName());
            }
        }

        return dto;
    }

    /**
     * 获取事件类型名称
     */
    private String getEventTypeName(String eventType) {
        switch (eventType) {
            case EVENT_TYPE_CASE_CREATE:
                return "案件创建";
            case EVENT_TYPE_CASE_UPDATE:
                return "案件更新";
            case EVENT_TYPE_EVIDENCE_ADD:
                return "证据添加";
            case EVENT_TYPE_DOCUMENT_CREATE:
                return "文书创建";
            case EVENT_TYPE_DOCUMENT_SUBMIT:
                return "文书提交";
            case EVENT_TYPE_HEARING:
                return "开庭审理";
            case EVENT_TYPE_JUDGMENT:
                return "裁判结果";
            case EVENT_TYPE_OTHER:
                return "其他";
            default:
                return eventType;
        }
    }
}
