package com.lawyer.service.cases.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lawyer.service.cases.entity.TimelineEventEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 时间线事件Mapper
 */
@Mapper
public interface TimelineEventMapper extends BaseMapper<TimelineEventEntity> {
}
