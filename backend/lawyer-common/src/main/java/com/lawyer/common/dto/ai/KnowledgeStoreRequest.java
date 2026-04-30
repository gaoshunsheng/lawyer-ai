package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 知识存储请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class KnowledgeStoreRequest {

    /**
     * 文档类型：LAW-法规, CASE-案例, INTERNAL-内部资料, TEMPLATE-模板
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
     * 分类
     */
    private String category;

    /**
     * 标签
     */
    private List<String> tags;

    /**
     * 来源
     */
    private String source;

    /**
     * 租户ID
     */
    private Long tenantId;
}
