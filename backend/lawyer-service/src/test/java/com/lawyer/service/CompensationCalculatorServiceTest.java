package com.lawyer.service;

import com.lawyer.common.dto.calculator.IllegalTerminationRequest;
import com.lawyer.common.dto.calculator.IllegalTerminationResult;
import com.lawyer.common.dto.calculator.OvertimePayRequest;
import com.lawyer.common.dto.calculator.OvertimePayResult;
import com.lawyer.service.calculator.service.CompensationCalculatorService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 赔偿计算器服务测试
 */
@ExtendWith(MockitoExtension.class)
class CompensationCalculatorServiceTest {

    @InjectMocks
    private CompensationCalculatorService calculatorService;

    @Test
    @DisplayName("计算违法解除赔偿金 - 标准情况")
    void testCalculateIllegalTermination_StandardCase() {
        // 准备测试数据
        IllegalTerminationRequest request = new IllegalTerminationRequest();
        request.setEntryDate(LocalDate.of(2020, 1, 1));
        request.setLeaveDate(LocalDate.of(2024, 1, 1)); // 工作满4年
        request.setAverageSalary(new BigDecimal("10000")); // 月均工资1万
        request.setCity("上海");

        // 执行测试
        IllegalTerminationResult result = calculatorService.calculateIllegalTermination(request);

        // 验证
        assertNotNull(result);
        assertEquals(4, result.getWorkYears());
        assertEquals(0, result.getWorkMonths());
        assertEquals(new BigDecimal("40000.00"), result.getEconomicCompensation());
        assertEquals(new BigDecimal("80000.00"), result.getIllegalTerminationCompensation());
        assertNotNull(result.getLegalBasis());
        assertTrue(result.getLegalBasis().size() > 0);
    }

    @Test
    @DisplayName("计算违法解除赔偿金 - 不满半年")
    void testCalculateIllegalTermination_LessThanHalfYear() {
        // 准备测试数据
        IllegalTerminationRequest request = new IllegalTerminationRequest();
        request.setEntryDate(LocalDate.of(2023, 8, 1));
        request.setLeaveDate(LocalDate.of(2024, 1, 1)); // 工作5个月
        request.setAverageSalary(new BigDecimal("10000"));
        request.setCity("上海");

        // 执行测试
        IllegalTerminationResult result = calculatorService.calculateIllegalTermination(request);

        // 验证
        assertNotNull(result);
        assertEquals(0, result.getWorkYears());
        assertEquals(5, result.getWorkMonths());
        // 不满半年按半年计算，0.5个月经济补偿
        assertEquals(new BigDecimal("5000.00"), result.getEconomicCompensation());
        assertEquals(new BigDecimal("10000.00"), result.getIllegalTerminationCompensation());
    }

    @Test
    @DisplayName("计算违法解除赔偿金 - 高薪封顶")
    void testCalculateIllegalTermination_HighSalary() {
        // 准备测试数据
        IllegalTerminationRequest request = new IllegalTerminationRequest();
        request.setEntryDate(LocalDate.of(2020, 1, 1));
        request.setLeaveDate(LocalDate.of(2024, 1, 1));
        request.setAverageSalary(new BigDecimal("50000")); // 高薪
        request.setCity("上海");
        request.setHighSalaryCap(true);

        // 执行测试
        IllegalTerminationResult result = calculatorService.calculateIllegalTermination(request);

        // 验证
        assertNotNull(result);
        assertTrue(result.getHighSalaryCapApplied());
        // 高薪封顶按三倍社平工资计算
        assertNotNull(result.getCappedSalary());
    }

    @Test
    @DisplayName("计算加班费 - 工作日加班")
    void testCalculateOvertimePay_Workday() {
        // 准备测试数据
        OvertimePayRequest request = new OvertimePayRequest();
        request.setMonthlySalary(new BigDecimal("10000"));
        request.setOvertimeType("workday");
        request.setOvertimeHours(10);

        // 执行测试
        OvertimePayResult result = calculatorService.calculateOvertimePay(request);

        // 验证
        assertNotNull(result);
        assertEquals("工作日加班", result.getOvertimeTypeName());
        assertEquals(new BigDecimal("862.07"), result.getHourlyRate());
        // 工作日加班1.5倍
        assertEquals(new BigDecimal("1293.11"), result.getOvertimePay());
    }

    @Test
    @DisplayName("计算加班费 - 周末加班")
    void testCalculateOvertimePay_Weekend() {
        // 准备测试数据
        OvertimePayRequest request = new OvertimePayRequest();
        request.setMonthlySalary(new BigDecimal("10000"));
        request.setOvertimeType("weekend");
        request.setOvertimeHours(8);

        // 执行测试
        OvertimePayResult result = calculatorService.calculateOvertimePay(request);

        // 验证
        assertNotNull(result);
        assertEquals("周末加班", result.getOvertimeTypeName());
        // 周末加班2倍
        assertEquals(new BigDecimal("1379.31"), result.getOvertimePay());
    }

    @Test
    @DisplayName("计算加班费 - 法定节假日加班")
    void testCalculateOvertimePay_Holiday() {
        // 准备测试数据
        OvertimePayRequest request = new OvertimePayRequest();
        request.setMonthlySalary(new BigDecimal("10000"));
        request.setOvertimeType("holiday");
        request.setOvertimeHours(8);

        // 执行测试
        OvertimePayResult result = calculatorService.calculateOvertimePay(request);

        // 验证
        assertNotNull(result);
        assertEquals("法定节假日加班", result.getOvertimeTypeName());
        // 法定节假日加班3倍
        assertEquals(new BigDecimal("2068.97"), result.getOvertimePay());
    }
}
