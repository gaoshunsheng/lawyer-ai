package com.lawyer.common.dto.document;

import com.lawyer.common.enums.DocumentStatus;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 更新文书请求DTO
 */
@Data
public class DocumentUpdateRequest {

    /**
     * 文书标题
     */
    @Size(max = 200, message = "文书标题长度不能超过200个字符")
    private String title;

    /**
     * 文书内容
     */
    private String content;

    /**
     * 文书状态
     */
    private DocumentStatus status;
}
