package com.lawyer.service.ai.service;

import com.lawyer.common.dto.ai.*;
import com.lawyer.common.client.AIServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AI聊天服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AIChatService {

    private final AIServiceClient aiServiceClient;

    /**
     * 智能问答
     *
     * @param message  用户消息
     * @param sessionId 会话ID（可选）
     * @param tenantId  租户ID（可选）
     * @param caseId    案件ID（可选）
     * @return AI回复
     */
    public AIChatResponse chat(String message, String sessionId, Long tenantId, Long caseId) {
        AIChatRequest request = AIChatRequest.builder()
                .message(message)
                .sessionId(sessionId)
                .context(buildContext(tenantId, caseId))
                .stream(false)
                .build();

        return aiServiceClient.chat(request);
    }

    /**
     * 智能问答（带历史上下文）
     *
     * @param message   用户消息
     * @param sessionId 会话ID
     * @param context   上下文信息
     * @return AI回复
     */
    public AIChatResponse chatWithContext(String message, String sessionId, Map<String, Object> context) {
        AIChatRequest request = AIChatRequest.builder()
                .message(message)
                .sessionId(sessionId)
                .context(context)
                .stream(false)
                .build();

        return aiServiceClient.chat(request);
    }

    /**
     * 快速法律咨询
     *
     * @param question 法律问题
     * @return AI回复
     */
    public AIChatResponse quickConsult(String question) {
        return chat(question, null, null, null);
    }

    /**
     * 案件相关咨询
     *
     * @param question 问题
     * @param caseId   案件ID
     * @param tenantId 租户ID
     * @return AI回复
     */
    public AIChatResponse caseConsult(String question, Long caseId, Long tenantId) {
        return chat(question, null, tenantId, caseId);
    }

    /**
     * 构建上下文
     */
    private Map<String, Object> buildContext(Long tenantId, Long caseId) {
        Map<String, Object> context = new HashMap<>();
        if (tenantId != null) {
            context.put("tenant_id", tenantId);
        }
        if (caseId != null) {
            context.put("case_id", caseId);
        }
        return context;
    }
}
