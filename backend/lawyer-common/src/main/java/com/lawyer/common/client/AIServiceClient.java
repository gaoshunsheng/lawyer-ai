package com.lawyer.common.client;

import com.lawyer.common.dto.ai.*;
import com.lawyer.common.config.AIServiceConfig;
import com.lawyer.common.result.Result;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

/**
 * AI服务客户端
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AIServiceClient {

    private final AIServiceConfig config;
    private final RestTemplate restTemplate;

    /**
     * 智能咨询问答
     */
    public AIChatResponse chat(AIChatRequest request) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/chat/query";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<AIChatRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<AIChatResponse> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    AIChatResponse.class
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 生成文书
     */
    public DocumentGenerateResponse generateDocument(DocumentGenerateRequest request) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/documents/generate";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<DocumentGenerateRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<DocumentGenerateResponse> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    DocumentGenerateResponse.class
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 分析文书
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> analyzeDocument(String content, String docType) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/documents/analyze?content=" + encodeUrl(content);
        if (docType != null) {
            url += "&doc_type=" + docType;
        }

        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<Void> entity = new HttpEntity<>(headers);

            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    new ParameterizedTypeReference<>() {}
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 获取文书模板列表
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getDocumentTemplates() {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/documents/templates";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<Void> entity = new HttpEntity<>(headers);

            ResponseEntity<Map<String, List<Map<String, Object>>>> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    entity,
                    new ParameterizedTypeReference<>() {}
            );

            return response.getBody() != null ? response.getBody().get("templates") : null;
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 存储知识到向量数据库
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> storeKnowledge(KnowledgeStoreRequest request) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/knowledge/store";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<KnowledgeStoreRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    new ParameterizedTypeReference<>() {}
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 批量存储知识
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> storeKnowledgeBatch(List<KnowledgeStoreRequest> requests) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/knowledge/store-batch";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<List<KnowledgeStoreRequest>> entity = new HttpEntity<>(requests, headers);

            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    new ParameterizedTypeReference<>() {}
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 知识检索
     */
    public List<KnowledgeSearchResult> searchKnowledge(KnowledgeSearchRequest request) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/knowledge/search";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<KnowledgeSearchRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<List<KnowledgeSearchResult>> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    new ParameterizedTypeReference<>() {}
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 删除知识
     */
    public boolean deleteKnowledge(Long knowledgeId) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return false;
        }

        String url = config.getUrl() + "/api/v1/knowledge/" + knowledgeId;
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<Void> entity = new HttpEntity<>(headers);

            restTemplate.exchange(url, HttpMethod.DELETE, entity, Void.class);
            return true;
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 案件分析
     */
    public CaseAnalysisResponse analyzeCase(CaseAnalysisRequest request) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/cases/analyze";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<CaseAnalysisRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<CaseAnalysisResponse> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    CaseAnalysisResponse.class
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 胜诉预测
     */
    public CasePredictionResponse predictCase(CasePredictionRequest request) {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/cases/predict";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<CasePredictionRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<CasePredictionResponse> response = restTemplate.exchange(
                    url,
                    HttpMethod.POST,
                    entity,
                    CasePredictionResponse.class
            );

            return response.getBody();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 获取案件类型列表
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getCaseTypes() {
        if (!config.getEnabled()) {
            log.warn("AI服务未启用");
            return null;
        }

        String url = config.getUrl() + "/api/v1/cases/types";
        try {
            HttpHeaders headers = buildHeaders();
            HttpEntity<Void> entity = new HttpEntity<>(headers);

            ResponseEntity<Map<String, List<Map<String, Object>>>> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    entity,
                    new ParameterizedTypeReference<>() {}
            );

            return response.getBody() != null ? response.getBody().get("types") : null;
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 健康检查
     */
    public boolean healthCheck() {
        String url = config.getUrl() + "/health";
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            log.error("AI服务健康检查失败: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 构建请求头
     */
    private HttpHeaders buildHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        return headers;
    }

    /**
     * URL编码
     */
    private String encodeUrl(String value) {
        try {
            return java.net.URLEncoder.encode(value, "UTF-8");
        } catch (Exception e) {
            return value;
        }
    }
}
