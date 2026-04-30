package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 知识检索请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class KnowledgeSearchRequest {

    /**
     * 检索文本
     */
    private String query;

    /**
     * 文档类型过滤
     */
    private List<String> docTypes;

    /**
     * 分类过滤
     */
    private String category;

    /**
     * 返回数量
     */
    private Integer topK;

    /**
     * 最小相似度
     */
    private Double minScore;
}
