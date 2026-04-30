package com.lawyer.service.user.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import com.lawyer.common.entity.BaseEntity;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 租户实体（律所）
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("tenants")
public class Tenant extends BaseEntity {

    /**
     * 律所名称
     */
    private String name;

    /**
     * 律所编码
     */
    private String code;

    /**
     * 联系人
     */
    private String contactPerson;

    /**
     * 联系电话
     */
    private String contactPhone;

    /**
     * 地址
     */
    private String address;

    /**
     * 状态：0-禁用，1-启用
     */
    private Integer status;

    /**
     * 到期时间
     */
    private java.time.LocalDateTime expireTime;

    /**
     * 最大用户数
     */
    private Integer maxUsers;

    /**
     * 当前用户数
     */
    private Integer currentUserCount;
}
