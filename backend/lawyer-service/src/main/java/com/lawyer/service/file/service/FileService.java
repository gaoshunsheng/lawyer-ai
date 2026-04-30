package com.lawyer.service.file.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.file.entity.FileEntity;
import com.lawyer.service.file.mapper.FileMapper;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.file.FileInfo;
import com.lawyer.common.dto.file.FileQueryRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * 文件服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FileService {

    private final FileMapper fileMapper;
    private final UserMapper userMapper;

    @Value("${file.upload.path:./uploads}")
    private String uploadPath;

    @Value("${file.upload.url-prefix:/files}")
    private String urlPrefix;

    @Value("${file.upload.max-size:20971520}")
    private long maxFileSize;

    // 允许的文件类型
    private static final List<String> ALLOWED_EXTENSIONS = List.of(
            "doc", "docx", "pdf", "xls", "xlsx", "ppt", "pptx",
            "jpg", "jpeg", "png", "gif", "bmp",
            "txt", "zip", "rar"
    );

    // 图片类型
    private static final List<String> IMAGE_EXTENSIONS = List.of("jpg", "jpeg", "png", "gif", "bmp");

    // 文档类型
    private static final List<String> DOCUMENT_EXTENSIONS = List.of("doc", "docx", "pdf", "xls", "xlsx", "ppt", "pptx", "txt");

    /**
     * 上传文件
     */
    @Transactional(rollbackFor = Exception.class)
    public FileInfo uploadFile(MultipartFile file, String category, Long relatedId, String relatedType, String description) {
        // 验证文件
        validateFile(file);

        Long userId = SecurityUtils.getCurrentUserId();
        User user = userMapper.selectById(userId);
        Long tenantId = user != null ? user.getTenantId() : null;

        // 获取原始文件名
        String originalName = file.getOriginalFilename();
        String extension = getFileExtension(originalName);

        // 生成存储文件名
        String storedName = UUID.randomUUID().toString() + "." + extension;

        // 按日期分目录存储
        String datePath = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM/dd"));
        String categoryPath = category != null ? category : "common";
        String fullPath = uploadPath + "/" + categoryPath + "/" + datePath;

        // 创建目录
        try {
            Path directory = Paths.get(fullPath);
            if (!Files.exists(directory)) {
                Files.createDirectories(directory);
            }
        } catch (IOException e) {
            log.error("创建目录失败: {}", fullPath, e);
            throw new BusinessException(ResultCode.FAIL, "文件上传失败");
        }

        // 保存文件
        String filePath = fullPath + "/" + storedName;
        try {
            file.transferTo(new File(filePath));
        } catch (IOException e) {
            log.error("保存文件失败: {}", filePath, e);
            throw new BusinessException(ResultCode.FAIL, "文件保存失败");
        }

        // 生成访问URL
        String fileUrl = urlPrefix + "/" + categoryPath + "/" + datePath + "/" + storedName;

        // 获取MIME类型
        String fileType = file.getContentType();

        // 保存文件信息到数据库
        FileEntity fileEntity = new FileEntity();
        fileEntity.setOriginalName(originalName);
        fileEntity.setStoredName(storedName);
        fileEntity.setFilePath(filePath);
        fileEntity.setFileUrl(fileUrl);
        fileEntity.setFileType(fileType);
        fileEntity.setFileExtension(extension);
        fileEntity.setFileSize(file.getSize());
        fileEntity.setCategory(category);
        fileEntity.setRelatedId(relatedId);
        fileEntity.setRelatedType(relatedType);
        fileEntity.setTenantId(tenantId);
        fileEntity.setDescription(description);
        fileEntity.setCreatedBy(userId);
        fileEntity.setUpdatedBy(userId);

        fileMapper.insert(fileEntity);

        return convertToFileInfo(fileEntity);
    }

    /**
     * 获取文件信息
     */
    public FileInfo getFileInfo(Long id) {
        FileEntity fileEntity = fileMapper.selectById(id);
        if (fileEntity == null || fileEntity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND, "文件不存在");
        }
        return convertToFileInfo(fileEntity);
    }

    /**
     * 删除文件
     */
    @Transactional(rollbackFor = Exception.class)
    public void deleteFile(Long id) {
        Long userId = SecurityUtils.getCurrentUserId();

        FileEntity fileEntity = fileMapper.selectById(id);
        if (fileEntity == null || fileEntity.getIsDeleted() == 1) {
            throw new BusinessException(ResultCode.RESOURCE_NOT_FOUND, "文件不存在");
        }

        // 删除物理文件
        try {
            Path path = Paths.get(fileEntity.getFilePath());
            if (Files.exists(path)) {
                Files.delete(path);
            }
        } catch (IOException e) {
            log.error("删除物理文件失败: {}", fileEntity.getFilePath(), e);
        }

        // 软删除数据库记录
        fileEntity.setIsDeleted(1);
        fileEntity.setUpdatedBy(userId);
        fileMapper.updateById(fileEntity);
    }

    /**
     * 查询文件列表
     */
    public IPage<FileInfo> queryFiles(FileQueryRequest request, Long tenantId) {
        Page<FileEntity> page = new Page<>(request.getPage(), request.getPageSize());

        LambdaQueryWrapper<FileEntity> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(FileEntity::getIsDeleted, 0);

        // 租户过滤
        if (tenantId != null) {
            wrapper.eq(FileEntity::getTenantId, tenantId);
        }

        // 分类过滤
        if (request.getCategory() != null && !request.getCategory().isEmpty()) {
            wrapper.eq(FileEntity::getCategory, request.getCategory());
        }

        // 关联ID过滤
        if (request.getRelatedId() != null) {
            wrapper.eq(FileEntity::getRelatedId, request.getRelatedId());
        }

        // 关联类型过滤
        if (request.getRelatedType() != null && !request.getRelatedType().isEmpty()) {
            wrapper.eq(FileEntity::getRelatedType, request.getRelatedType());
        }

        // 关键词搜索
        if (request.getKeyword() != null && !request.getKeyword().isEmpty()) {
            wrapper.like(FileEntity::getOriginalName, request.getKeyword());
        }

        // 文件类型过滤
        if (request.getFileType() != null && !request.getFileType().isEmpty()) {
            wrapper.like(FileEntity::getFileType, request.getFileType());
        }

        wrapper.orderByDesc(FileEntity::getCreatedAt);

        IPage<FileEntity> filePage = fileMapper.selectPage(page, wrapper);

        return filePage.convert(this::convertToFileInfo);
    }

    /**
     * 根据关联信息获取文件列表
     */
    public List<FileInfo> getFilesByRelated(String relatedType, Long relatedId) {
        LambdaQueryWrapper<FileEntity> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(FileEntity::getIsDeleted, 0)
                .eq(FileEntity::getRelatedType, relatedType)
                .eq(FileEntity::getRelatedId, relatedId)
                .orderByDesc(FileEntity::getCreatedAt);

        List<FileEntity> files = fileMapper.selectList(wrapper);
        return files.stream()
                .map(this::convertToFileInfo)
                .collect(Collectors.toList());
    }

    /**
     * 验证文件
     */
    private void validateFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ResultCode.PARAM_ERROR, "文件不能为空");
        }

        // 验证文件大小
        if (file.getSize() > maxFileSize) {
            throw new BusinessException(ResultCode.PARAM_ERROR,
                    "文件大小超过限制，最大允许" + (maxFileSize / 1024 / 1024) + "MB");
        }

        // 验证文件扩展名
        String extension = getFileExtension(file.getOriginalFilename());
        if (extension == null || !ALLOWED_EXTENSIONS.contains(extension.toLowerCase())) {
            throw new BusinessException(ResultCode.PARAM_ERROR, "不支持的文件类型");
        }
    }

    /**
     * 获取文件扩展名
     */
    private String getFileExtension(String filename) {
        if (filename == null || filename.isEmpty()) {
            return null;
        }
        int lastDot = filename.lastIndexOf('.');
        if (lastDot == -1) {
            return null;
        }
        return filename.substring(lastDot + 1).toLowerCase();
    }

    /**
     * 转换为FileInfo
     */
    private FileInfo convertToFileInfo(FileEntity entity) {
        FileInfo info = new FileInfo();
        info.setId(entity.getId());
        info.setOriginalName(entity.getOriginalName());
        info.setStoredName(entity.getStoredName());
        info.setFilePath(entity.getFilePath());
        info.setFileUrl(entity.getFileUrl());
        info.setFileType(entity.getFileType());
        info.setFileExtension(entity.getFileExtension());
        info.setFileSize(entity.getFileSize());
        info.setCategory(entity.getCategory());
        info.setRelatedId(entity.getRelatedId());
        info.setRelatedType(entity.getRelatedType());
        info.setDescription(entity.getDescription());
        info.setTenantId(entity.getTenantId());
        info.setCreatedBy(entity.getCreatedBy());
        info.setCreatedAt(entity.getCreatedAt() != null ? entity.getCreatedAt().toString() : null);

        // 获取创建人姓名
        if (entity.getCreatedBy() != null) {
            User user = userMapper.selectById(entity.getCreatedBy());
            if (user != null) {
                info.setCreatedByName(user.getRealName());
            }
        }

        return info;
    }
}
