package com.lawyer.common.dto.knowledge;

import lombok.Data;

import java.util.List;

/**
 * 知识检索请求DTO
 */
@Data
public class KnowledgeSearchRequest {

    /**
     * 搜索关键词
     */
    private String keyword;

    /**
     * 文档类型
     */
    private String docType;

    /**
     * 分类
     */
    private String category;

    /**
     * 标签
     */
    private List<String> tags;

    /**
     * 是否有效（未失效）
     */
    private Boolean effective;

    /**
     * 页码
     */
    private Integer page = 1;

    /**
     * 每页数量
     */
    private Integer pageSize = 20;

    /**
     * 排序字段
     */
    private String sortBy = "createdAt";

    /**
     * 排序方向
     */
    private String sortOrder = "desc";
}
