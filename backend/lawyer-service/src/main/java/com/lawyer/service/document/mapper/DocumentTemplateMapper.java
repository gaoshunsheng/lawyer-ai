package com.lawyer.service.document.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lawyer.service.document.entity.DocumentTemplate;
import org.apache.ibatis.annotations.Mapper;

/**
 * 文书模板Mapper
 */
@Mapper
public interface DocumentTemplateMapper extends BaseMapper<DocumentTemplate> {
}
