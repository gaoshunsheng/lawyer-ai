package com.lawyer.api.controller;

import com.lawyer.api.BaseTest;
import com.lawyer.common.dto.ai.AIChatResponse;
import com.lawyer.common.dto.knowledge.KnowledgeSearchResult;
import com.lawyer.service.ai.service.AIChatService;
import com.lawyer.service.ai.service.AIKnowledgeService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;

import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * AI控制器测试
 */
class AIControllerTest extends BaseTest {

    @MockBean
    private AIChatService aiChatService;

    @MockBean
    private AIKnowledgeService aiKnowledgeService;

    @Test
    @DisplayName("AI智能问答 - 成功")
    void testAiQuery() throws Exception {
        // Mock服务返回
        AIChatResponse mockResponse = AIChatResponse.builder()
                .sessionId("test-session-id")
                .reply("根据《劳动合同法》的规定，用人单位违法解除劳动合同...")
                .confidence(0.85)
                .suggestedQuestions(Arrays.asList("经济补偿金如何计算？", "如何申请劳动仲裁？"))
                .build();

        when(aiChatService.chat(anyString(), any(), any(), any())).thenReturn(mockResponse);

        // 执行测试
        mockMvc.perform(post("/chat/ai/query")
                        .param("message", "违法解除怎么赔偿？")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.sessionId").value("test-session-id"));
    }

    @Test
    @DisplayName("快速法律咨询 - 成功")
    void testQuickConsult() throws Exception {
        // Mock服务返回
        AIChatResponse mockResponse = AIChatResponse.builder()
                .sessionId("quick-session-id")
                .reply("关于加班费的计算标准...")
                .build();

        when(aiChatService.quickConsult(anyString())).thenReturn(mockResponse);

        // 执行测试
        mockMvc.perform(post("/chat/ai/quick")
                        .param("question", "加班费怎么计算？")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @DisplayName("AI检索法规 - 成功")
    void testAiSearchLaws() throws Exception {
        // Mock服务返回
        List<KnowledgeSearchResult> mockResults = Arrays.asList(
                KnowledgeSearchResult.builder()
                        .knowledgeId(1L)
                        .docType("LAW")
                        .title("中华人民共和国劳动合同法")
                        .content("劳动合同法内容...")
                        .score(0.95)
                        .build()
        );

        when(aiKnowledgeService.searchLaws(anyString(), any())).thenReturn(mockResults);

        // 执行测试
        mockMvc.perform(get("/knowledge/ai/laws")
                        .param("query", "劳动合同法")
                        .param("topK", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data[0].docType").value("LAW"));
    }

    @Test
    @DisplayName("AI检索案例 - 成功")
    void testAiSearchCases() throws Exception {
        // Mock服务返回
        List<KnowledgeSearchResult> mockResults = Arrays.asList(
                KnowledgeSearchResult.builder()
                        .knowledgeId(2L)
                        .docType("CASE")
                        .title("张三诉某公司劳动争议案")
                        .content("案例内容...")
                        .score(0.88)
                        .build()
        );

        when(aiKnowledgeService.searchCases(anyString(), any())).thenReturn(mockResults);

        // 执行测试
        mockMvc.perform(get("/knowledge/ai/cases")
                        .param("query", "违法解除")
                        .param("topK", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data[0].docType").value("CASE"));
    }
}
