package com.lawyer.common.dto.document;

import lombok.Data;

import java.util.Map;

/**
 * AI生成文书请求DTO
 */
@Data
public class DocumentGenerateRequest {

    /**
     * 模板ID
     */
    private Long templateId;

    /**
     * 案件ID
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
     * 额外参数
     */
    private Map<String, Object> extraParams;
}
