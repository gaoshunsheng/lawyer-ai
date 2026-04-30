package com.lawyer.common.dto.log;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * 操作日志统计
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OperationLogStatistics {

    /**
     * 总操作次数
     */
    private Long totalOperations;

    /**
     * 今日操作次数
     */
    private Long todayOperations;

    /**
     * 成功操作次数
     */
    private Long successOperations;

    /**
     * 失败操作次数
     */
    private Long failedOperations;

    /**
     * 平均响应时间
     */
    private Double avgResponseTime;

    /**
     * 操作类型分布
     */
    private Map<String, Long> operationTypeDistribution;

    /**
     * 用户操作排名
     */
    private java.util.List<UserOperationCount> userOperationRanking;

    /**
     * 用户操作次数
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserOperationCount {
        private Long userId;
        private String username;
        private Long operationCount;
    }
}
