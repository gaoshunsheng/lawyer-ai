package com.lawyer.common.dto.chat;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 聊天响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {

    /**
     * 消息ID
     */
    private String messageId;

    /**
     * 会话ID
     */
    private Long sessionId;

    /**
     * 角色
     */
    private String role;

    /**
     * 消息内容
     */
    private String content;

    /**
     * 内容类型
     */
    private String contentType;

    /**
     * 法律依据
     */
    private List<LegalBasis> legalBasis;

    /**
     * 引用案例
     */
    private List<CaseReference> casesReferenced;

    /**
     * 消耗Token数
     */
    private Integer tokensUsed;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;

    /**
     * 法律依据
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LegalBasis {
        private String lawName;
        private String articleNumber;
        private String content;
        private String url;
    }

    /**
     * 案例引用
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CaseReference {
        private String caseNumber;
        private String court;
        private String date;
        private String summary;
        private String result;
        private Double similarity;
    }
}
