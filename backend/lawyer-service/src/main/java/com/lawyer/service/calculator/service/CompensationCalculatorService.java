package com.lawyer.service.calculator.service;

import com.lawyer.common.dto.calculator.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.Period;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 赔偿计算器服务
 */
@Slf4j
@Service
public class CompensationCalculatorService {

    // 2023年各城市社会平均工资
    private static final Map<String, BigDecimal> SOCIAL_AVERAGE_SALARY = new HashMap<>() {{
        put("上海", new BigDecimal("12183"));
        put("北京", new BigDecimal("11297"));
        put("深圳", new BigDecimal("11620"));
        put("广州", new BigDecimal("10308"));
        put("杭州", new BigDecimal("10292"));
        put("南京", new BigDecimal("9428"));
        put("苏州", new BigDecimal("9461"));
        put("成都", new BigDecimal("7988"));
        put("武汉", new BigDecimal("7884"));
        put("西安", new BigDecimal("7259"));
        put("重庆", new BigDecimal("7163"));
        put("天津", new BigDecimal("7478"));
        put("青岛", new BigDecimal("8248"));
        put("大连", new BigDecimal("7499"));
        put("宁波", new BigDecimal("9011"));
    }};

    // 每月工作天数
    private static final BigDecimal WORK_DAYS_PER_MONTH = new BigDecimal("21.75");

    // 每天工作小时数
    private static final BigDecimal WORK_HOURS_PER_DAY = new BigDecimal("8");

    /**
     * 计算违法解除劳动合同赔偿金
     */
    public IllegalTerminationResult calculateIllegalTermination(IllegalTerminationRequest request) {
        IllegalTerminationResult result = new IllegalTerminationResult();

        // 计算工作年限
        BigDecimal workYears = calculateWorkYears(request.getEntryDate(), request.getLeaveDate());
        result.setWorkYears(workYears);

        // 工作年限说明
        String workYearsDesc = generateWorkYearsDescription(request.getEntryDate(), request.getLeaveDate(), workYears);
        result.setWorkYearsDescription(workYearsDesc);

        // 确定计算基数
        BigDecimal avgSalary = request.getAverageSalary12m() != null
                ? request.getAverageSalary12m()
                : request.getMonthlySalary();

        // 判断是否适用高薪封顶
        BigDecimal socialAvgSalary = getSocialAverageSalary(request.getCity());
        BigDecimal tripleSalary = socialAvgSalary.multiply(new BigDecimal("3"));

        boolean isHighSalaryCapped = Boolean.TRUE.equals(request.getHighSalaryCap()) &&
                avgSalary.compareTo(tripleSalary) > 0;
        result.setIsHighSalaryCapped(isHighSalaryCapped);
        result.setSocialAverageSalaryTriple(tripleSalary);

        // 确定实际计算基数
        BigDecimal calculationBase = isHighSalaryCapped ? tripleSalary : avgSalary;
        result.setCalculationBase(calculationBase);

        // 判断是协商解除还是违法解除
        boolean isNegotiated = Boolean.TRUE.equals(request.getIsNegotiated());
        int multiplier = isNegotiated ? 1 : 2;
        result.setMultiplier(multiplier);

        // 计算经济补偿金
        BigDecimal severancePay = workYears.multiply(calculationBase);
        result.setSeverancePay(severancePay);

        // 计算赔偿金总额
        BigDecimal totalCompensation = severancePay.multiply(new BigDecimal(multiplier));
        result.setTotalCompensation(totalCompensation);

        // 计算应补发金额
        BigDecimal paidAmount = request.getPaidCompensation() != null ? request.getPaidCompensation() : BigDecimal.ZERO;
        result.setPaidAmount(paidAmount);
        result.setUnpaidAmount(totalCompensation.subtract(paidAmount).max(BigDecimal.ZERO));

        // 构建输入参数摘要
        result.setInput(IllegalTerminationResult.IllegalTerminationInput.builder()
                .entryDate(request.getEntryDate().toString())
                .leaveDate(request.getLeaveDate().toString())
                .monthlySalary(request.getMonthlySalary())
                .averageSalary12m(request.getAverageSalary12m())
                .city(request.getCity())
                .highSalaryCap(request.getHighSalaryCap())
                .isNegotiated(request.getIsNegotiated())
                .build());

        // 构建计算步骤
        result.setSteps(buildIllegalTerminationSteps(request, result, socialAvgSalary));

        // 添加法律依据
        result.setLegalBasis(buildIllegalTerminationLegalBasis(isNegotiated));

        // 添加注意事项
        result.setNotes(buildIllegalTerminationNotes(isHighSalaryCapped, isNegotiated));

        return result;
    }

