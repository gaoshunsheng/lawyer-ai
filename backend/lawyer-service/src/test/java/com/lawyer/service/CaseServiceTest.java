package com.lawyer.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.lawyer.common.dto.cases.CaseCreateRequest;
import com.lawyer.common.dto.cases.CaseInfo;
import com.lawyer.common.dto.cases.CaseUpdateRequest;
import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import com.lawyer.service.cases.service.CaseService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * 案件服务测试
 */
@ExtendWith(MockitoExtension.class)
class CaseServiceTest {

    @Mock
    private CaseMapper caseMapper;

    @InjectMocks
    private CaseService caseService;

    private Case mockCase;
    private CaseCreateRequest createRequest;

    @BeforeEach
    void setUp() {
        // 创建模拟案件
        mockCase = new Case();
        mockCase.setId(1L);
        mockCase.setCaseNumber("(2024)沪0101民初12345号");
        mockCase.setCaseType(CaseType.LABOR_DISPUTE);
        mockCase.setCaseStatus(CaseStatus.PENDING);
        mockCase.setClaimAmount(new BigDecimal("100000"));
        mockCase.setDescription("测试案件");
        mockCase.setIsDeleted(0);

        // 创建请求
        createRequest = new CaseCreateRequest();
        createRequest.setCaseType(CaseType.LABOR_DISPUTE);
        createRequest.setCaseStatus(CaseStatus.PENDING);
        createRequest.setClaimAmount(new BigDecimal("100000"));
        createRequest.setDescription("测试案件");

        Map<String, Object> plaintiff = new HashMap<>();
        plaintiff.put("name", "张三");
        plaintiff.put("phone", "13800138000");
        createRequest.setPlaintiff(plaintiff);

        Map<String, Object> defendant = new HashMap<>();
        defendant.put("name", "某公司");
        createRequest.setDefendant(defendant);
    }

    @Test
    @DisplayName("创建案件 - 成功")
    void testCreateCase() {
        // Mock mapper
        when(caseMapper.insert(any(Case.class))).thenReturn(1);
        when(caseMapper.selectById(anyLong())).thenReturn(mockCase);

        // 执行测试
        CaseInfo result = caseService.createCase(createRequest);

        // 验证
        assertNotNull(result);
        verify(caseMapper, times(1)).insert(any(Case.class));
    }

    @Test
    @DisplayName("获取案件详情 - 成功")
    void testGetCaseById() {
        // Mock mapper
        when(caseMapper.selectById(1L)).thenReturn(mockCase);

        // 执行测试
        CaseInfo result = caseService.getCaseById(1L);

        // 验证
        assertNotNull(result);
        assertEquals(1L, result.getId());
        verify(caseMapper, times(1)).selectById(1L);
    }

    @Test
    @DisplayName("更新案件 - 成功")
    void testUpdateCase() {
        // Mock mapper
        when(caseMapper.selectById(1L)).thenReturn(mockCase);
        when(caseMapper.updateById(any(Case.class))).thenReturn(1);

        // 创建更新请求
        CaseUpdateRequest updateRequest = new CaseUpdateRequest();
        updateRequest.setDescription("更新后的描述");

        // 执行测试
        CaseInfo result = caseService.updateCase(1L, updateRequest);

        // 验证
        assertNotNull(result);
        verify(caseMapper, times(1)).updateById(any(Case.class));
    }

    @Test
    @DisplayName("删除案件 - 成功")
    void testDeleteCase() {
        // Mock mapper
        when(caseMapper.selectById(1L)).thenReturn(mockCase);
        when(caseMapper.updateById(any(Case.class))).thenReturn(1);

        // 执行测试
        caseService.deleteCase(1L);

        // 验证
        verify(caseMapper, times(1)).updateById(any(Case.class));
    }
}
