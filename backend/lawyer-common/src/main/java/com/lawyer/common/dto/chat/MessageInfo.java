package com.lawyer.common.dto.chat;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 消息信息DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MessageInfo {

    /**
     * 消息ID
     */
    private Long id;

    /**
     * 会话ID
     */
    private Long sessionId;

    /**
     * 角色：user/assistant
     */
    private String role;

    /**
     * 消息内容
     */
    private String content;

    /**
     * Token数
     */
    private Integer tokens;

    /**
     * 元数据
     */
    private String metadata;

    /**
     * 创建时间
     */
    private LocalDateTime createdAt;
}
