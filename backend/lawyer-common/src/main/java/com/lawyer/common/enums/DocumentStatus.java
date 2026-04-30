package com.lawyer.common.enums;

import lombok.Getter;

/**
 * 文书状态枚举
 */
@Getter
public enum DocumentStatus {

    DRAFT("draft", "草稿"),
    REVIEW("review", "审核中"),
    FINAL("final", "定稿"),
    ARCHIVED("archived", "已归档");

    private final String code;
    private final String name;

    DocumentStatus(String code, String name) {
        this.code = code;
        this.name = name;
    }

    public static DocumentStatus fromCode(String code) {
        for (DocumentStatus status : values()) {
            if (status.getCode().equals(code)) {
                return status;
            }
        }
        return null;
    }
}
