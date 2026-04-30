package com.lawyer.service.cases.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.lawyer.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 证据实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("evidences")
public class Evidence extends BaseEntity {

    /**
     * 案件ID
     */
    private Long caseId;

    /**
     * 证据名称
     */
    private String name;

    /**
     * 证据类型
     */
    private String type;

    /**
     * 证据描述
     */
    private String description;

    /**
     * 文件URL
     */
    private String fileUrl;

    /**
     * 文件类型
     */
    private String fileType;

    /**
     * 文件大小
     */
    private Long fileSize;

    /**
     * 上传时间
     */
    private LocalDateTime uploadTime;

    /**
     * 证据链顺序
     */
    private Integer chainOrder;

    /**
     * 证据链说明
     */
    private String chainDescription;

    /**
     * 租户ID
     */
    private Long tenantId;
}
