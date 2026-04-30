package com.lawyer.service.chat.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.dto.chat.ChatRequest;
import com.lawyer.common.dto.chat.ChatResponse;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

/**
 * AI服务客户端
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AiServiceClient {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    /**
     * 发送聊天消息
     */
    public ChatResponse chat(ChatRequest request, Long userId, Long tenantId) {
        try {
            String url = aiServiceUrl + "/api/v1/chat/message";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("X-User-Id", String.valueOf(userId));
            headers.set("X-Tenant-Id", String.valueOf(tenantId));

            HttpEntity<ChatRequest> entity = new HttpEntity<>(request, headers);

            log.info("发送聊天请求到AI服务: {}", url);
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                if (body.get("data") != null) {
                    return objectMapper.convertValue(body.get("data"), ChatResponse.class);
                }
            }

            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage(), e);
            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        }
    }

    /**
     * 创建聊天会话
     */
    public Map<String, Object> createSession(Long userId, Long tenantId, Long caseId, String title) {
        try {
            String url = aiServiceUrl + "/api/v1/chat/sessions";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("X-User-Id", String.valueOf(userId));
            headers.set("X-Tenant-Id", String.valueOf(tenantId));

            Map<String, Object> body = Map.of(
                    "caseId", caseId != null ? caseId : 0,
                    "title", title != null ? title : "新会话"
            );

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

            log.info("创建聊天会话: {}", url);
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return (Map<String, Object>) response.getBody().get("data");
            }

            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("创建聊天会话失败: {}", e.getMessage(), e);
            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        }
    }

    /**
     * 获取聊天历史
     */
    public Map<String, Object> getChatHistory(Long sessionId, int page, int size) {
        try {
            String url = aiServiceUrl + "/api/v1/chat/sessions/" + sessionId + "/messages?page=" + page + "&size=" + size;

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Void> entity = new HttpEntity<>(headers);

            log.info("获取聊天历史: {}", url);
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.GET, entity, Map.class);

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return response.getBody();
            }

            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("获取聊天历史失败: {}", e.getMessage(), e);
            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        }
    }

    /**
     * RAG检索
     */
    public Map<String, Object> searchKnowledge(String query, String docType, int topK, Long tenantId) {
        try {
            String url = aiServiceUrl + "/api/v1/rag/search";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            if (tenantId != null) {
                headers.set("X-Tenant-Id", String.valueOf(tenantId));
            }

            Map<String, Object> body = Map.of(
                    "query", query,
                    "docType", docType != null ? docType : "",
                    "topK", topK
            );

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

            log.info("RAG检索: {}", url);
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return response.getBody();
            }

            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("RAG检索失败: {}", e.getMessage(), e);
            throw new BusinessException(ResultCode.AI_SERVICE_UNAVAILABLE);
        }
    }
}
