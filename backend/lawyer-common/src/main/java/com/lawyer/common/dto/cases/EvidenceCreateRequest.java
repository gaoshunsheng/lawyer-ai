package com.lawyer.common.dto.cases;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 创建证据请求DTO
 */
@Data
public class EvidenceCreateRequest {

    @NotNull(message = "案件ID不能为空")
    private Long caseId;

    @NotBlank(message = "证据名称不能为空")
    @Size(max = 200, message = "证据名称长度不能超过200个字符")
    private String name;

    /**
     * 证据类型
     */
    private String type;

    /**
     * 证据描述
     */
    private String description;

    /**
     * 文件URL
     */
    private String fileUrl;

    /**
     * 文件类型
     */
    private String fileType;

    /**
     * 文件大小
     */
    private Long fileSize;

    /**
     * 证据链顺序
     */
    private Integer chainOrder;

    /**
     * 证据链说明
     */
    private String chainDescription;
}
