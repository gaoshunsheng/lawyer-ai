package com.lawyer.api.controller;

import com.lawyer.common.result.Result;
import com.lawyer.common.dto.chat.*;
import com.lawyer.common.dto.ai.AIChatResponse;
import com.lawyer.service.chat.service.ChatService;
import com.lawyer.service.ai.service.AIChatService;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 智能咨询控制器
 */
@Tag(name = "智能咨询", description = "AI聊天咨询接口")
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;
    private final AIChatService aiChatService;
    private final UserMapper userMapper;

    /**
     * 发送聊天消息
     */
    @Operation(summary = "发送消息", description = "发送消息给AI助手并获取回复")
    @PostMapping("/message")
    public Result<ChatResponse> sendMessage(@Valid @RequestBody ChatRequest request) {
        ChatResponse response = chatService.sendMessage(request);
        return Result.success(response);
    }

    /**
     * 创建会话
     */
    @Operation(summary = "创建会话", description = "创建新的聊天会话")
    @PostMapping("/sessions")
    public Result<SessionInfo> createSession(
            @Parameter(description = "案件ID") @RequestParam(required = false) Long caseId,
            @Parameter(description = "会话标题") @RequestParam(required = false) String title) {
        SessionInfo session = chatService.createSession(caseId, title);
        return Result.success(session);
    }

    /**
     * 获取会话列表
     */
    @Operation(summary = "获取会话列表", description = "获取当前用户的聊天会话列表")
    @GetMapping("/sessions")
    public Result<List<SessionInfo>> getSessions(
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页数量") @RequestParam(defaultValue = "20") int size) {
        List<SessionInfo> sessions = chatService.getSessions(page, size);
        return Result.success(sessions);
    }

    /**
     * 获取会话消息历史
     */
    @Operation(summary = "获取消息历史", description = "获取指定会话的消息历史")
    @GetMapping("/sessions/{sessionId}/messages")
    public Result<List<MessageInfo>> getMessages(
            @Parameter(description = "会话ID") @PathVariable Long sessionId,
            @Parameter(description = "页码") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页数量") @RequestParam(defaultValue = "20") int size) {
        List<MessageInfo> messages = chatService.getMessages(sessionId, page, size);
        return Result.success(messages);
    }

    /**
     * 删除会话
     */
    @Operation(summary = "删除会话", description = "删除指定的聊天会话")
    @DeleteMapping("/sessions/{sessionId}")
    public Result<Void> deleteSession(@Parameter(description = "会话ID") @PathVariable Long sessionId) {
        chatService.deleteSession(sessionId);
        return Result.success();
    }

    /**
     * AI智能问答
     */
    @Operation(summary = "AI智能问答", description = "直接调用AI服务进行智能问答")
    @PostMapping("/ai/query")
    public Result<AIChatResponse> aiQuery(
            @Parameter(description = "问题内容") @RequestParam String message,
            @Parameter(description = "会话ID") @RequestParam(required = false) String sessionId,
            @Parameter(description = "案件ID") @RequestParam(required = false) Long caseId) {
        Long tenantId = getCurrentTenantId();
        AIChatResponse response = aiChatService.chat(message, sessionId, tenantId, caseId);
        return Result.success(response);
    }

    /**
     * 快速法律咨询
     */
    @Operation(summary = "快速法律咨询", description = "快速法律问题咨询")
    @PostMapping("/ai/quick")
    public Result<AIChatResponse> quickConsult(
            @Parameter(description = "法律问题") @RequestParam String question) {
        AIChatResponse response = aiChatService.quickConsult(question);
        return Result.success(response);
    }

    /**
     * 案件相关咨询
     */
    @Operation(summary = "案件相关咨询", description = "针对特定案件的AI咨询")
    @PostMapping("/ai/case/{caseId}")
    public Result<AIChatResponse> caseConsult(
            @Parameter(description = "案件ID") @PathVariable Long caseId,
            @Parameter(description = "问题") @RequestParam String question) {
        Long tenantId = getCurrentTenantId();
        AIChatResponse response = aiChatService.caseConsult(question, caseId, tenantId);
        return Result.success(response);
    }

    /**
     * 获取当前租户ID
     */
    private Long getCurrentTenantId() {
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                return user.getTenantId();
            }
        }
        return null;
    }
}
