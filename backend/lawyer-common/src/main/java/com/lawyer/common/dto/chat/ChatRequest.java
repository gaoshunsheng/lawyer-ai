package com.lawyer.common.dto.chat;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.List;

/**
 * 聊天请求DTO
 */
@Data
public class ChatRequest {

    /**
     * 会话ID（可选，新会话不传）
     */
    private Long sessionId;

    /**
     * 关联案件ID（可选）
     */
    private Long caseId;

    /**
     * 消息内容
     */
    @NotBlank(message = "消息内容不能为空")
    @Size(max = 10000, message = "消息内容长度不能超过10000个字符")
    private String content;

    /**
     * 是否流式输出
     */
    private Boolean stream = false;

    /**
     * 附件列表
     */
    private List<Attachment> attachments;

    /**
     * 附件信息
     */
    @Data
    public static class Attachment {
        private String name;
        private String type;
        private String url;
        private Long size;
    }
}
