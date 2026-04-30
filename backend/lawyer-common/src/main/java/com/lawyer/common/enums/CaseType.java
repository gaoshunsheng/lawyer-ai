package com.lawyer.common.enums;

import lombok.Getter;

/**
 * 案件类型枚举
 */
@Getter
public enum CaseType {

    LABOR_CONTRACT("labor_contract", "劳动合同纠纷"),
    WAGE("wage", "劳动报酬纠纷"),
    INJURY("injury", "工伤保险纠纷"),
    SOCIAL_INSURANCE("social_insurance", "社会保险纠纷"),
    TERMINATION("termination", "解除劳动关系纠纷"),
    DISCRIMINATION("discrimination", "就业歧视纠纷"),
    OTHER("other", "其他劳动纠纷");

    private final String code;
    private final String name;

    CaseType(String code, String name) {
        this.code = code;
        this.name = name;
    }

    public static CaseType fromCode(String code) {
        for (CaseType type : values()) {
            if (type.getCode().equals(code)) {
                return type;
            }
        }
        return null;
    }
}
