package com.lawyer.common;

/**
 * 通用常量
 */
public class Constants {

    /**
     * 成功状态码
     */
    public static final int SUCCESS = 0;

    /**
     * 失败状态码
     */
    public static final int FAIL = 1;

    /**
     * Token前缀
     */
    public static final String TOKEN_PREFIX = "Bearer ";

    /**
     * Token请求头
     */
    public static final String HEADER_AUTHORIZATION = "Authorization";

    /**
     * 租户ID请求头
     */
    public static final String HEADER_TENANT_ID = "X-Tenant-Id";

    /**
     * 请求ID请求头
     */
    public static final String HEADER_REQUEST_ID = "X-Request-Id";

    /**
     * 默认页码
     */
    public static final int DEFAULT_PAGE = 1;

    /**
     * 默认每页数量
     */
    public static final int DEFAULT_PAGE_SIZE = 20;

    /**
     * 最大每页数量
     */
    public static final int MAX_PAGE_SIZE = 100;

    /**
     * 删除标记 - 已删除
     */
    public static final int DELETED = 1;

    /**
     * 删除标记 - 未删除
     */
    public static final int NOT_DELETED = 0;

    /**
     * 启用状态
     */
    public static final int ENABLED = 1;

    /**
     * 禁用状态
     */
    public static final int DISABLED = 0;
}
