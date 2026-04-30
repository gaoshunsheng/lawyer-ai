package com.lawyer.service.file.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.lawyer.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 文件实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("files")
public class FileEntity extends BaseEntity {

    /**
     * 原始文件名
     */
    private String originalName;

    /**
     * 存储文件名（UUID）
     */
    private String storedName;

    /**
     * 文件路径
     */
    private String filePath;

    /**
     * 文件URL
     */
    private String fileUrl;

    /**
     * 文件类型（MIME类型）
     */
    private String fileType;

    /**
     * 文件扩展名
     */
    private String fileExtension;

    /**
     * 文件大小（字节）
     */
    private Long fileSize;

    /**
     * 文件分类（evidence/document/avatar）
     */
    private String category;

    /**
     * 关联ID（案件ID、文书ID等）
     */
    private Long relatedId;

    /**
     * 关联类型（case/document）
     */
    private String relatedType;

    /**
     * 租户ID
     */
    private Long tenantId;

    /**
     * 描述
     */
    private String description;
}