    /**
     * 计算加班费
     */
    public OvertimePayResult calculateOvertimePay(OvertimePayRequest request) {
        OvertimePayResult result = new OvertimePayResult();

        // 计算小时工资
        BigDecimal hourlyRate = request.getMonthlySalary()
                .divide(WORK_DAYS_PER_MONTH, 4, RoundingMode.HALF_UP)
                .divide(request.getWorkHoursPerDay(), 2, RoundingMode.HALF_UP);
        result.setHourlyRate(hourlyRate);

        // 工作日加班费 (150%)
        OvertimePayResult.OvertimePayDetail workdayDetail = OvertimePayResult.OvertimePayDetail.builder()
                .hours(request.getWorkdayHours())
                .rate(new BigDecimal("1.5"))
                .rateDescription("工作日加班150%")
                .amount(hourlyRate.multiply(new BigDecimal("1.5"))
                        .multiply(request.getWorkdayHours())
                        .setScale(2, RoundingMode.HALF_UP))
                .build();
        result.setWorkdayOvertime(workdayDetail);

        // 休息日加班费 (200%)
        BigDecimal weekendAmount = BigDecimal.ZERO;
        if (!Boolean.TRUE.equals(request.getHasCompensatoryLeave())) {
            weekendAmount = hourlyRate.multiply(new BigDecimal("2"))
                    .multiply(request.getWeekendHours())
                    .setScale(2, RoundingMode.HALF_UP);
        }
        OvertimePayResult.OvertimePayDetail weekendDetail = OvertimePayResult.OvertimePayDetail.builder()
                .hours(request.getWeekendHours())
                .rate(new BigDecimal("2.0"))
                .rateDescription("休息日加班200%" + (Boolean.TRUE.equals(request.getHasCompensatoryLeave()) ? "(已安排补休)" : ""))
                .amount(weekendAmount)
                .build();
        result.setWeekendOvertime(weekendDetail);

        // 法定节假日加班费 (300%)
        OvertimePayResult.OvertimePayDetail holidayDetail = OvertimePayResult.OvertimePayDetail.builder()
                .hours(request.getHolidayHours())
                .rate(new BigDecimal("3.0"))
                .rateDescription("法定节假日加班300%")
                .amount(hourlyRate.multiply(new BigDecimal("3"))
                        .multiply(request.getHolidayHours())
                        .setScale(2, RoundingMode.HALF_UP))
                .build();
        result.setHolidayOvertime(holidayDetail);

        // 计算总额
        BigDecimal totalOvertimePay = workdayDetail.getAmount()
                .add(weekendAmount)
                .add(holidayDetail.getAmount())
                .setScale(2, RoundingMode.HALF_UP);
        result.setTotalOvertimePay(totalOvertimePay);

        // 构建计算步骤
        result.setSteps(buildOvertimeSteps(request, result));

        // 添加法律依据
        result.setLegalBasis(buildOvertimeLegalBasis());

        // 添加注意事项
        result.setNotes(buildOvertimeNotes());

        return result;
    }

