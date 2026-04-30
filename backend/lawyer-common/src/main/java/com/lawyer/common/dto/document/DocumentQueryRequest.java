package com.lawyer.common.dto.document;

import com.lawyer.common.enums.DocumentStatus;
import lombok.Data;

import java.util.Map;

/**
 * 文书查询条件DTO
 */
@Data
public class DocumentQueryRequest {

    /**
     * 页码
     */
    private Integer page = 1;

    /**
     * 每页数量
     */
    private Integer pageSize = 20;

    /**
     * 关键词搜索（标题）
     */
    private String keyword;

    /**
     * 案件ID
     */
    private Long caseId;

    /**
     * 文书类型
     */
    private String docType;

    /**
     * 文书状态
     */
    private DocumentStatus status;

    /**
     * 创建人ID
     */
    private Long createdBy;

    /**
     * 排序字段
     */
    private String sortBy = "createdAt";

    /**
     * 排序方向
     */
    private String sortOrder = "desc";
}
