package com.lawyer.common.dto.knowledge;

import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 知识条目信息DTO
 */
@Data
public class KnowledgeInfo {

    private Long id;

    private String category;

    private String docType;

    private String docTypeName;

    private String title;

    private String content;

    private String source;

    private LocalDate publishDate;

    private LocalDate effectiveDate;

    private LocalDate expiryDate;

    private List<String> tags;

    private String metadata;

    private Integer viewCount;

    private Integer favoriteCount;

    private Long tenantId;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
