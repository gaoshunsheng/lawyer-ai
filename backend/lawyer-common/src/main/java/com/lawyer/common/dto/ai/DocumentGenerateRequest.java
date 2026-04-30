package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 文书生成请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentGenerateRequest {

    /**
     * 模板ID
     */
    private String templateId;

    /**
     * 关联案件ID
     */
    private Long caseId;

    /**
     * 模板变量
     */
    private Map<String, Object> variables;

    /**
     * 文书风格：formal-正式, concise-简洁
     */
    private String style;
}
