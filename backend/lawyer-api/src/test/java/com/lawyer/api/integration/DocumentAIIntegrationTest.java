package com.lawyer.api.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.dto.document.DocumentCreateRequest;
import com.lawyer.common.dto.document.DocumentInfo;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 文书与AI集成测试
 * 测试文书管理和AI生成功能的集成
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class DocumentAIIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private static Long createdDocumentId;
    private static Long testCaseId = 1L;

    @Test
    @Order(1)
    @DisplayName("创建文书 - 基础流程")
    void testCreateDocument() throws Exception {
        DocumentCreateRequest request = new DocumentCreateRequest();
        request.setTitle("劳动仲裁申请书");
        request.setDocType("ARBITRATION_APPLICATION");
        request.setCaseId(testCaseId);
        request.setContent("申请人：张三\n被申请人：某科技公司\n仲裁请求：支付违法解除赔偿金15万元...");

        MvcResult result = mockMvc.perform(post("/documents")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").exists())
                .andReturn();

        String response = result.getResponse().getContentAsString();
        createdDocumentId = objectMapper.readTree(response).path("data").path("id").asLong();
    }

    @Test
    @Order(2)
    @DisplayName("获取文书详情")
    void testGetDocument() throws Exception {
        mockMvc.perform(get("/documents/{id}", createdDocumentId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").value(createdDocumentId))
                .andExpect(jsonPath("$.data.title").value("劳动仲裁申请书"));
    }

    @Test
    @Order(3)
    @DisplayName("更新文书内容")
    void testUpdateDocument() throws Exception {
        Map<String, Object> updateRequest = new HashMap<>();
        updateRequest.put("content", "更新后的文书内容...");
        updateRequest.put("status", "REVIEW");

        mockMvc.perform(put("/documents/{id}", createdDocumentId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(4)
    @DisplayName("查询文书模板列表")
    void testGetTemplates() throws Exception {
        mockMvc.perform(get("/templates"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data").isArray());
    }

    @Test
    @Order(5)
    @DisplayName("AI生成文书 - 仲裁申请书")
    void testAIGenerateArbitrationApplication() throws Exception {
        // 注意：此测试需要AI服务可用
        mockMvc.perform(post("/documents/ai/arbitration/{caseId}", testCaseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.title").exists())
                .andExpect(jsonPath("$.data.content").exists());
    }

    @Test
    @Order(6)
    @DisplayName("AI生成文书 - 起诉状")
    void testAIGenerateComplaint() throws Exception {
        mockMvc.perform(post("/documents/ai/complaint/{caseId}", testCaseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(7)
    @DisplayName("AI生成文书 - 律师函")
    void testAIGenerateLawyerLetter() throws Exception {
        Map<String, Object> variables = new HashMap<>();
        variables.put("委托人", "张三");
        variables.put("收函人", "某科技公司");
        variables.put("函告事项", "催告支付劳动报酬");

        mockMvc.perform(post("/documents/ai/lawyer-letter")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(variables)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(8)
    @DisplayName("AI分析文书")
    void testAIAnalyzeDocument() throws Exception {
        String content = "劳动仲裁申请书\n申请人：张三\n被申请人：某科技公司\n仲裁请求：支付违法解除赔偿金";

        mockMvc.perform(post("/documents/ai/analyze")
                        .param("content", content)
                        .param("docType", "ARBITRATION_APPLICATION"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(9)
    @DisplayName("获取案件关联文书")
    void testGetDocumentsByCase() throws Exception {
        mockMvc.perform(get("/documents/case/{caseId}", testCaseId)
                        .param("page", "1")
                        .param("pageSize", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.records").isArray());
    }

    @Test
    @Order(10)
    @DisplayName("删除文书")
    void testDeleteDocument() throws Exception {
        mockMvc.perform(delete("/documents/{id}", createdDocumentId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
}
