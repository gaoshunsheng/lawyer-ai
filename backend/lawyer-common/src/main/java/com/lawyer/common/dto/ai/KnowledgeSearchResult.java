package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 知识检索结果DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class KnowledgeSearchResult {

    /**
     * 知识ID
     */
    private Long knowledgeId;

    /**
     * 文档类型
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
     * 相似度分数
     */
    private Double score;

    /**
     * 高亮片段
     */
    private String highlight;
}