    /**
     * 计算年休假工资
     */
    public AnnualLeaveResult calculateAnnualLeave(AnnualLeaveRequest request) {
        AnnualLeaveResult result = new AnnualLeaveResult();

        // 计算日工资
        BigDecimal dailyRate = request.getMonthlySalary()
                .divide(WORK_DAYS_PER_MONTH, 2, RoundingMode.HALF_UP);
        result.setDailyRate(dailyRate);
        result.setTotalWorkYears(request.getTotalWorkYears());

        // 确定应休年休假天数
        int entitledDays;
        String entitledDaysDesc;
        if (request.getTotalWorkYears().compareTo(new BigDecimal("1")) < 0) {
            entitledDays = 0;
            entitledDaysDesc = "工作不满1年，无法定年休假";
        } else if (request.getTotalWorkYears().compareTo(new BigDecimal("10")) < 0) {
            entitledDays = 5;
            entitledDaysDesc = "累计工作满1年不满10年，年休假5天";
        } else if (request.getTotalWorkYears().compareTo(new BigDecimal("20")) < 0) {
            entitledDays = 10;
            entitledDaysDesc = "累计工作满10年不满20年，年休假10天";
        } else {
            entitledDays = 15;
            entitledDaysDesc = "累计工作满20年，年休假15天";
        }
        result.setEntitledDays(entitledDays);
        result.setEntitledDaysDescription(entitledDaysDesc);
        result.setUsedDays(request.getUsedDays());
        result.setUnusedDays(request.getUnusedDays());

        // 判断是否因个人原因不休年假
        if (Boolean.TRUE.equals(request.getPersonalReason())) {
            result.setMultiplier(0);
            result.setUnpaidWages(BigDecimal.ZERO);
            result.setNotes(List.of("因个人原因不休年休假，不享受未休年休假工资"));
        } else {
            // 未休年休假工资 = 日工资 × 未休天数 × 300%
            result.setMultiplier(3);
            BigDecimal unpaidWages = dailyRate
                    .multiply(request.getUnusedDays())
                    .multiply(new BigDecimal("3"))
                    .setScale(2, RoundingMode.HALF_UP);
            result.setUnpaidWages(unpaidWages);
        }

        // 构建计算步骤
        result.setSteps(buildAnnualLeaveSteps(request, result));

        // 添加法律依据
        result.setLegalBasis(buildAnnualLeaveLegalBasis());

        // 添加注意事项
        if (!Boolean.TRUE.equals(request.getPersonalReason())) {
            result.setNotes(buildAnnualLeaveNotes());
        }

        return result;
    }

    /**
     * 获取社会平均工资
     */
    public BigDecimal getSocialAverageSalary(String city) {
        if (city == null || city.isEmpty()) {
            return new BigDecimal("8000"); // 默认值
        }
        return SOCIAL_AVERAGE_SALARY.getOrDefault(city, new BigDecimal("8000"));
    }

    /**
     * 获取所有城市社会平均工资
     */
    public Map<String, BigDecimal> getAllSocialAverageSalaries() {
        return new HashMap<>(SOCIAL_AVERAGE_SALARY);
    }

    // ==================== 私有方法 ====================

    /**
     * 计算工作年限
     */
    private BigDecimal calculateWorkYears(LocalDate entryDate, LocalDate leaveDate) {
        long months = ChronoUnit.MONTHS.between(entryDate, leaveDate);
        long years = months / 12;
        long remainingMonths = months % 12;

        // 不满6个月按0.5年计算，满6个月按1年计算
        BigDecimal yearsDecimal = new BigDecimal(years);
        if (remainingMonths >= 6) {
            yearsDecimal = yearsDecimal.add(BigDecimal.ONE);
        } else if (remainingMonths > 0) {
            yearsDecimal = yearsDecimal.add(new BigDecimal("0.5"));
        }

        return yearsDecimal;
    }

    /**
     * 生成工作年限描述
     */
    private String generateWorkYearsDescription(LocalDate entryDate, LocalDate leaveDate, BigDecimal workYears) {
        Period period = Period.between(entryDate, leaveDate);
        return String.format("入职日期%s至解除日期%s，实际工作%d年%d个月，按%.1f年计算",
                entryDate, leaveDate, period.getYears(), period.getMonths(), workYears);
    }

