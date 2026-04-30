package com.lawyer.common.enums;

import lombok.Getter;

/**
 * 案件状态枚举
 */
@Getter
public enum CaseStatus {

    PENDING("pending", "待立案"),
    ARBITRATION("arbitration", "仲裁中"),
    FIRST_APPEAL("first_appeal", "一审中"),
    SECOND_APPEAL("second_appeal", "二审中"),
    RETRIAL("retrial", "再审中"),
    EXECUTION("execution", "执行中"),
    CLOSED("closed", "已结案"),
    CANCELLED("cancelled", "已撤销");

    private final String code;
    private final String name;

    CaseStatus(String code, String name) {
        this.code = code;
        this.name = name;
    }

    public static CaseStatus fromCode(String code) {
        for (CaseStatus status : values()) {
            if (status.getCode().equals(code)) {
                return status;
            }
        }
        return null;
    }
}
