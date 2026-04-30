package com.lawyer.common.enums;

/**
 * 用户角色枚举
 */
public enum UserRole {
    /**
     * 系统管理员
     */
    ADMIN("ADMIN", "系统管理员"),

    /**
     * 主办律师
     */
    SENIOR_LAWYER("SENIOR_LAWYER", "主办律师"),

    /**
     * 辅助律师
     */
    JUNIOR_LAWYER("JUNIOR_LAWYER", "辅助律师"),

    /**
     * 律师助理
     */
    ASSISTANT("ASSISTANT", "律师助理"),

    /**
     * 行政人员
     */
    ADMIN_STAFF("ADMIN_STAFF", "行政人员");

    private final String code;
    private final String description;

    UserRole(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    public static UserRole fromCode(String code) {
        for (UserRole role : values()) {
            if (role.code.equals(code)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Unknown user role code: " + code);
    }
}
