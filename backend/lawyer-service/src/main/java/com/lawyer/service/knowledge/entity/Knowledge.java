package com.lawyer.service.knowledge.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.lawyer.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDate;

/**
 * 知识库实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("knowledge_base")
public class Knowledge extends BaseEntity {

    /**
     * 分类
     */
    private String category;

    /**
     * 文档类型：LAW-法规，CASE-案例，INTERNAL-内部资料
     */
    private String docType;

    /**
     * 标题
     */
    private String title;

    /**
     * 内容
     */
    private String content;

    /**
     * 来源
     */
    private String source;

    /**
     * 发布日期
     */
    private LocalDate publishDate;

    /**
     * 生效日期
     */
    private LocalDate effectiveDate;

    /**
     * 失效日期
     */
    private LocalDate expiryDate;

    /**
     * 标签
     */
    private String tags;

    /**
     * 元数据JSON
     */
    private String metadata;

    /**
     * 查看次数
     */
    private Integer viewCount;

    /**
     * 收藏次数
     */
    private Integer favoriteCount;

    /**
     * 租户ID（空表示公共知识库）
     */
    private Long tenantId;
}
