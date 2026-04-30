package com.lawyer.common.dto.document;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.Map;

/**
 * 创建文书请求DTO
 */
@Data
public class DocumentCreateRequest {

    /**
     * 模板ID
     */
    @NotNull(message = "模板ID不能为空")
    private Long templateId;

    /**
     * 关联案件ID
     */
    private Long caseId;

    /**
     * 文书标题
     */
    @NotBlank(message = "文书标题不能为空")
    @Size(max = 200, message = "文书标题长度不能超过200个字符")
    private String title;

    /**
     * 变量值
     */
    private Map<String, Object> variables;
}
