package com.lawyer.common.dto.document;

import com.lawyer.common.enums.DocumentStatus;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 文书信息响应DTO
 */
@Data
public class DocumentInfo {

    private Long id;

    private Long caseId;

    private String caseTitle;

    private String docType;

    private String docTypeName;

    private String title;

    private String content;

    private Long templateId;

    private String templateName;

    private Integer version;

    private DocumentStatus status;

    private String statusName;

    private String aiSuggestions;

    private Long tenantId;

    private Long createdBy;

    private String createdByName;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