    /**
     * 构建违法解除赔偿计算步骤
     */
    private List<CalculationResult.CalculationStep> buildIllegalTerminationSteps(
            IllegalTerminationRequest request, IllegalTerminationResult result, BigDecimal socialAvgSalary) {
        List<CalculationResult.CalculationStep> steps = new ArrayList<>();
        int order = 1;

        // 步骤1：工作年限
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order++)
                .title("工作年限计算")
                .description(result.getWorkYearsDescription())
                .amount(result.getWorkYears())
                .unit("年")
                .build());

        // 步骤2：工资标准
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order++)
                .title("工资标准确定")
                .description(request.getAverageSalary12m() != null ? "使用解除前12个月平均工资" : "使用月工资标准")
                .amount(result.getCalculationBase())
                .unit("元/月")
                .build());

        // 步骤3：高薪封顶判断
        if (Boolean.TRUE.equals(request.getHighSalaryCap())) {
            steps.add(CalculationResult.CalculationStep.builder()
                    .order(order++)
                    .title("高薪封顶判断")
                    .description(result.getIsHighSalaryCapped()
                            ? String.format("工资超过社平工资3倍（%s元/月 × 3 = %s元），按封顶基数计算",
                            socialAvgSalary, result.getSocialAverageSalaryTriple())
                            : "工资未超过社平工资3倍，不适用封顶")
                    .amount(result.getSocialAverageSalaryTriple())
                    .unit("元/月")
                    .build());
        }

        // 步骤4：经济补偿金计算
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order++)
                .title("经济补偿金计算")
                .description(String.format("工作年限 %.1f 年 × 月工资 %s 元", result.getWorkYears(), result.getCalculationBase()))
                .formula(String.format("%s × %s = %s 元", result.getWorkYears(), result.getCalculationBase(), result.getSeverancePay()))
                .amount(result.getSeverancePay())
                .unit("元")
                .build());

        // 步骤5：赔偿金计算
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order)
                .title(Boolean.TRUE.equals(request.getIsNegotiated()) ? "协商解除经济补偿金" : "违法解除赔偿金")
                .description(Boolean.TRUE.equals(request.getIsNegotiated())
                        ? "协商解除，支付N个月经济补偿金"
                        : "违法解除，支付2N个月赔偿金")
                .formula(String.format("%s × %d = %s 元", result.getSeverancePay(), result.getMultiplier(), result.getTotalCompensation()))
                .amount(result.getTotalCompensation())
                .unit("元")
                .build());

        return steps;
    }

    /**
     * 构建违法解除赔偿法律依据
     */
    private List<CalculationResult.LegalBasis> buildIllegalTerminationLegalBasis(boolean isNegotiated) {
        List<CalculationResult.LegalBasis> basis = new ArrayList<>();

        basis.add(CalculationResult.LegalBasis.builder()
                .lawName("《劳动合同法》第47条")
                .content("经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。六个月以上不满一年的，按一年计算；不满六个月的，向劳动者支付半个月工资的经济补偿。")
                .build());

        if (!isNegotiated) {
            basis.add(CalculationResult.LegalBasis.builder()
                    .lawName("《劳动合同法》第48条")
                    .content("用人单位违反本法规定解除或者终止劳动合同，劳动者要求继续履行劳动合同的，用人单位应当继续履行；劳动者不要求继续履行劳动合同或者劳动合同已经不能继续履行的，用人单位应当依照本法第八十七条规定支付赔偿金。")
                    .build());

            basis.add(CalculationResult.LegalBasis.builder()
                    .lawName("《劳动合同法》第87条")
                    .content("用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第四十七条规定的经济补偿标准的二倍向劳动者支付赔偿金。")
                    .build());
        }

        return basis;
    }

    /**
     * 构建违法解除赔偿注意事项
     */
    private List<String> buildIllegalTerminationNotes(boolean isHighSalaryCapped, boolean isNegotiated) {
        List<String> notes = new ArrayList<>();

        if (isNegotiated) {
            notes.add("协商解除情况下，用人单位只需支付经济补偿金（N）");
            notes.add("如果协商解除由劳动者主动提出，用人单位可能不需要支付经济补偿金");
        } else {
            notes.add("违法解除赔偿金是经济补偿金的两倍（2N）");
            notes.add("赔偿金和经济补偿金不能同时主张");
        }

        if (isHighSalaryCapped) {
            notes.add("月工资高于社平工资3倍的，按社平工资3倍计算，最高不超过12年");
        }

        notes.add("月工资包括：基本工资、奖金、津贴、补贴等所有货币性收入");
        notes.add("计算月平均工资时，应扣除加班费、非常规性奖金等");

        return notes;
    }

    /**
     * 构建加班费计算步骤
     */
    private List<CalculationResult.CalculationStep> buildOvertimeSteps(OvertimePayRequest request, OvertimePayResult result) {
        List<CalculationResult.CalculationStep> steps = new ArrayList<>();
        int order = 1;

        // 步骤1：小时工资计算
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order++)
                .title("小时工资计算")
                .description("月工资 ÷ 21.75 ÷ 8")
                .formula(String.format("%s ÷ 21.75 ÷ 8 = %s 元/小时", request.getMonthlySalary(), result.getHourlyRate()))
                .amount(result.getHourlyRate())
                .unit("元/小时")
                .build());

        // 步骤2：工作日加班费
        if (request.getWorkdayHours().compareTo(BigDecimal.ZERO) > 0) {
            steps.add(CalculationResult.CalculationStep.builder()
                    .order(order++)
                    .title("工作日加班费")
                    .description("小时工资 × 150% × 加班小时数")
                    .formula(String.format("%s × 1.5 × %s = %s 元",
                            result.getHourlyRate(), request.getWorkdayHours(), result.getWorkdayOvertime().getAmount()))
                    .amount(result.getWorkdayOvertime().getAmount())
                    .unit("元")
                    .build());
        }

        // 步骤3：休息日加班费
        if (request.getWeekendHours().compareTo(BigDecimal.ZERO) > 0) {
            steps.add(CalculationResult.CalculationStep.builder()
                    .order(order++)
                    .title("休息日加班费")
                    .description(Boolean.TRUE.equals(request.getHasCompensatoryLeave()) ? "已安排补休，不计发加班费" : "小时工资 × 200% × 加班小时数")
                    .formula(Boolean.TRUE.equals(request.getHasCompensatoryLeave())
                            ? "已安排补休"
                            : String.format("%s × 2 × %s = %s 元",
                            result.getHourlyRate(), request.getWeekendHours(), result.getWeekendOvertime().getAmount()))
                    .amount(result.getWeekendOvertime().getAmount())
                    .unit("元")
                    .build());
        }

        // 步骤4：法定节假日加班费
        if (request.getHolidayHours().compareTo(BigDecimal.ZERO) > 0) {
            steps.add(CalculationResult.CalculationStep.builder()
                    .order(order++)
                    .title("法定节假日加班费")
                    .description("小时工资 × 300% × 加班小时数")
                    .formula(String.format("%s × 3 × %s = %s 元",
                            result.getHourlyRate(), request.getHolidayHours(), result.getHolidayOvertime().getAmount()))
                    .amount(result.getHolidayOvertime().getAmount())
                    .unit("元")
                    .build());
        }

        // 步骤5：总计
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order)
                .title("加班费总计")
                .description("各项加班费合计")
                .formula(String.format("%s + %s + %s = %s 元",
                        result.getWorkdayOvertime().getAmount(),
                        result.getWeekendOvertime().getAmount(),
                        result.getHolidayOvertime().getAmount(),
                        result.getTotalOvertimePay()))
                .amount(result.getTotalOvertimePay())
                .unit("元")
                .build());

        return steps;
    }

    /**
     * 构建加班费法律依据
     */
    private List<CalculationResult.LegalBasis> buildOvertimeLegalBasis() {
        List<CalculationResult.LegalBasis> basis = new ArrayList<>();

        basis.add(CalculationResult.LegalBasis.builder()
                .lawName("《劳动法》第44条")
                .content("有下列情形之一的，用人单位应当按照下列标准支付高于劳动者正常工作时间工资的工资报酬：(一)安排劳动者延长工作时间的，支付不低于工资的百分之一百五十的工资报酬；(二)休息日安排劳动者工作又不能安排补休的，支付不低于工资的百分之二百的工资报酬；(三)法定休假日安排劳动者工作的，支付不低于工资的百分之三百的工资报酬。")
                .build());

        return basis;
    }

    /**
     * 构建加班费注意事项
     */
    private List<String> buildOvertimeNotes() {
        List<String> notes = new ArrayList<>();

        notes.add("加班事实的举证责任在劳动者，需保存加班证据");
        notes.add("休息日加班可以安排补休，补休时间应不少于加班时间");
        notes.add("法定节假日加班不能以补休代替加班费");
        notes.add("加班费计算基数应按劳动合同约定的工资标准确定");
        notes.add("主张加班费的仲裁时效为一年");
        notes.add("如用人单位掌握考勤记录，可申请法院调查取证");

        return notes;
    }

    /**
     * 构建年休假计算步骤
     */
    private List<CalculationResult.CalculationStep> buildAnnualLeaveSteps(AnnualLeaveRequest request, AnnualLeaveResult result) {
        List<CalculationResult.CalculationStep> steps = new ArrayList<>();
        int order = 1;

        // 步骤1：日工资计算
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order++)
                .title("日工资计算")
                .description("月工资 ÷ 21.75")
                .formula(String.format("%s ÷ 21.75 = %s 元/天", request.getMonthlySalary(), result.getDailyRate()))
                .amount(result.getDailyRate())
                .unit("元/天")
                .build());

        // 步骤2：应休年休假
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order++)
                .title("应休年休假天数")
                .description(result.getEntitledDaysDescription())
                .amount(new BigDecimal(result.getEntitledDays()))
                .unit("天")
                .build());

        // 步骤3：未休天数
        steps.add(CalculationResult.CalculationStep.builder()
                .order(order++)
                .title("未休年休假天数")
                .description("应休天数 - 已休天数")
                .amount(result.getUnusedDays())
                .unit("天")
                .build());

        // 步骤4：未休年休假工资
        if (!Boolean.TRUE.equals(request.getPersonalReason())) {
            steps.add(CalculationResult.CalculationStep.builder()
                    .order(order)
                    .title("未休年休假工资")
                    .description("日工资 × 未休天数 × 300%")
                    .formula(String.format("%s × %s × 3 = %s 元",
                            result.getDailyRate(), result.getUnusedDays(), result.getUnpaidWages()))
                    .amount(result.getUnpaidWages())
                    .unit("元")
                    .build());
        }

        return steps;
    }

    /**
     * 构建年休假法律依据
     */
    private List<CalculationResult.LegalBasis> buildAnnualLeaveLegalBasis() {
        List<CalculationResult.LegalBasis> basis = new ArrayList<>();

        basis.add(CalculationResult.LegalBasis.builder()
                .lawName("《职工带薪年休假条例》第3条")
                .content("职工累计工作已满1年不满10年的，年休假5天；已满10年不满20年的，年休假10天；已满20年的，年休假15天。")
                .build());

        basis.add(CalculationResult.LegalBasis.builder()
                .lawName("《企业职工带薪年休假实施办法》第10条")
                .content("用人单位经职工同意不安排年休假或者安排职工年休假天数少于应休年休假天数，应当对本年度应休未休年休假天数，按照其日工资收入的300%支付未休年休假工资报酬。")
                .build());

        return basis;
    }

    /**
     * 构建年休假注意事项
     */
    private List<String> buildAnnualLeaveNotes() {
        List<String> notes = new ArrayList<>();

        notes.add("未休年休假工资包含正常工作期间的工资（100%）和额外工资（200%）");
        notes.add("累计工作年限应以社保记录、劳动合同等为证");
        notes.add("年休假一般不跨年度安排，确有必要的可跨1个年度安排");
        notes.add("用人单位安排年休假，职工因个人原因不休的，不享受额外工资");
        notes.add("主张未休年休假工资的仲裁时效为一年");

        return notes;
    }
}
