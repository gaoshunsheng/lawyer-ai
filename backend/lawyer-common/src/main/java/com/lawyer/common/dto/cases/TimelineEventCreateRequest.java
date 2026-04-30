package com.lawyer.common.dto.cases;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 创建时间线事件请求DTO
 */
@Data
public class TimelineEventCreateRequest {

    @NotNull(message = "案件ID不能为空")
    private Long caseId;

    @NotBlank(message = "事件类型不能为空")
    private String eventType;

    @NotBlank(message = "事件标题不能为空")
    private String title;

    private String description;

    @NotNull(message = "事件时间不能为空")
    private LocalDateTime eventTime;

    private Integer sortOrder;

    private String attachments;
}
