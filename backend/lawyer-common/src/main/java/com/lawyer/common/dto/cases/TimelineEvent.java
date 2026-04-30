package com.lawyer.common.dto.cases;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 时间线事件DTO
 */
@Data
public class TimelineEvent {

    private Long id;

    private Long caseId;

    private String eventType;

    private String eventTypeName;

    private String title;

    private String description;

    private LocalDateTime eventTime;

    private Integer sortOrder;

    private String attachments;

    private String createdBy;

    private String createdByName;

    private LocalDateTime createdAt;
}
