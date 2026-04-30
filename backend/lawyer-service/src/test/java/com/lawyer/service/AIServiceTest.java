package com.lawyer.service;

import com.lawyer.common.dto.ai.AIChatResponse;
import com.lawyer.common.dto.ai.CaseAnalysisResponse;
import com.lawyer.common.dto.ai.DocumentGenerateResponse;
import com.lawyer.common.dto.ai.KnowledgeSearchResult;
import com.lawyer.common.client.AIServiceClient;
import com.lawyer.service.ai.service.AIChatService;
import com.lawyer.service.ai.service.AICaseAnalysisService;
import com.lawyer.service.ai.service.AIDocumentService;
import com.lawyer.service.ai.service.AIKnowledgeService;
import com.lawyer.service.cases.mapper.CaseMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * AI服务测试
 */
@ExtendWith(MockitoExtension.class)
class AIServiceTest {

    @Mock
    private AIServiceClient aiServiceClient;

    @Mock
    private CaseMapper caseMapper;

    @InjectMocks
    private AIChatService aiChatService;

    @InjectMocks
    private AIDocumentService aiDocumentService;

    @InjectMocks
    private AIKnowledgeService aiKnowledgeService;

    @InjectMocks
    private AICaseAnalysisService aiCaseAnalysisService;

    @Test
    @DisplayName("AI聊天服务 - 智能问答")
    void testAiChatService() {
        // Mock返回
        AIChatResponse mockResponse = AIChatResponse.builder()
                .sessionId("test-session")
                .reply("根据《劳动合同法》的规定...")
                .confidence(0.9)
                .build();

        when(aiServiceClient.chat(any())).thenReturn(mockResponse);

        // 执行测试
        AIChatResponse result = aiChatService.chat("违法解除怎么赔偿？", null, null, null);

        // 验证
        assertNotNull(result);
        assertEquals("test-session", result.getSessionId());
        assertTrue(result.getReply().contains("劳动合同法"));
        verify(aiServiceClient, times(1)).chat(any());
    }

    @Test
    @DisplayName("AI聊天服务 - 快速咨询")
    void testQuickConsult() {
        // Mock返回
        AIChatResponse mockResponse = AIChatResponse.builder()
                .sessionId("quick-session")
                .reply("关于加班费的计算...")
                .build();

        when(aiServiceClient.chat(any())).thenReturn(mockResponse);

        // 执行测试
        AIChatResponse result = aiChatService.quickConsult("加班费怎么计算？");

        // 验证
        assertNotNull(result);
        assertEquals("quick-session", result.getSessionId());
    }

    @Test
    @DisplayName("AI文档服务 - 生成文书")
    void testGenerateDocument() {
        // Mock返回
        DocumentGenerateResponse mockResponse = DocumentGenerateResponse.builder()
                .title("劳动仲裁申请书")
                .content("申请人：张三\n被申请人：某公司\n...")
                .build();

        when(aiServiceClient.generateDocument(any())).thenReturn(mockResponse);

        // 执行测试
        DocumentGenerateResponse result = aiDocumentService.generateDocument(
                "arbitration_application", 1L, null, "formal");

        // 验证
        assertNotNull(result);
        assertEquals("劳动仲裁申请书", result.getTitle());
        assertTrue(result.getContent().contains("申请人"));
    }

    @Test
    @DisplayName("AI知识服务 - 检索法规")
    void testSearchLaws() {
        // Mock返回
        List<KnowledgeSearchResult> mockResults = Arrays.asList(
                KnowledgeSearchResult.builder()
                        .knowledgeId(1L)
                        .docType("LAW")
                        .title("劳动合同法")
                        .content("劳动合同法内容...")
                        .score(0.95)
                        .build()
        );

        when(aiServiceClient.searchKnowledge(any())).thenReturn(mockResults);

        // 执行测试
        List<KnowledgeSearchResult> results = aiKnowledgeService.searchLaws("劳动合同法", 10);

        // 验证
        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals("LAW", results.get(0).getDocType());
    }

    @Test
    @DisplayName("AI知识服务 - 综合检索")
    void testSearchComprehensive() {
        // Mock返回
        List<KnowledgeSearchResult> mockResults = Arrays.asList(
                KnowledgeSearchResult.builder()
                        .knowledgeId(1L)
                        .docType("LAW")
                        .title("劳动合同法")
                        .score(0.95)
                        .build(),
                KnowledgeSearchResult.builder()
                        .knowledgeId(2L)
                        .docType("CASE")
                        .title("劳动争议案例")
                        .score(0.88)
                        .build()
        );

        when(aiServiceClient.searchKnowledge(any())).thenReturn(mockResults);

        // 执行测试
        List<KnowledgeSearchResult> results = aiKnowledgeService.searchComprehensive("违法解除", 10);

        // 验证
        assertNotNull(results);
        assertEquals(2, results.size());
    }

    @Test
    @DisplayName("AI案件分析服务 - 全面分析")
    void testFullAnalysis() {
        // Mock返回
        CaseAnalysisResponse mockResponse = CaseAnalysisResponse.builder()
                .caseId(1L)
                .summary("案件摘要...")
                .winProbability(0.75)
                .build();

        when(aiServiceClient.analyzeCase(any())).thenReturn(mockResponse);

        // 执行测试
        CaseAnalysisResponse result = aiCaseAnalysisService.fullAnalysis(1L);

        // 验证
        assertNotNull(result);
        assertEquals(1L, result.getCaseId());
        assertEquals(0.75, result.getWinProbability());
    }

    @Test
    @DisplayName("AI案件分析服务 - 获取案件类型")
    void testGetCaseTypes() {
        // Mock返回
        List<Map<String, Object>> mockTypes = Arrays.asList(
                Map.of("code", "illegal_termination", "name", "违法解除劳动合同"),
                Map.of("code", "overtime_pay", "name", "加班费争议")
        );

        when(aiServiceClient.getCaseTypes()).thenReturn(mockTypes);

        // 执行测试
        List<Map<String, Object>> types = aiCaseAnalysisService.getCaseTypes();

        // 验证
        assertNotNull(types);
        assertEquals(2, types.size());
        assertEquals("illegal_termination", types.get(0).get("code"));
    }
}
