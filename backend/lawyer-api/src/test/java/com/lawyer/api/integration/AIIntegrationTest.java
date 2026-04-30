package com.lawyer.api.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * AI功能集成测试
 * 测试AI聊天、知识检索、案件分析等功能的集成
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class AIIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @Order(1)
    @DisplayName("AI智能问答 - 基础咨询")
    void testAIChatQuery() throws Exception {
        mockMvc.perform(post("/chat/ai/query")
                        .param("message", "违法解除劳动合同怎么赔偿？")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.sessionId").exists())
                .andExpect(jsonPath("$.data.reply").exists());
    }

    @Test
    @Order(2)
    @DisplayName("AI智能问答 - 快速咨询")
    void testAIQuickConsult() throws Exception {
        mockMvc.perform(post("/chat/ai/quick")
                        .param("question", "加班费怎么计算？")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.reply").exists());
    }

    @Test
    @Order(3)
    @DisplayName("AI智能问答 - 案件相关咨询")
    void testAICaseConsult() throws Exception {
        Long caseId = 1L;

        mockMvc.perform(post("/chat/ai/case/{caseId}", caseId)
                        .param("question", "这个案件的胜诉概率如何？")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(4)
    @DisplayName("AI知识检索 - 综合检索")
    void testAIKnowledgeSearch() throws Exception {
        Map<String, Object> request = new HashMap<>();
        request.put("query", "劳动合同法违法解除");
        request.put("topK", 10);

        mockMvc.perform(post("/knowledge/ai/search")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(5)
    @DisplayName("AI知识检索 - 法规检索")
    void testAISearchLaws() throws Exception {
        mockMvc.perform(get("/knowledge/ai/laws")
                        .param("query", "劳动合同法")
                        .param("topK", "5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(6)
    @DisplayName("AI知识检索 - 案例检索")
    void testAISearchCases() throws Exception {
        mockMvc.perform(get("/knowledge/ai/cases")
                        .param("query", "违法解除劳动争议")
                        .param("topK", "5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(7)
    @DisplayName("AI案件分析 - 全面分析")
    void testAICaseAnalysis() throws Exception {
        Long caseId = 1L;

        mockMvc.perform(post("/ai/cases/analyze/{caseId}", caseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.caseId").value(caseId));
    }

    @Test
    @Order(8)
    @DisplayName("AI案件分析 - 风险分析")
    void testAICaseRiskAnalysis() throws Exception {
        Long caseId = 1L;

        mockMvc.perform(post("/ai/cases/risk/{caseId}", caseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(9)
    @DisplayName("AI案件分析 - 策略建议")
    void testAICaseStrategyAnalysis() throws Exception {
        Long caseId = 1L;

        mockMvc.perform(post("/ai/cases/strategy/{caseId}", caseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(10)
    @DisplayName("AI胜诉预测 - 案件预测")
    void testAICasePrediction() throws Exception {
        Long caseId = 1L;

        mockMvc.perform(post("/ai/cases/predict/{caseId}", caseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.probability").exists());
    }

    @Test
    @Order(11)
    @DisplayName("AI胜诉预测 - 自定义案情预测")
    void testAICasePredictionByDescription() throws Exception {
        mockMvc.perform(post("/ai/cases/predict")
                        .param("caseDescription", "劳动者在公司工作3年后被以严重违纪为由解除，但公司仅有口头警告记录")
                        .param("caseType", "illegal_termination")
                        .param("plaintiffType", "employee"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.probability").isNumber());
    }

    @Test
    @Order(12)
    @DisplayName("获取AI案件类型列表")
    void testGetAICaseTypes() throws Exception {
        mockMvc.perform(get("/ai/cases/types"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data[0].code").exists())
                .andExpect(jsonPath("$.data[0].name").exists());
    }

    @Test
    @Order(13)
    @DisplayName("获取AI文书模板列表")
    void testGetAIDocumentTemplates() throws Exception {
        mockMvc.perform(get("/documents/ai/templates"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data").isArray());
    }

    @Test
    @Order(14)
    @DisplayName("存储知识到AI向量库")
    void testStoreKnowledgeToAI() throws Exception {
        mockMvc.perform(post("/knowledge/ai/store")
                        .param("docType", "LAW")
                        .param("title", "劳动合同法")
                        .param("content", "中华人民共和国劳动合同法...")
                        .param("category", "劳动法规"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
}
