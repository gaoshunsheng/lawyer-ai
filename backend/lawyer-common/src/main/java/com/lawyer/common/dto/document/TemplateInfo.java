package com.lawyer.common.dto.document;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 文书模板信息DTO
 */
@Data
public class TemplateInfo {

    private Long id;

    private String name;

    private String docType;

    private String docTypeName;

    private String content;

    private String variables;

    private String category;

    private String description;

    private Integer isPublic;

    private Long tenantId;

    private Integer useCount;

    private BigDecimal rating;

    private LocalDateTime createdAt;
}
