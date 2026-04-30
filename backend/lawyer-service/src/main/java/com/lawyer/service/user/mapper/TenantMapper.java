package com.lawyer.service.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lawyer.service.user.entity.Tenant;
import org.apache.ibatis.annotations.Mapper;

/**
 * 租户Mapper
 */
@Mapper
public interface TenantMapper extends BaseMapper<Tenant> {
}
