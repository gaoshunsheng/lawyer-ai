package com.lawyer.service.file.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.lawyer.service.file.entity.FileEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 文件Mapper
 */
@Mapper
public interface FileMapper extends BaseMapper<FileEntity> {
}
