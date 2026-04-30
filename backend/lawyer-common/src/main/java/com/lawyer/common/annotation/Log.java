package com.lawyer.common.annotation;

import java.lang.annotation.*;

/**
 * 操作日志注解
 */
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Log {
    /**
     * 操作类型
     */
    OperationType operationType() default OperationType.VIEW;

    /**
     * 操作描述
     */
    String description() default "";

    /**
     * 操作类型枚举
     */
    enum OperationType {
        /**
         * 查看
         */
        VIEW("VIEW", "查看"),
        /**
         * 查询
         */
        QUERY("QUERY", "查询"),
        /**
         * 新增
         */
        INSERT("INSERT", "新增"),
        /**
         * 修改
         */
        UPDATE("UPDATE", "修改"),
        /**
         * 删除
         */
        DELETE("DELETE", "删除"),
        /**
         * 导出
         */
        EXPORT("EXPORT", "导出"),
        /**
         * 导入
         */
        IMPORT("IMPORT", "导入"),
        /**
         * 登录
         */
        LOGIN("LOGIN", "登录"),
        /**
         * 登出
         */
        LOGOUT("LOGOUT", "登出"),
        /**
         * 其他
         */
        OTHER("OTHER", "其他");

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
