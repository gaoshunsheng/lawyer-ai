package com.lawyer.service.log.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.lawyer.common.dto.log.OperationLogQuery;
import com.lawyer.common.dto.log.OperationLogStatistics;
import com.lawyer.common.dto.log.OperationLogVO;
import com.lawyer.service.log.entity.OperationLog;
import com.lawyer.service.log.mapper.OperationLogMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 操作日志服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OperationLogService {

    private final OperationLogMapper operationLogMapper;
    private final UserMapper userMapper;

    /**
     * 记录操作日志
     */
    public void recordLog(OperationLog operationLog) {
        operationLogMapper.insert(operationLog);
    }

    /**
     * 异步记录操作日志
     */
    public void recordLogAsync(OperationLog operationLog) {
        // 使用异步方式记录日志，不影响主业务
        try {
            operationLogMapper.insert(operationLog);
        } catch (Exception e) {
            log.error("记录操作日志失败: {}", e.getMessage());
        }
    }

    /**
     * 分页查询操作日志
     */
    public IPage<OperationLogVO> queryLogs(OperationLogQuery query, Long tenantId) {
        Page<OperationLog> page = new Page<>(
                query.getPage() != null ? query.getPage() : 1,
                query.getSize() != null ? query.getSize() : 20
        );

        LambdaQueryWrapper<OperationLog> wrapper = new LambdaQueryWrapper<>();

        // 租户隔离
        if (tenantId != null) {
            wrapper.eq(OperationLog::getTenantId, tenantId);
        }

        // 用户ID过滤
        if (query.getUserId() != null) {
            wrapper.eq(OperationLog::getUserId, query.getUserId());
        }

        // 用户名模糊查询
        if (StringUtils.hasText(query.getUsername())) {
            wrapper.like(OperationLog::getUsername, query.getUsername());
        }

        // 操作类型过滤
        if (StringUtils.hasText(query.getOperationType())) {
            wrapper.eq(OperationLog::getOperationType, query.getOperationType());
        }

        // 时间范围过滤
        if (query.getStartTime() != null) {
            wrapper.ge(OperationLog::getCreatedAt, query.getStartTime());
        }
        if (query.getEndTime() != null) {
            wrapper.le(OperationLog::getCreatedAt, query.getEndTime());
        }

        // 响应状态过滤
        if (query.getResponseStatus() != null) {
            wrapper.eq(OperationLog::getResponseStatus, query.getResponseStatus());
        }

        // 排序
        String sortBy = StringUtils.hasText(query.getSortBy()) ? query.getSortBy() : "createdAt";
        String sortOrder = StringUtils.hasText(query.getSortOrder()) ? query.getSortOrder() : "desc";
        if ("desc".equalsIgnoreCase(sortOrder)) {
            wrapper.orderByDesc(OperationLog::getCreatedAt);
        } else {
            wrapper.orderByAsc(OperationLog::getCreatedAt);
        }

        IPage<OperationLog> logPage = operationLogMapper.selectPage(page, wrapper);

        // 转换为VO
        IPage<OperationLogVO> voPage = logPage.convert(this::convertToVO);
        return voPage;
    }

    /**
     * 获取日志详情
     */
    public OperationLogVO getLogById(Long id, Long tenantId) {
        LambdaQueryWrapper<OperationLog> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(OperationLog::getId, id);
        if (tenantId != null) {
            wrapper.eq(OperationLog::getTenantId, tenantId);
        }

        OperationLog log = operationLogMapper.selectOne(wrapper);
        return log != null ? convertToVO(log) : null;
    }

    /**
     * 删除日志（物理删除）
     */
    public void deleteLog(Long id, Long tenantId) {
        LambdaQueryWrapper<OperationLog> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(OperationLog::getId, id);
        if (tenantId != null) {
            wrapper.eq(OperationLog::getTenantId, tenantId);
        }
        operationLogMapper.delete(wrapper);
    }

    /**
     * 批量删除日志
     */
    public void deleteLogs(List<Long> ids, Long tenantId) {
        if (ids == null || ids.isEmpty()) {
            return;
        }

        LambdaQueryWrapper<OperationLog> wrapper = new LambdaQueryWrapper<>();
        wrapper.in(OperationLog::getId, ids);
        if (tenantId != null) {
            wrapper.eq(OperationLog::getTenantId, tenantId);
        }
        operationLogMapper.delete(wrapper);
    }

    /**
     * 清理指定时间之前的日志
     */
    public int cleanLogsBefore(LocalDateTime beforeTime, Long tenantId) {
        LambdaQueryWrapper<OperationLog> wrapper = new LambdaQueryWrapper<>();
        wrapper.lt(OperationLog::getCreatedAt, beforeTime);
        if (tenantId != null) {
            wrapper.eq(OperationLog::getTenantId, tenantId);
        }
        return operationLogMapper.delete(wrapper);
    }

    /**
     * 获取操作日志统计
     */
    public OperationLogStatistics getStatistics(Long tenantId) {
        LambdaQueryWrapper<OperationLog> baseWrapper = new LambdaQueryWrapper<>();
        if (tenantId != null) {
            baseWrapper.eq(OperationLog::getTenantId, tenantId);
        }

        // 总操作次数
        Long totalOperations = operationLogMapper.selectCount(baseWrapper);

        // 今日操作次数
        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        LambdaQueryWrapper<OperationLog> todayWrapper = new LambdaQueryWrapper<>();
        todayWrapper.ge(OperationLog::getCreatedAt, todayStart);
        if (tenantId != null) {
            todayWrapper.eq(OperationLog::getTenantId, tenantId);
        }
        Long todayOperations = operationLogMapper.selectCount(todayWrapper);

        // 成功操作次数（响应状态2xx）
        LambdaQueryWrapper<OperationLog> successWrapper = new LambdaQueryWrapper<>();
        successWrapper.between(OperationLog::getResponseStatus, 200, 299);
        if (tenantId != null) {
            successWrapper.eq(OperationLog::getTenantId, tenantId);
        }
        Long successOperations = operationLogMapper.selectCount(successWrapper);

        // 失败操作次数（响应状态非2xx）
        LambdaQueryWrapper<OperationLog> failedWrapper = new LambdaQueryWrapper<>();
        failedWrapper.notBetween(OperationLog::getResponseStatus, 200, 299);
        if (tenantId != null) {
            failedWrapper.eq(OperationLog::getTenantId, tenantId);
        }
        Long failedOperations = operationLogMapper.selectCount(failedWrapper);

        // 平均响应时间
        List<OperationLog> allLogs = operationLogMapper.selectList(baseWrapper);
        Double avgResponseTime = allLogs.stream()
                .filter(l -> l.getResponseTime() != null)
                .mapToLong(OperationLog::getResponseTime)
                .average()
                .orElse(0.0);

        // 操作类型分布
        Map<String, Long> operationTypeDistribution = allLogs.stream()
                .filter(l -> l.getOperationType() != null)
                .collect(Collectors.groupingBy(
                        OperationLog::getOperationType,
                        Collectors.counting()
                ));

        // 用户操作排名（Top 10）
        Map<Long, Long> userOperationCount = allLogs.stream()
                .filter(l -> l.getUserId() != null)
                .collect(Collectors.groupingBy(
                        OperationLog::getUserId,
                        Collectors.counting()
                ));

        List<OperationLogStatistics.UserOperationCount> userRanking = new ArrayList<>();
        userOperationCount.entrySet().stream()
                .sorted(Map.Entry.<Long, Long>comparingByValue().reversed())
                .limit(10)
                .forEach(entry -> {
                    User user = userMapper.selectById(entry.getKey());
                    if (user != null) {
                        userRanking.add(OperationLogStatistics.UserOperationCount.builder()
                                .userId(entry.getKey())
                                .username(user.getUsername())
                                .operationCount(entry.getValue())
                                .build());
                    }
                });

        return OperationLogStatistics.builder()
                .totalOperations(totalOperations)
                .todayOperations(todayOperations)
                .successOperations(successOperations)
                .failedOperations(failedOperations)
                .avgResponseTime(avgResponseTime)
                .operationTypeDistribution(operationTypeDistribution)
                .userOperationRanking(userRanking)
                .build();
    }

    /**
     * 转换为VO
     */
    private OperationLogVO convertToVO(OperationLog log) {
        // 获取操作类型描述
        String operationTypeDesc = "";
        for (Log.OperationType type : Log.OperationType.values()) {
            if (type.getCode().equals(log.getOperationType())) {
                operationTypeDesc = type.getDesc();
                break;
            }
        }

        return OperationLogVO.builder()
                .id(log.getId())
                .userId(log.getUserId())
                .username(log.getUsername())
                .tenantId(log.getTenantId())
                .operationType(log.getOperationType())
                .operationTypeDesc(operationTypeDesc)
                .operationDesc(log.getOperationDesc())
                .requestMethod(log.getRequestMethod())
                .requestUrl(log.getRequestUrl())
                .requestParams(log.getRequestParams())
                .responseStatus(log.getResponseStatus())
                .responseTime(log.getResponseTime())
                .ipAddress(log.getIpAddress())
                .userAgent(log.getUserAgent())
                .createdAt(log.getCreatedAt())
                .build();
    }
}
