package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * AI聊天请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AIChatRequest {

    /**
     * 会话ID（可选，用于保持上下文）
     */
    private String sessionId;

    /**
     * 用户消息
     */
    private String message;

    /**
     * 上下文信息
     */
    private Map<String, Object> context;

    /**
     * 是否流式响应
     */
    private Boolean stream;
}
