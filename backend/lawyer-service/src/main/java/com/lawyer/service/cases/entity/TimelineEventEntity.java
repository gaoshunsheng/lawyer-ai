package com.lawyer.service.cases.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.lawyer.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 时间线事件实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("timeline_events")
public class TimelineEventEntity extends BaseEntity {

    /**
     * 案件ID
     */
    private Long caseId;

    /**
     * 事件类型
     */
    private String eventType;

    /**
     * 事件标题
     */
    private String title;

    /**
     * 事件描述
     */
    private String description;

    /**
     * 事件时间
     */
    private LocalDateTime eventTime;

    /**
     * 排序
     */
    private Integer sortOrder;

    /**
     * 附件（JSON）
     */
    private String attachments;
}
