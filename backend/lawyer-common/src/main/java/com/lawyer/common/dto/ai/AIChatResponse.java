package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * AI聊天响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AIChatResponse {

    /**
     * 会话ID
     */
    private String sessionId;

    /**
     * AI回复内容
     */
    private String reply;

    /**
     * 引用来源（法条、案例等）
     */
    private List<SourceInfo> sources;

    /**
     * 置信度
     */
    private Double confidence;

    /**
     * 推荐问题
     */
    private List<String> suggestedQuestions;

    /**
     * 来源信息
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SourceInfo {
        /**
         * 来源类型：LAW-法规, CASE-案例, INTERNAL-内部资料
         */
        private String type;

        /**
         * 标题
         */
        private String title;

        /**
         * 相似度分数
         */
        private Double score;
    }
}
