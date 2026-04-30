package com.lawyer.service.knowledge.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lawyer.service.knowledge.entity.Knowledge;
import org.apache.ibatis.annotations.Mapper;

/**
 * 知识库Mapper
 */
@Mapper
public interface KnowledgeMapper extends BaseMapper<Knowledge> {
}
