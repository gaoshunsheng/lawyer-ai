package com.lawyer.service.statistics.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.lawyer.common.dto.cases.CaseStatistics;
import com.lawyer.common.dto.statistics.CaseReport;
import com.lawyer.common.dto.statistics.SystemStatistics;
import com.lawyer.common.enums.CaseStatus;
import com.lawyer.common.enums.CaseType;
import com.lawyer.common.enums.DocumentStatus;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import com.lawyer.service.document.entity.Document;
import com.lawyer.service.document.mapper.DocumentMapper;
import com.lawyer.service.knowledge.entity.Knowledge;
import com.lawyer.service.knowledge.mapper.KnowledgeMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 统计服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class StatisticsService {

    private final CaseMapper caseMapper;
    private final DocumentMapper documentMapper;
    private final UserMapper userMapper;
    private final KnowledgeMapper knowledgeMapper;

    /**
     * 获取系统统计概览
     */
    public SystemStatistics getSystemStatistics(Long tenantId) {
        return SystemStatistics.builder()
                .caseStatistics(getCaseStatistics(tenantId))
                .documentStatistics(getDocumentStatistics(tenantId))
                .userStatistics(getUserStatistics(tenantId))
                .knowledgeStatistics(getKnowledgeStatistics(tenantId))
                .build();
    }

    /**
     * 获取案件统计
     */
    public SystemStatistics.CaseStatistics getCaseStatistics(Long tenantId) {
        LambdaQueryWrapper<Case> baseWrapper = new LambdaQueryWrapper<>();
        baseWrapper.eq(Case::getIsDeleted, 0);
        if (tenantId != null) {
            baseWrapper.eq(Case::getTenantId, tenantId);
        }

        // 总案件数
        Long totalCases = caseMapper.selectCount(baseWrapper);

        // 进行中案件数
        LambdaQueryWrapper<Case> ongoingWrapper = new LambdaQueryWrapper<>();
        ongoingWrapper.eq(Case::getIsDeleted, 0)
                .notIn(Case::getCaseStatus, CaseStatus.CLOSED, CaseStatus.CANCELLED);
        if (tenantId != null) {
            ongoingWrapper.eq(Case::getTenantId, tenantId);
        }
        Long ongoingCases = caseMapper.selectCount(ongoingWrapper);

        // 已结案案件数
        LambdaQueryWrapper<Case> closedWrapper = new LambdaQueryWrapper<>();
        closedWrapper.eq(Case::getIsDeleted, 0)
                .eq(Case::getCaseStatus, CaseStatus.CLOSED);
        if (tenantId != null) {
            closedWrapper.eq(Case::getTenantId, tenantId);
        }
        Long closedCases = caseMapper.selectCount(closedWrapper);

        // 本月新增
        LocalDateTime monthStart = LocalDate.now().withDayOfMonth(1).atStartOfDay();
        LambdaQueryWrapper<Case> monthWrapper = new LambdaQueryWrapper<>();
        monthWrapper.eq(Case::getIsDeleted, 0)
                .ge(Case::getCreatedAt, monthStart);
        if (tenantId != null) {
            monthWrapper.eq(Case::getTenantId, tenantId);
        }
        Long thisMonthNewCases = caseMapper.selectCount(monthWrapper);

        // 本周新增
        LocalDateTime weekStart = LocalDate.now().minusDays(LocalDate.now().getDayOfWeek().getValue() - 1).atStartOfDay();
        LambdaQueryWrapper<Case> weekWrapper = new LambdaQueryWrapper<>();
        weekWrapper.eq(Case::getIsDeleted, 0)
                .ge(Case::getCreatedAt, weekStart);
        if (tenantId != null) {
            weekWrapper.eq(Case::getTenantId, tenantId);
        }
        Long thisWeekNewCases = caseMapper.selectCount(weekWrapper);

        // 总标的金额
        BigDecimal totalClaimAmount = BigDecimal.ZERO;
        List<Case> allCases = caseMapper.selectList(baseWrapper);
        for (Case c : allCases) {
            if (c.getClaimAmount() != null) {
                totalClaimAmount = totalClaimAmount.add(c.getClaimAmount());
            }
        }

        // 本月标的金额
        BigDecimal thisMonthClaimAmount = BigDecimal.ZERO;
        List<Case> monthCases = caseMapper.selectList(monthWrapper);
        for (Case c : monthCases) {
            if (c.getClaimAmount() != null) {
                thisMonthClaimAmount = thisMonthClaimAmount.add(c.getClaimAmount());
            }
        }

        // 案件类型分布
        Map<String, Long> caseTypeDistribution = new HashMap<>();
        for (CaseType type : CaseType.values()) {
            LambdaQueryWrapper<Case> typeWrapper = new LambdaQueryWrapper<>();
            typeWrapper.eq(Case::getIsDeleted, 0).eq(Case::getCaseType, type);
            if (tenantId != null) {
                typeWrapper.eq(Case::getTenantId, tenantId);
            }
            caseTypeDistribution.put(type.getCode(), caseMapper.selectCount(typeWrapper));
        }

        // 案件状态分布
        Map<String, Long> caseStatusDistribution = new HashMap<>();
        for (CaseStatus status : CaseStatus.values()) {
            LambdaQueryWrapper<Case> statusWrapper = new LambdaQueryWrapper<>();
            statusWrapper.eq(Case::getIsDeleted, 0).eq(Case::getCaseStatus, status);
            if (tenantId != null) {
                statusWrapper.eq(Case::getTenantId, tenantId);
            }
            caseStatusDistribution.put(status.getCode(), caseMapper.selectCount(statusWrapper));
        }

        // 月度趋势（最近6个月）
        List<SystemStatistics.TrendData> monthlyTrend = getCaseMonthlyTrend(tenantId, 6);

        return SystemStatistics.CaseStatistics.builder()
                .totalCases(totalCases)
                .ongoingCases(ongoingCases)
                .closedCases(closedCases)
                .thisMonthNewCases(thisMonthNewCases)
                .thisWeekNewCases(thisWeekNewCases)
                .totalClaimAmount(totalClaimAmount)
                .thisMonthClaimAmount(thisMonthClaimAmount)
                .caseTypeDistribution(caseTypeDistribution)
                .caseStatusDistribution(caseStatusDistribution)
                .monthlyTrend(monthlyTrend)
                .build();
    }

    /**
     * 获取文书统计
     */
    public SystemStatistics.DocumentStatistics getDocumentStatistics(Long tenantId) {
        LambdaQueryWrapper<Document> baseWrapper = new LambdaQueryWrapper<>();
        baseWrapper.eq(Document::getIsDeleted, 0);
        if (tenantId != null) {
            baseWrapper.eq(Document::getTenantId, tenantId);
        }

        // 总文书数
        Long totalDocuments = documentMapper.selectCount(baseWrapper);

        // 各状态文书数
        LambdaQueryWrapper<Document> draftWrapper = new LambdaQueryWrapper<>();
        draftWrapper.eq(Document::getIsDeleted, 0).eq(Document::getStatus, DocumentStatus.DRAFT);
        if (tenantId != null) {
            draftWrapper.eq(Document::getTenantId, tenantId);
        }
        Long draftDocuments = documentMapper.selectCount(draftWrapper);

        LambdaQueryWrapper<Document> reviewWrapper = new LambdaQueryWrapper<>();
        reviewWrapper.eq(Document::getIsDeleted, 0).eq(Document::getStatus, DocumentStatus.REVIEW);
        if (tenantId != null) {
            reviewWrapper.eq(Document::getTenantId, tenantId);
        }
        Long reviewDocuments = documentMapper.selectCount(reviewWrapper);

        LambdaQueryWrapper<Document> finalWrapper = new LambdaQueryWrapper<>();
        finalWrapper.eq(Document::getIsDeleted, 0).eq(Document::getStatus, DocumentStatus.FINAL);
        if (tenantId != null) {
            finalWrapper.eq(Document::getTenantId, tenantId);
        }
        Long finalDocuments = documentMapper.selectCount(finalWrapper);

        // 本月创建
        LocalDateTime monthStart = LocalDate.now().withDayOfMonth(1).atStartOfDay();
        LambdaQueryWrapper<Document> monthWrapper = new LambdaQueryWrapper<>();
        monthWrapper.eq(Document::getIsDeleted, 0)
                .ge(Document::getCreatedAt, monthStart);
        if (tenantId != null) {
            monthWrapper.eq(Document::getTenantId, tenantId);
        }
        Long thisMonthCreated = documentMapper.selectCount(monthWrapper);

        // 文书类型分布
        Map<String, Long> docTypeDistribution = new HashMap<>();
        List<Document> allDocs = documentMapper.selectList(baseWrapper);
        docTypeDistribution = allDocs.stream()
                .collect(Collectors.groupingBy(
                        doc -> doc.getDocType() != null ? doc.getDocType() : "OTHER",
                        Collectors.counting()
                ));

        // 月度趋势
        List<SystemStatistics.TrendData> monthlyTrend = getDocumentMonthlyTrend(tenantId, 6);

        return SystemStatistics.DocumentStatistics.builder()
                .totalDocuments(totalDocuments)
                .draftDocuments(draftDocuments)
                .reviewDocuments(reviewDocuments)
                .finalDocuments(finalDocuments)
                .thisMonthCreated(thisMonthCreated)
                .docTypeDistribution(docTypeDistribution)
                .monthlyTrend(monthlyTrend)
                .build();
    }

    /**
     * 获取用户统计
     */
    public SystemStatistics.UserStatistics getUserStatistics(Long tenantId) {
        LambdaQueryWrapper<User> baseWrapper = new LambdaQueryWrapper<>();
        baseWrapper.eq(User::getIsDeleted, 0);
        if (tenantId != null) {
            baseWrapper.eq(User::getTenantId, tenantId);
        }

        // 总用户数
        Long totalUsers = userMapper.selectCount(baseWrapper);

        // 活跃用户数
        LambdaQueryWrapper<User> activeWrapper = new LambdaQueryWrapper<>();
        activeWrapper.eq(User::getIsDeleted, 0).eq(User::getStatus, 1);
        if (tenantId != null) {
            activeWrapper.eq(User::getTenantId, tenantId);
        }
        Long activeUsers = userMapper.selectCount(activeWrapper);

        // 本月活跃
        LocalDateTime monthStart = LocalDate.now().withDayOfMonth(1).atStartOfDay();
        LambdaQueryWrapper<User> monthActiveWrapper = new LambdaQueryWrapper<>();
        monthActiveWrapper.eq(User::getIsDeleted, 0)
                .ge(User::getLastLoginTime, monthStart);
        if (tenantId != null) {
            monthActiveWrapper.eq(User::getTenantId, tenantId);
        }
        Long thisMonthActive = userMapper.selectCount(monthActiveWrapper);

        // 角色分布
        Map<String, Long> roleDistribution = new HashMap<>();
        List<User> allUsers = userMapper.selectList(baseWrapper);
        roleDistribution = allUsers.stream()
                .filter(u -> u.getRole() != null)
                .collect(Collectors.groupingBy(
                        u -> u.getRole().getCode(),
                        Collectors.counting()
                ));

        return SystemStatistics.UserStatistics.builder()
                .totalUsers(totalUsers)
                .activeUsers(activeUsers)
                .thisMonthActive(thisMonthActive)
                .roleDistribution(roleDistribution)
                .build();
    }

    /**
     * 获取知识库统计
     */
    public SystemStatistics.KnowledgeStatistics getKnowledgeStatistics(Long tenantId) {
        LambdaQueryWrapper<Knowledge> baseWrapper = new LambdaQueryWrapper<>();
        baseWrapper.eq(Knowledge::getIsDeleted, 0);
        if (tenantId != null) {
            baseWrapper.and(w -> w.isNull(Knowledge::getTenantId)
                    .or().eq(Knowledge::getTenantId, tenantId));
        }

        // 总数
        Long totalKnowledge = knowledgeMapper.selectCount(baseWrapper);

        // 法规数量
        LambdaQueryWrapper<Knowledge> lawWrapper = new LambdaQueryWrapper<>();
        lawWrapper.eq(Knowledge::getIsDeleted, 0).eq(Knowledge::getDocType, "LAW");
        if (tenantId != null) {
            lawWrapper.and(w -> w.isNull(Knowledge::getTenantId)
                    .or().eq(Knowledge::getTenantId, tenantId));
        }
        Long lawCount = knowledgeMapper.selectCount(lawWrapper);

        // 案例数量
        LambdaQueryWrapper<Knowledge> caseWrapper = new LambdaQueryWrapper<>();
        caseWrapper.eq(Knowledge::getIsDeleted, 0).eq(Knowledge::getDocType, "CASE");
        if (tenantId != null) {
            caseWrapper.and(w -> w.isNull(Knowledge::getTenantId)
                    .or().eq(Knowledge::getTenantId, tenantId));
        }
        Long caseCount = knowledgeMapper.selectCount(caseWrapper);

        // 内部资料数量
        LambdaQueryWrapper<Knowledge> internalWrapper = new LambdaQueryWrapper<>();
        internalWrapper.eq(Knowledge::getIsDeleted, 0).eq(Knowledge::getDocType, "INTERNAL");
        if (tenantId != null) {
            internalWrapper.and(w -> w.isNull(Knowledge::getTenantId)
                    .or().eq(Knowledge::getTenantId, tenantId));
        }
        Long internalCount = knowledgeMapper.selectCount(internalWrapper);

        // 本月查看
        LocalDateTime monthStart = LocalDate.now().withDayOfMonth(1).atStartOfDay();
        // TODO: 需要添加查看记录表

        // 分类分布
        List<Knowledge> allKnowledge = knowledgeMapper.selectList(baseWrapper);
        Map<String, Long> categoryDistribution = allKnowledge.stream()
                .filter(k -> k.getCategory() != null)
                .collect(Collectors.groupingBy(
                        Knowledge::getCategory,
                        Collectors.counting()
                ));

        return SystemStatistics.KnowledgeStatistics.builder()
                .totalKnowledge(totalKnowledge)
                .lawCount(lawCount)
                .caseCount(caseCount)
                .internalCount(internalCount)
                .thisMonthViewed(0L) // TODO
                .categoryDistribution(categoryDistribution)
                .build();
    }

    /**
     * 获取案件月度趋势
     */
    private List<SystemStatistics.TrendData> getCaseMonthlyTrend(Long tenantId, int months) {
        List<SystemStatistics.TrendData> trends = new ArrayList<>();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM");

        for (int i = months - 1; i >= 0; i--) {
            YearMonth yearMonth = YearMonth.now().minusMonths(i);
            LocalDateTime start = yearMonth.atDay(1).atStartOfDay();
            LocalDateTime end = yearMonth.atEndOfMonth().atTime(23, 59, 59);

            LambdaQueryWrapper<Case> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(Case::getIsDeleted, 0)
                    .between(Case::getCreatedAt, start, end);
            if (tenantId != null) {
                wrapper.eq(Case::getTenantId, tenantId);
            }
            Long count = caseMapper.selectCount(wrapper);

            trends.add(SystemStatistics.TrendData.builder()
                    .date(yearMonth.format(formatter))
                    .count(count)
                    .amount(BigDecimal.ZERO)
                    .build());
        }

        return trends;
    }

    /**
     * 获取文书月度趋势
     */
    private List<SystemStatistics.TrendData> getDocumentMonthlyTrend(Long tenantId, int months) {
        List<SystemStatistics.TrendData> trends = new ArrayList<>();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM");

        for (int i = months - 1; i >= 0; i--) {
            YearMonth yearMonth = YearMonth.now().minusMonths(i);
            LocalDateTime start = yearMonth.atDay(1).atStartOfDay();
            LocalDateTime end = yearMonth.atEndOfMonth().atTime(23, 59, 59);

            LambdaQueryWrapper<Document> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(Document::getIsDeleted, 0)
                    .between(Document::getCreatedAt, start, end);
            if (tenantId != null) {
                wrapper.eq(Document::getTenantId, tenantId);
            }
            Long count = documentMapper.selectCount(wrapper);

            trends.add(SystemStatistics.TrendData.builder()
                    .date(yearMonth.format(formatter))
                    .count(count)
                    .amount(BigDecimal.ZERO)
                    .build());
        }

        return trends;
    }

    /**
     * 获取案件报告
     */
    public CaseReport getCaseReport(Long tenantId, String startDate, String endDate) {
        LocalDate start = startDate != null ? LocalDate.parse(startDate) : LocalDate.now().withDayOfMonth(1);
        LocalDate end = endDate != null ? LocalDate.parse(endDate) : LocalDate.now();

        LambdaQueryWrapper<Case> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Case::getIsDeleted, 0)
                .between(Case::getCreatedAt, start.atStartOfDay(), end.atTime(23, 59, 59));
        if (tenantId != null) {
            wrapper.eq(Case::getTenantId, tenantId);
        }

        List<Case> cases = caseMapper.selectList(wrapper);

        // 统计数据
        Long totalCases = (long) cases.size();
        Long newCases = totalCases;

        Long closedCases = cases.stream()
                .filter(c -> c.getCaseStatus() == CaseStatus.CLOSED)
                .count();

        BigDecimal totalClaimAmount = cases.stream()
                .filter(c -> c.getClaimAmount() != null)
                .map(Case::getClaimAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        // 案件类型统计
        Map<String, Long> caseTypeCount = cases.stream()
                .filter(c -> c.getCaseType() != null)
                .collect(Collectors.groupingBy(
                        c -> c.getCaseType().getCode(),
                        Collectors.counting()
                ));

        // 案件状态统计
        Map<String, Long> caseStatusCount = cases.stream()
                .filter(c -> c.getCaseStatus() != null)
                .collect(Collectors.groupingBy(
                        c -> c.getCaseStatus().getCode(),
                        Collectors.counting()
                ));

        // 律师办案统计
        Map<Long, List<Case>> lawyerCases = cases.stream()
                .filter(c -> c.getLawyerId() != null)
                .collect(Collectors.groupingBy(Case::getLawyerId));

        List<CaseReport.LawyerCaseCount> lawyerCaseCounts = new ArrayList<>();
        for (Map.Entry<Long, List<Case>> entry : lawyerCases.entrySet()) {
            User lawyer = userMapper.selectById(entry.getKey());
            if (lawyer != null) {
                BigDecimal amount = entry.getValue().stream()
                        .filter(c -> c.getClaimAmount() != null)
                        .map(Case::getClaimAmount)
                        .reduce(BigDecimal.ZERO, BigDecimal::add);

                lawyerCaseCounts.add(CaseReport.LawyerCaseCount.builder()
                        .lawyerId(entry.getKey())
                        .lawyerName(lawyer.getRealName())
                        .caseCount((long) entry.getValue().size())
                        .totalClaimAmount(amount)
                        .build());
            }
        }

        // 按办案数量排序
        lawyerCaseCounts.sort((a, b) -> b.getCaseCount().compareTo(a.getCaseCount()));

        return CaseReport.builder()
                .title("案件统计报告")
                .timeRange(start + " 至 " + end)
                .totalCases(totalCases)
                .newCases(newCases)
                .closedCases(closedCases)
                .totalClaimAmount(totalClaimAmount)
                .caseTypeCount(caseTypeCount)
                .caseStatusCount(caseStatusCount)
                .lawyerCaseCounts(lawyerCaseCounts.subList(0, Math.min(10, lawyerCaseCounts.size())))
                .monthlyTrends(new ArrayList<>()) // TODO: 实现月度趋势
                .build();
    }
}
