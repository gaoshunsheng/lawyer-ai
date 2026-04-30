package com.lawyer.api.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.lawyer.common.result.Result;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.file.FileInfo;
import com.lawyer.common.dto.file.FileQueryRequest;
import com.lawyer.service.file.service.FileService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * 文件管理控制器
 */
@Tag(name = "文件管理", description = "文件上传、下载、删除接口")
@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {

    private final FileService fileService;
    private final UserMapper userMapper;

    /**
     * 上传文件
     */
    @Operation(summary = "上传文件", description = "上传单个文件")
    @PostMapping("/upload")
    public Result<FileInfo> uploadFile(
            @Parameter(description = "文件") @RequestParam("file") MultipartFile file,
            @Parameter(description = "文件分类") @RequestParam(required = false) String category,
            @Parameter(description = "关联ID") @RequestParam(required = false) Long relatedId,
            @Parameter(description = "关联类型") @RequestParam(required = false) String relatedType,
            @Parameter(description = "描述") @RequestParam(required = false) String description) {

        FileInfo fileInfo = fileService.uploadFile(file, category, relatedId, relatedType, description);
        return Result.success(fileInfo);
    }

    /**
     * 批量上传文件
     */
    @Operation(summary = "批量上传文件", description = "批量上传多个文件")
    @PostMapping("/upload/batch")
    public Result<List<FileInfo>> uploadFiles(
            @Parameter(description = "文件列表") @RequestParam("files") MultipartFile[] files,
            @Parameter(description = "文件分类") @RequestParam(required = false) String category,
            @Parameter(description = "关联ID") @RequestParam(required = false) Long relatedId,
            @Parameter(description = "关联类型") @RequestParam(required = false) String relatedType) {

        List<FileInfo> results = new java.util.ArrayList<>();
        for (MultipartFile file : files) {
            FileInfo fileInfo = fileService.uploadFile(file, category, relatedId, relatedType, null);
            results.add(fileInfo);
        }
        return Result.success(results);
    }

    /**
     * 获取文件信息
     */
    @Operation(summary = "获取文件信息", description = "根据ID获取文件信息")
    @GetMapping("/{id}")
    public Result<FileInfo> getFileInfo(@Parameter(description = "文件ID") @PathVariable Long id) {
        FileInfo fileInfo = fileService.getFileInfo(id);
        return Result.success(fileInfo);
    }

    /**
     * 下载文件
     */
    @Operation(summary = "下载文件", description = "根据ID下载文件")
    @GetMapping("/{id}/download")
    public ResponseEntity<Resource> downloadFile(@Parameter(description = "文件ID") @PathVariable Long id) {
        FileInfo fileInfo = fileService.getFileInfo(id);

        File file = new File(fileInfo.getFilePath());
        if (!file.exists()) {
            return ResponseEntity.notFound().build();
        }

        Resource resource = new FileSystemResource(file);

        // 编码文件名
        String encodedFilename;
        try {
            encodedFilename = URLEncoder.encode(fileInfo.getOriginalName(), StandardCharsets.UTF_8.toString())
                    .replaceAll("\\+", "%20");
        } catch (UnsupportedEncodingException e) {
            encodedFilename = fileInfo.getStoredName();
        }

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(fileInfo.getFileType()))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + encodedFilename + "\"")
                .body(resource);
    }

    /**
     * 删除文件
     */
    @Operation(summary = "删除文件", description = "删除指定文件")
    @DeleteMapping("/{id}")
    public Result<Void> deleteFile(@Parameter(description = "文件ID") @PathVariable Long id) {
        fileService.deleteFile(id);
        return Result.success();
    }

    /**
     * 查询文件列表
     */
    @Operation(summary = "查询文件列表", description = "根据条件分页查询文件列表")
    @GetMapping
    public Result<IPage<FileInfo>> queryFiles(FileQueryRequest request) {
        Long tenantId = null;
        Long userId = SecurityUtils.getCurrentUserId();
        if (userId != null) {
            User user = userMapper.selectById(userId);
            if (user != null) {
                tenantId = user.getTenantId();
            }
        }
        IPage<FileInfo> page = fileService.queryFiles(request, tenantId);
        return Result.success(page);
    }

    /**
     * 根据关联信息获取文件
     */
    @Operation(summary = "获取关联文件", description = "根据关联类型和ID获取文件列表")
    @GetMapping("/related")
    public Result<List<FileInfo>> getFilesByRelated(
            @Parameter(description = "关联类型") @RequestParam String relatedType,
            @Parameter(description = "关联ID") @RequestParam Long relatedId) {
        List<FileInfo> files = fileService.getFilesByRelated(relatedType, relatedId);
        return Result.success(files);
    }

    /**
     * 获取案件文件
     */
    @Operation(summary = "获取案件文件", description = "获取指定案件的所有文件")
    @GetMapping("/case/{caseId}")
    public Result<List<FileInfo>> getCaseFiles(@Parameter(description = "案件ID") @PathVariable Long caseId) {
        List<FileInfo> files = fileService.getFilesByRelated("case", caseId);
        return Result.success(files);
    }

    /**
     * 获取证据文件
     */
    @Operation(summary = "获取证据文件", description = "获取指定证据的文件")
    @GetMapping("/evidence/{evidenceId}")
    public Result<List<FileInfo>> getEvidenceFiles(@Parameter(description = "证据ID") @PathVariable Long evidenceId) {
        List<FileInfo> files = fileService.getFilesByRelated("evidence", evidenceId);
        return Result.success(files);
    }
}
