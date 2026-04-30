package com.lawyer.service.document.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.lawyer.common.entity.BaseEntity;
import com.lawyer.common.enums.DocumentStatus;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 文书实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName(value = "documents", autoResultMap = true)
public class Document extends BaseEntity {

    /**
     * 关联案件ID
     */
    private Long caseId;

    /**
     * 文书类型
     */
    private String docType;

    /**
     * 文书标题
     */
    private String title;

    /**
     * 文书内容
     */
    private String content;

    /**
     * 模板ID
     */
    private Long templateId;

    /**
     * 版本号
     */
    private Integer version;

    /**
     * 文书状态
     */
    private DocumentStatus status;

    /**
     * AI建议JSON
     */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private String aiSuggestions;

    /**
     * 租户ID
     */
    private Long tenantId;
}
