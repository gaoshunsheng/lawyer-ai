package com.lawyer.service.log.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 操作日志实体
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("operation_logs")
public class OperationLog {

    /**
     * 主键ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 用户名
     */
    private String username;

    /**
     * 租户ID
     */
    private Long tenantId;

    /**
     * 操作类型
     */
    private String operationType;

    /**
     * 操作描述
     */
    private String operationDesc;

    /**
     * 请求方法
     */
    private String requestMethod;

    /**
     * 请求URL
     */
    private String requestUrl;

    /**
     * 请求参数
     */
    private String requestParams;

    /**
     * 响应状态
     */
    private Integer responseStatus;

    /**
     * 响应时间（毫秒）
     */
    private Long responseTime;

    /**
     * IP地址
     */
    private String ipAddress;

    /**
     * 用户代理
     */
    private String userAgent;

    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 操作类型枚举
     */
    public enum OperationType {
        /**
         * 创建
         */
        CREATE("CREATE", "创建"),
        /**
         * 更新
         */
        UPDATE("UPDATE", "更新"),
        /**
         * 删除
         */
        DELETE("DELETE", "删除"),
        /**
         * 查看
         */
        VIEW("VIEW", "查看"),
        /**
         * 登录
         */
        LOGIN("LOGIN", "登录"),
        /**
         * 登出
         */
        LOGOUT("LOGOUT", "登出"),
        /**
         * 导出
         */
        EXPORT("EXPORT", "导出"),
        /**
         * 导入
         */
        IMPORT("IMPORT", "导入"),
        /**
         * 上传
         */
        UPLOAD("UPLOAD", "上传"),
        /**
         * 下载
         */
        DOWNLOAD("DOWNLOAD", "下载");

        private final String code;
        private final String desc;

        OperationType(String code, String desc) {
            this.code = code;
            this.desc = desc;
        }

        public String getCode() {
            return code;
        }

        public String getDesc() {
            return desc;
        }
    }
}
