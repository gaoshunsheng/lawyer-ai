package com.lawyer.api.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.dto.cases.CaseCreateRequest;
import com.lawyer.common.dto.cases.CaseInfo;
import com.lawyer.common.dto.cases.CaseUpdateRequest;
import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 案件管理集成测试
 * 测试完整的案件CRUD流程
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class CaseIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private static Long createdCaseId;
    private static String authToken;

    @BeforeEach
    void setUp() throws Exception {
        // 登录获取Token
        if (authToken == null) {
            Map<String, String> loginRequest = new HashMap<>();
            loginRequest.put("username", "testuser");
            loginRequest.put("password", "password123");

            // 注意：实际测试需要先创建测试用户
            // 这里假设已有测试用户
            authToken = "Bearer test-token";
        }
    }

    @Test
    @Order(1)
    @DisplayName("创建案件 - 完整流程")
    void testCreateCaseFlow() throws Exception {
        // 1. 准备案件数据
        CaseCreateRequest request = new CaseCreateRequest();
        request.setCaseType(CaseType.LABOR_DISPUTE);
        request.setCaseStatus(CaseStatus.PENDING);
        request.setClaimAmount(new BigDecimal("150000.00"));
        request.setDescription("劳动者违法解除劳动合同争议案件，公司以严重违纪为由解除，但证据不足");

        // 当事人信息
        Map<String, Object> plaintiff = new HashMap<>();
        plaintiff.put("name", "张三");
        plaintiff.put("phone", "13800138001");
        plaintiff.put("idCard", "310101199001011234");
        plaintiff.put("address", "上海市浦东新区张江高科技园区");
        request.setPlaintiff(plaintiff);

        Map<String, Object> defendant = new HashMap<>();
        defendant.put("name", "某科技有限公司");
        defendant.put("creditCode", "91310115MA1K4ABC12");
        defendant.put("address", "上海市浦东新区张江高科技园区");
        defendant.put("legalPerson", "李四");
        request.setDefendant(defendant);

        // 争议焦点
        request.setDisputeFocus(List.of("是否构成违法解除", "赔偿金计算标准", "加班费是否支持"));

        // 2. 执行创建
        MvcResult result = mockMvc.perform(post("/cases")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").exists())
                .andExpect(jsonPath("$.data.caseType").value("LABOR_DISPUTE"))
                .andExpect(jsonPath("$.data.claimAmount").value(150000.00))
                .andReturn();

        // 3. 提取案件ID
        String response = result.getResponse().getContentAsString();
        createdCaseId = objectMapper.readTree(response).path("data").path("id").asLong();
        Assertions.assertNotNull(createdCaseId, "案件ID不应为空");
    }

    @Test
    @Order(2)
    @DisplayName("查询案件详情")
    void testGetCaseDetail() throws Exception {
        mockMvc.perform(get("/cases/{id}", createdCaseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").value(createdCaseId))
                .andExpect(jsonPath("$.data.caseType").value("LABOR_DISPUTE"))
                .andExpect(jsonPath("$.data.plaintiff.name").value("张三"))
                .andExpect(jsonPath("$.data.defendant.name").value("某科技有限公司"));
    }

    @Test
    @Order(3)
    @DisplayName("更新案件信息")
    void testUpdateCase() throws Exception {
        // 1. 准备更新数据
        CaseUpdateRequest request = new CaseUpdateRequest();
        request.setDescription("案件已更新：劳动者违法解除劳动合同争议案件，公司以严重违纪为由解除，但仅有口头警告记录，证据不足");
        request.setCaseStatus(CaseStatus.ARBITRATION);

        // 2. 执行更新
        mockMvc.perform(put("/cases/{id}", createdCaseId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.caseStatus").value("ARBITRATION"));
    }

    @Test
    @Order(4)
    @DisplayName("查询案件列表")
    void testQueryCases() throws Exception {
        mockMvc.perform(get("/cases")
                        .param("page", "1")
                        .param("pageSize", "10")
                        .param("caseType", "LABOR_DISPUTE"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.records").isArray())
                .andExpect(jsonPath("$.data.records", hasSize(greaterThanOrEqualTo(1))));
    }

    @Test
    @Order(5)
    @DisplayName("查询案件统计")
    void testGetCaseStatistics() throws Exception {
        mockMvc.perform(get("/cases/statistics"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.totalCases").exists())
                .andExpect(jsonPath("$.data.ongoingCases").exists());
    }

    @Test
    @Order(6)
    @DisplayName("案件状态流转")
    void testCaseStatusTransition() throws Exception {
        // 1. 更新为仲裁阶段
        CaseUpdateRequest request1 = new CaseUpdateRequest();
        request1.setCaseStatus(CaseStatus.ARBITRATION);

        mockMvc.perform(put("/cases/{id}", createdCaseId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request1)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.caseStatus").value("ARBITRATION"));

        // 2. 更新为一审阶段
        CaseUpdateRequest request2 = new CaseUpdateRequest();
        request2.setCaseStatus(CaseStatus.FIRST_INSTANCE);

        mockMvc.perform(put("/cases/{id}", createdCaseId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request2)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.caseStatus").value("FIRST_INSTANCE"));

        // 3. 更新为已结案
        CaseUpdateRequest request3 = new CaseUpdateRequest();
        request3.setCaseStatus(CaseStatus.CLOSED);

        mockMvc.perform(put("/cases/{id}", createdCaseId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request3)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.caseStatus").value("CLOSED"));
    }

    @Test
    @Order(7)
    @DisplayName("搜索案件")
    void testSearchCases() throws Exception {
        mockMvc.perform(get("/cases")
                        .param("keyword", "张三")
                        .param("page", "1")
                        .param("pageSize", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(8)
    @DisplayName("按状态筛选案件")
    void testFilterCasesByStatus() throws Exception {
        mockMvc.perform(get("/cases")
                        .param("caseStatus", "CLOSED")
                        .param("page", "1")
                        .param("pageSize", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(9)
    @DisplayName("删除案件")
    void testDeleteCase() throws Exception {
        mockMvc.perform(delete("/cases/{id}", createdCaseId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));

        // 验证已删除 - 应返回404或已删除状态
        mockMvc.perform(get("/cases/{id}", createdCaseId))
                .andExpect(status().isNotFound());
    }

    @Test
    @Order(10)
    @DisplayName("创建案件 - 数据验证")
    void testCreateCaseValidation() throws Exception {
        // 缺少必填字段
        CaseCreateRequest request = new CaseCreateRequest();
        // 不设置任何字段

        mockMvc.perform(post("/cases")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }
}
