package com.lawyer.common.dto.cases;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 证据信息响应DTO
 */
@Data
public class EvidenceInfo {

    private Long id;

    private Long caseId;

    private String name;

    private String type;

    private String description;

    private String fileUrl;

    private String fileType;

    private Long fileSize;

    private LocalDateTime uploadTime;

    private Integer chainOrder;

    private String chainDescription;

    private Long tenantId;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
