package com.lawyer.service.ai.service;

import com.lawyer.common.dto.ai.*;
import com.lawyer.common.client.AIServiceClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * AI知识库服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AIKnowledgeService {

    private final AIServiceClient aiServiceClient;

    /**
     * 存储知识到向量数据库
     *
     * @param docType   文档类型
     * @param title     标题
     * @param content   内容
     * @param category  分类
     * @param tenantId  租户ID
     * @return 存储结果
     */
    public Map<String, Object> storeKnowledge(String docType, String title, String content,
                                               String category, Long tenantId) {
        KnowledgeStoreRequest request = KnowledgeStoreRequest.builder()
                .docType(docType)
                .title(title)
                .content(content)
                .category(category)
                .tenantId(tenantId)
                .build();

        return aiServiceClient.storeKnowledge(request);
    }

    /**
     * 批量存储知识
     *
     * @param requests 知识列表
     * @return 存储结果
     */
    public Map<String, Object> storeKnowledgeBatch(List<KnowledgeStoreRequest> requests) {
        return aiServiceClient.storeKnowledgeBatch(requests);
    }

    /**
     * 知识检索
     *
     * @param query    查询文本
     * @param docTypes 文档类型过滤
     * @param topK     返回数量
     * @return 检索结果
     */
    public List<KnowledgeSearchResult> searchKnowledge(String query, List<String> docTypes, Integer topK) {
        KnowledgeSearchRequest request = KnowledgeSearchRequest.builder()
                .query(query)
                .docTypes(docTypes)
                .topK(topK != null ? topK : 10)
                .minScore(0.5)
                .build();

        return aiServiceClient.searchKnowledge(request);
    }

    /**
     * 检索法规
     *
     * @param query 查询文本
     * @param topK  返回数量
     * @return 检索结果
     */
    public List<KnowledgeSearchResult> searchLaws(String query, Integer topK) {
        return searchKnowledge(query, List.of("LAW"), topK);
    }

    /**
     * 检索案例
     *
     * @param query 查询文本
     * @param topK  返回数量
     * @return 检索结果
     */
    public List<KnowledgeSearchResult> searchCases(String query, Integer topK) {
        return searchKnowledge(query, List.of("CASE"), topK);
    }

    /**
     * 检索内部资料
     *
     * @param query    查询文本
     * @param tenantId 租户ID
     * @param topK     返回数量
     * @return 检索结果
     */
    public List<KnowledgeSearchResult> searchInternal(String query, Long tenantId, Integer topK) {
        KnowledgeSearchRequest request = KnowledgeSearchRequest.builder()
                .query(query)
                .docTypes(List.of("INTERNAL"))
                .topK(topK != null ? topK : 10)
                .minScore(0.5)
                .build();

        return aiServiceClient.searchKnowledge(request);
    }

    /**
     * 综合检索（法规+案例）
     *
     * @param query 查询文本
     * @param topK  返回数量
     * @return 检索结果
     */
    public List<KnowledgeSearchResult> searchComprehensive(String query, Integer topK) {
        return searchKnowledge(query, List.of("LAW", "CASE"), topK);
    }

    /**
     * 删除知识
     *
     * @param knowledgeId 知识ID
     * @return 是否成功
     */
    public boolean deleteKnowledge(Long knowledgeId) {
        return aiServiceClient.deleteKnowledge(knowledgeId);
    }
}
