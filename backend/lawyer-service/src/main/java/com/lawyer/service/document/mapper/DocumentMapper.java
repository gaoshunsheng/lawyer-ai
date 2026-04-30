package com.lawyer.service.document.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lawyer.service.document.entity.Document;
import org.apache.ibatis.annotations.Mapper;

/**
 * 文书Mapper
 */
@Mapper
public interface DocumentMapper extends BaseMapper<Document> {
}
