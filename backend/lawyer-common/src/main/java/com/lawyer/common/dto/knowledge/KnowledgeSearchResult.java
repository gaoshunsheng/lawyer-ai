package com.lawyer.common.dto.knowledge;

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
     * 知识条目ID
     */
    private Long id;

    /**
     * 标题
     */
    private String title;

    /**
     * 摘要
     */
    private String summary;

    /**
     * 文档类型
     */
    private String docType;

    /**
     * 分类
     */
    private String category;

    /**
     * 来源
     */
    private String source;

    /**
     * 相似度得分
     */
    private Double score;

    /**
     * 高亮内容
     */
    private String highlight;
}
