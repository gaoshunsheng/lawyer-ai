package com.lawyer.service.cases.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lawyer.service.cases.entity.Case;
import org.apache.ibatis.annotations.Mapper;

/**
 * 案件Mapper
 */
@Mapper
public interface CaseMapper extends BaseMapper<Case> {
}
