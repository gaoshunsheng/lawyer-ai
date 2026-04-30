package com.lawyer.common.dto.ai;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 文书生成响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentGenerateResponse {

    /**
     * 生成的文书ID（如果保存到数据库）
     */
    private Long documentId;

    /**
     * 文书标题
     */
    private String title;

    /**
     * 文书内容
     */
    private String content;

    /**
     * AI建议
     */
    private List<Suggestion> suggestions;

    /**
     * 法律依据
     */
    private List<LegalBasis> legalBasis;

    /**
     * 建议信息
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Suggestion {
        /**
         * 建议类型
         */
        private String type;

        /**
         * 建议内容
         */
        private String content;

        /**
         * 详细建议
         */
        private String suggestion;
    }

    /**
     * 法律依据
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LegalBasis {
        /**
         * 法律名称
         */
        private String law;

        /**
         * 条款
         */
        private String article;

        /**
         * 类型
         */
        private String type;
    }
}
