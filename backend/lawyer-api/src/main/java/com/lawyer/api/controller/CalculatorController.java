package com.lawyer.api.controller;

import com.lawyer.common.result.Result;
import com.lawyer.common.dto.calculator.*;
import com.lawyer.service.calculator.service.CompensationCalculatorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 赔偿计算器控制器
 */
@Tag(name = "赔偿计算器", description = "劳动争议赔偿计算工具")
@RestController
@RequestMapping("/api/calculator")
@RequiredArgsConstructor
public class CalculatorController {

    private final CompensationCalculatorService calculatorService;

    /**
     * 计算违法解除劳动合同赔偿金
     */
    @Operation(summary = "违法解除赔偿计算", description = "计算违法解除劳动合同赔偿金、经济补偿金")
    @PostMapping("/illegal-termination")
    public Result<IllegalTerminationResult> calculateIllegalTermination(
            @Valid @RequestBody IllegalTerminationRequest request) {
        IllegalTerminationResult result = calculatorService.calculateIllegalTermination(request);
        return Result.success(result);
    }

    /**
     * 计算加班费
     */
    @Operation(summary = "加班费计算", description = "计算工作日、休息日、法定节假日加班费")
    @PostMapping("/overtime")
    public Result<OvertimePayResult> calculateOvertimePay(
            @Valid @RequestBody OvertimePayRequest request) {
        OvertimePayResult result = calculatorService.calculateOvertimePay(request);
        return Result.success(result);
    }

    /**
     * 计算未休年休假工资
     */
    @Operation(summary = "年休假工资计算", description = "计算未休年休假工资")
    @PostMapping("/annual-leave")
    public Result<AnnualLeaveResult> calculateAnnualLeave(
            @Valid @RequestBody AnnualLeaveRequest request) {
        AnnualLeaveResult result = calculatorService.calculateAnnualLeave(request);
        return Result.success(result);
    }

    /**
     * 获取各城市社会平均工资
     */
    @Operation(summary = "社会平均工资", description = "获取各城市社会平均工资数据")
    @GetMapping("/social-average-salary")
    public Result<Map<String, java.math.BigDecimal>> getSocialAverageSalary() {
        Map<String, java.math.BigDecimal> salaries = calculatorService.getAllSocialAverageSalaries();
        return Result.success(salaries);
    }

    /**
     * 快速计算违法解除赔偿
     */
    @Operation(summary = "快速计算违法解除赔偿", description = "简化参数的快速计算")
    @GetMapping("/illegal-termination/quick")
    public Result<IllegalTerminationResult> quickCalculateIllegalTermination(
            @Parameter(description = "入职日期") @RequestParam String entryDate,
            @Parameter(description = "解除日期") @RequestParam String leaveDate,
            @Parameter(description = "月工资") @RequestParam java.math.BigDecimal monthlySalary,
            @Parameter(description = "城市") @RequestParam(required = false) String city) {
        IllegalTerminationRequest request = new IllegalTerminationRequest();
        request.setEntryDate(java.time.LocalDate.parse(entryDate));
        request.setLeaveDate(java.time.LocalDate.parse(leaveDate));
        request.setMonthlySalary(monthlySalary);
        request.setCity(city);
        request.setHighSalaryCap(false);
        request.setIsNegotiated(false);

        IllegalTerminationResult result = calculatorService.calculateIllegalTermination(request);
        return Result.success(result);
    }

    /**
     * 快速计算加班费
     */
    @Operation(summary = "快速计算加班费", description = "简化参数的快速计算")
    @GetMapping("/overtime/quick")
    public Result<OvertimePayResult> quickCalculateOvertimePay(
            @Parameter(description = "月工资") @RequestParam java.math.BigDecimal monthlySalary,
            @Parameter(description = "工作日加班小时") @RequestParam(required = false, defaultValue = "0") java.math.BigDecimal workdayHours,
            @Parameter(description = "休息日加班小时") @RequestParam(required = false, defaultValue = "0") java.math.BigDecimal weekendHours,
            @Parameter(description = "节假日加班小时") @RequestParam(required = false, defaultValue = "0") java.math.BigDecimal holidayHours) {
        OvertimePayRequest request = new OvertimePayRequest();
        request.setMonthlySalary(monthlySalary);
        request.setWorkdayHours(workdayHours != null ? workdayHours : java.math.BigDecimal.ZERO);
        request.setWeekendHours(weekendHours != null ? weekendHours : java.math.BigDecimal.ZERO);
        request.setHolidayHours(holidayHours != null ? holidayHours : java.math.BigDecimal.ZERO);

        OvertimePayResult result = calculatorService.calculateOvertimePay(request);
        return Result.success(result);
    }

    /**
     * 快速计算年休假工资
     */
    @Operation(summary = "快速计算年休假工资", description = "简化参数的快速计算")
    @GetMapping("/annual-leave/quick")
    public Result<AnnualLeaveResult> quickCalculateAnnualLeave(
            @Parameter(description = "月工资") @RequestParam java.math.BigDecimal monthlySalary,
            @Parameter(description = "累计工作年限") @RequestParam java.math.BigDecimal totalWorkYears,
            @Parameter(description = "未休天数") @RequestParam java.math.BigDecimal unusedDays) {
        AnnualLeaveRequest request = new AnnualLeaveRequest();
        request.setMonthlySalary(monthlySalary);
        request.setTotalWorkYears(totalWorkYears);
        request.setUnusedDays(unusedDays);

        AnnualLeaveResult result = calculatorService.calculateAnnualLeave(request);
        return Result.success(result);
    }
}
