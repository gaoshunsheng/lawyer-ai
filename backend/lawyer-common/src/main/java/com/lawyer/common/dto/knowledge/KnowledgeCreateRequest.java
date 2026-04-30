package com.lawyer.common.dto.knowledge;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.time.LocalDate;
import java.util.List;

/**
 * 创建知识条目请求DTO
 */
@Data
public class KnowledgeCreateRequest {

    /**
     * 分类
     */
    @NotBlank(message = "分类不能为空")
    private String category;

    /**
     * 文档类型：LAW-法规，CASE-案例，INTERNAL-内部资料
     */
    @NotBlank(message = "文档类型不能为空")
    private String docType;

    /**
     * 标题
     */
    @NotBlank(message = "标题不能为空")
    @Size(max = 500, message = "标题长度不能超过500个字符")
    private String title;

    /**
     * 内容
     */
    private String content;

    /**
     * 来源
     */
    @Size(max = 200, message = "来源长度不能超过200个字符")
    private String source;

    /**
     * 发布日期
     */
    private LocalDate publishDate;

    /**
     * 生效日期
     */
    private LocalDate effectiveDate;

    /**
     * 失效日期
     */
    private LocalDate expiryDate;

    /**
     * 标签
     */
    private List<String> tags;

    /**
     * 元数据
     */
    private String metadata;
}
