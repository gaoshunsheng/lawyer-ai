package com.lawyer.api.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.dto.calculator.IllegalTerminationRequest;
import com.lawyer.common.dto.calculator.OvertimePayRequest;
import com.lawyer.common.dto.calculator.AnnualLeaveRequest;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 赔偿计算器集成测试
 * 测试各项赔偿计算功能的完整流程
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class CalculatorIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @Order(1)
    @DisplayName("违法解除赔偿计算 - 标准情况")
    void testIllegalTerminationStandard() throws Exception {
        IllegalTerminationRequest request = new IllegalTerminationRequest();
        request.setEntryDate(LocalDate.of(2020, 1, 1));
        request.setLeaveDate(LocalDate.of(2024, 1, 1));
        request.setAverageSalary(new BigDecimal("15000"));
        request.setCity("上海");

        mockMvc.perform(post("/calculator/illegal-termination")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.workYears").value(4))
                .andExpect(jsonPath("$.data.economicCompensation").exists())
                .andExpect(jsonPath("$.data.illegalTerminationCompensation").exists())
                .andExpect(jsonPath("$.data.legalBasis").isArray());
    }

    @Test
    @Order(2)
    @DisplayName("违法解除赔偿计算 - 高薪封顶")
    void testIllegalTerminationHighSalary() throws Exception {
        IllegalTerminationRequest request = new IllegalTerminationRequest();
        request.setEntryDate(LocalDate.of(2018, 1, 1));
        request.setLeaveDate(LocalDate.of(2024, 1, 1));
        request.setAverageSalary(new BigDecimal("80000")); // 高薪
        request.setCity("上海");
        request.setHighSalaryCap(true);

        mockMvc.perform(post("/calculator/illegal-termination")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.highSalaryCapApplied").value(true));
    }

    @Test
    @Order(3)
    @DisplayName("违法解除赔偿计算 - 不满半年")
    void testIllegalTerminationLessThanHalfYear() throws Exception {
        IllegalTerminationRequest request = new IllegalTerminationRequest();
        request.setEntryDate(LocalDate.of(2023, 8, 1));
        request.setLeaveDate(LocalDate.of(2024, 1, 1));
        request.setAverageSalary(new BigDecimal("10000"));
        request.setCity("北京");

        mockMvc.perform(post("/calculator/illegal-termination")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.workYears").value(0));
    }

    @Test
    @Order(4)
    @DisplayName("加班费计算 - 工作日加班")
    void testOvertimePayWorkday() throws Exception {
        OvertimePayRequest request = new OvertimePayRequest();
        request.setMonthlySalary(new BigDecimal("10000"));
        request.setOvertimeType("workday");
        request.setOvertimeHours(20);

        mockMvc.perform(post("/calculator/overtime-pay")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.overtimeTypeName").value("工作日加班"))
                .andExpect(jsonPath("$.data.overtimePay").exists());
    }

    @Test
    @Order(5)
    @DisplayName("加班费计算 - 周末加班")
    void testOvertimePayWeekend() throws Exception {
        OvertimePayRequest request = new OvertimePayRequest();
        request.setMonthlySalary(new BigDecimal("10000"));
        request.setOvertimeType("weekend");
        request.setOvertimeHours(16);

        mockMvc.perform(post("/calculator/overtime-pay")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.overtimeTypeName").value("周末加班"));
    }

    @Test
    @Order(6)
    @DisplayName("加班费计算 - 法定节假日加班")
    void testOvertimePayHoliday() throws Exception {
        OvertimePayRequest request = new OvertimePayRequest();
        request.setMonthlySalary(new BigDecimal("10000"));
        request.setOvertimeType("holiday");
        request.setOvertimeHours(8);

        mockMvc.perform(post("/calculator/overtime-pay")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.overtimeTypeName").value("法定节假日加班"));
    }

    @Test
    @Order(7)
    @DisplayName("年休假工资计算")
    void testAnnualLeavePay() throws Exception {
        AnnualLeaveRequest request = new AnnualLeaveRequest();
        request.setWorkYears(5);
        request.setAnnualLeaveDays(5); // 应休天数
        request.setUsedDays(2); // 已休天数
        request.setDailySalary(new BigDecimal("500"));

        mockMvc.perform(post("/calculator/annual-leave")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.unusedDays").value(3))
                .andExpect(jsonPath("$.data.annualLeavePay").exists());
    }

    @Test
    @Order(8)
    @DisplayName("综合计算 - 多项赔偿")
    void testComprehensiveCalculation() throws Exception {
        // 这是一个综合场景测试，验证多项计算可以正常工作

        // 1. 计算违法解除赔偿
        IllegalTerminationRequest itRequest = new IllegalTerminationRequest();
        itRequest.setEntryDate(LocalDate.of(2020, 1, 1));
        itRequest.setLeaveDate(LocalDate.of(2024, 6, 1));
        itRequest.setAverageSalary(new BigDecimal("20000"));
        itRequest.setCity("上海");

        mockMvc.perform(post("/calculator/illegal-termination")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(itRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));

        // 2. 计算加班费
        OvertimePayRequest otRequest = new OvertimePayRequest();
        otRequest.setMonthlySalary(new BigDecimal("20000"));
        otRequest.setOvertimeType("workday");
        otRequest.setOvertimeHours(50);

        mockMvc.perform(post("/calculator/overtime-pay")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(otRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));

        // 3. 计算年休假工资
        AnnualLeaveRequest alRequest = new AnnualLeaveRequest();
        alRequest.setWorkYears(4);
        alRequest.setAnnualLeaveDays(5);
        alRequest.setUsedDays(0);
        alRequest.setDailySalary(new BigDecimal("919.54")); // 20000/21.75

        mockMvc.perform(post("/calculator/annual-leave")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(alRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
}
