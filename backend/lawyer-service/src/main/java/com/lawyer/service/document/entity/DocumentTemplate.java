package com.lawyer.service.document.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.lawyer.common.entity.BaseEntity;
import com.lawyer.common.enums.DocumentStatus;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 文书模板实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName(value = "document_templates", autoResultMap = true)
public class DocumentTemplate extends BaseEntity {

    /**
     * 模板名称
     */
    private String name;

    /**
     * 文书类型
     */
    private String docType;

    /**
     * 模板内容
     */
    private String content;

    /**
     * 变量定义JSON
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private String variables;

    /**
     * 分类
     */
    private String category;

    /**
     * 描述
     */
    private String description;

    /**
     * 是否公开：0-否，1-是
     */
    private Integer isPublic;

    /**
     * 租户ID（空表示系统模板）
     */
    private Long tenantId;

    /**
     * 使用次数
     */
    private Integer useCount;

    /**
     * 评分
     */
    private java.math.BigDecimal rating;
}
