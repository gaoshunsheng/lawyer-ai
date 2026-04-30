package com.lawyer.service.chat.service;

import com.lawyer.common.dto.chat.*;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.chat.client.AiServiceClient;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 聊天服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

    private final AiServiceClient aiServiceClient;
    private final UserMapper userMapper;

    /**
     * 发送聊天消息
     */
    public ChatResponse sendMessage(ChatRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        Long tenantId = user != null ? user.getTenantId() : null;

        return aiServiceClient.chat(request, userId, tenantId);
    }

    /**
     * 创建会话
     */
    public SessionInfo createSession(Long caseId, String title) {
        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        Long tenantId = user != null ? user.getTenantId() : null;

        Map<String, Object> result = aiServiceClient.createSession(userId, tenantId, caseId, title);

        return SessionInfo.builder()
                .id(((Number) result.get("id")).longValue())
                .userId(userId)
                .title((String) result.get("title"))
                .caseId(caseId)
                .tenantId(tenantId)
                .build();
    }

    /**
     * 获取用户的会话列表
     */
    public List<SessionInfo> getSessions(int page, int size) {
        // 调用AI服务获取会话列表
        // 实际实现中需要调用AI服务的会话列表接口
        return List.of();
    }

    /**
     * 获取会话的消息历史
     */
    public List<MessageInfo> getMessages(Long sessionId, int page, int size) {
        Map<String, Object> result = aiServiceClient.getChatHistory(sessionId, page, size);

        // 解析返回结果
        // 实际实现中需要解析AI服务返回的消息列表
        return List.of();
    }

    /**
     * 删除会话
     */
    public void deleteSession(Long sessionId) {
        // 调用AI服务删除会话
        // 实际实现中需要调用AI服务的删除会话接口
    }
}
