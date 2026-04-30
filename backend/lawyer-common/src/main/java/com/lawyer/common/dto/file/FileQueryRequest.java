package com.lawyer.common.dto.file;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 文件查询条件DTO
 */
@Data
public class FileQueryRequest {

    /**
     * 页码
     */
    private Integer page = 1;

    /**
     * 每页数量
     */
    private Integer pageSize = 20;

    /**
     * 文件分类
     */
    private String category;

    /**
     * 关联ID
     */
    private Long relatedId;

    /**
     * 关联类型
     */
    private String relatedType;

    /**
     * 关键词（文件名）
     */
    private String keyword;

    /**
     * 文件类型
     */
    private String fileType;
}
