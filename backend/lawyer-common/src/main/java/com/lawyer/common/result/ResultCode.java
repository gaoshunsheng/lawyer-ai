package com.lawyer.common.result;

import lombok.Getter;

/**
 * 响应状态码
 */
@Getter
public enum ResultCode {

    // 成功
    SUCCESS(0, "success"),

    // 通用错误 1xxxx
    FAIL(1, "操作失败"),
    PARAM_ERROR(10001, "参数错误"),
    REQUEST_FORMAT_ERROR(10002, "请求格式错误"),
    METHOD_NOT_SUPPORTED(10003, "请求方法不支持"),
    RATE_LIMIT_ERROR(10004, "请求频率超限，请稍后再试"),

    // 认证错误 2xxxx
    UNAUTHORIZED(20001, "未登录"),
    TOKEN_EXPIRED(20002, "Token已过期"),
    TOKEN_INVALID(20003, "Token无效"),
    FORBIDDEN(20004, "权限不足"),
    ACCOUNT_DISABLED(20005, "账号已禁用"),
    ACCOUNT_LOCKED(20006, "账号已锁定"),
    LOGIN_ERROR(20007, "用户名或密码错误"),
    USER_NOT_FOUND(20008, "用户不存在"),
    USER_DISABLED(20009, "用户已禁用"),
    PASSWORD_ERROR(20010, "密码错误"),
    USERNAME_EXISTS(20011, "用户名已存在"),
    PHONE_EXISTS(20012, "手机号已注册"),
    TENANT_NOT_FOUND(20013, "租户不存在"),
    TENANT_DISABLED(20014, "租户已禁用"),
    TENANT_EXPIRED(20015, "租户已过期"),
    TENANT_USER_LIMIT(20016, "租户用户数已达上限"),

    // 业务错误 3xxxx
    RESOURCE_NOT_FOUND(30001, "资源不存在"),
    RESOURCE_EXISTS(30002, "资源已存在"),
    RESOURCE_DELETED(30003, "资源已删除"),
    OPERATION_NOT_ALLOWED(30004, "操作不允许"),
    DATA_VALIDATE_FAIL(30005, "数据校验失败"),

    // 案件错误 4xxxx
    CASE_NOT_FOUND(40001, "案件不存在"),
    CASE_STATUS_ERROR(40002, "案件状态不允许此操作"),
    CASE_LIMIT_EXCEEDED(40003, "案件数量已达上限"),

    // 文书错误 5xxxx
    DOCUMENT_NOT_FOUND(50001, "文书不存在"),
    TEMPLATE_NOT_FOUND(50002, "模板不存在"),
    DOCUMENT_GENERATE_FAIL(50003, "文书生成失败"),

    // AI错误 6xxxx
    AI_SERVICE_UNAVAILABLE(60001, "AI服务不可用"),
    AI_REQUEST_TIMEOUT(60002, "AI请求超时"),
    AI_RESPONSE_ERROR(60003, "AI响应错误"),
    CONTENT_AUDIT_FAIL(60004, "内容审核不通过"),

    // 系统错误 9xxxx
    SYSTEM_ERROR(90001, "系统繁忙，请稍后再试"),
    SERVICE_UNAVAILABLE(90002, "服务不可用"),
    DATABASE_ERROR(90003, "数据库错误"),
    CACHE_ERROR(90004, "缓存错误");

    private final int code;
    private final String message;

    ResultCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
}
