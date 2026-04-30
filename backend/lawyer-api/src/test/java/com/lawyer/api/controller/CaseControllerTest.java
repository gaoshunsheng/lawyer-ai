package com.lawyer.api.controller;

import com.lawyer.api.BaseTest;
import com.lawyer.common.dto.cases.CaseCreateRequest;
import com.lawyer.common.dto.cases.CaseQueryRequest;
import com.lawyer.common.dto.cases.CaseUpdateRequest;
import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import com.lawyer.common.enums.UserRole;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import com.lawyer.service.cases.service.CaseService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 案件控制器测试
 */
class CaseControllerTest extends BaseTest {

    @MockBean
    private CaseService caseService;

    @MockBean
    private CaseMapper caseMapper;

    @Test
    @DisplayName("创建案件 - 成功")
    void testCreateCase() throws Exception {
        // 准备测试数据
        CaseCreateRequest request = new CaseCreateRequest();
        request.setCaseType(CaseType.LABOR_DISPUTE);
        request.setCaseStatus(CaseStatus.PENDING);
        request.setClaimAmount(new BigDecimal("100000"));
        request.setDescription("测试案件");

        Map<String, Object> plaintiff = new HashMap<>();
        plaintiff.put("name", "张三");
        plaintiff.put("phone", "13800138000");
        request.setPlaintiff(plaintiff);

        Map<String, Object> defendant = new HashMap<>();
        defendant.put("name", "某公司");
        defendant.put("address", "上海市浦东新区");
        request.setDefendant(defendant);

        // Mock服务返回
        when(caseService.createCase(any())).thenReturn(createMockCaseInfo());

        // 执行测试
        mockMvc.perform(post("/cases")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.caseType").value("LABOR_DISPUTE"));
    }

    @Test
    @DisplayName("获取案件详情 - 成功")
    void testGetCaseById() throws Exception {
        // Mock服务返回
        when(caseService.getCaseById(anyLong())).thenReturn(createMockCaseInfo());

        // 执行测试
        mockMvc.perform(get("/cases/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").value(1));
    }

    @Test
    @DisplayName("查询案件列表 - 成功")
    void testQueryCases() throws Exception {
        // 执行测试
        mockMvc.perform(get("/cases")
                        .param("page", "1")
                        .param("pageSize", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @DisplayName("更新案件 - 成功")
    void testUpdateCase() throws Exception {
        // 准备测试数据
        CaseUpdateRequest request = new CaseUpdateRequest();
        request.setDescription("更新后的描述");

        // Mock服务返回
        when(caseService.updateCase(anyLong(), any())).thenReturn(createMockCaseInfo());

        // 执行测试
        mockMvc.perform(put("/cases/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @DisplayName("删除案件 - 成功")
    void testDeleteCase() throws Exception {
        // 执行测试
        mockMvc.perform(delete("/cases/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    /**
     * 创建模拟案件信息
     */
    private com.lawyer.api.dto.cases.CaseInfo createMockCaseInfo() {
        return com.lawyer.api.dto.cases.CaseInfo.builder()
                .id(1L)
                .caseNumber("(2024)沪0101民初12345号")
                .caseType(CaseType.LABOR_DISPUTE)
                .caseStatus(CaseStatus.PENDING)
                .claimAmount(new BigDecimal("100000"))
                .description("测试案件")
                .build();
    }
}
