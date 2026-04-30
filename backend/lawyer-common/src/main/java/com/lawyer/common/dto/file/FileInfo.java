package com.lawyer.common.dto.file;

import lombok.Data;

/**
 * 文件信息DTO
 */
@Data
public class FileInfo {

    private Long id;

    private String originalName;

    private String storedName;

    private String filePath;

    private String fileUrl;

    private String fileType;

    private String fileExtension;

    private Long fileSize;

    private String category;

    private Long relatedId;

    private String relatedType;

    private String description;

    private Long tenantId;

    private Long createdBy;

    private String createdByName;

    private String createdAt;
}
