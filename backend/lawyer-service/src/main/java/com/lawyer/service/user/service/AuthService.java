package com.lawyer.service.user.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.lawyer.common.enums.UserRole;
import com.lawyer.common.exception.BusinessException;
import com.lawyer.common.result.ResultCode;
import com.lawyer.common.utils.JwtUtils;
import com.lawyer.common.utils.PasswordUtils;
import com.lawyer.service.user.entity.Tenant;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.TenantMapper;
import com.lawyer.service.user.mapper.UserMapper;
import com.lawyer.common.dto.user.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

/**
 * 认证服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserMapper userMapper;
    private final TenantMapper tenantMapper;
    private final JwtUtils jwtUtils;

    /**
     * 用户登录
     */
    public LoginResponse login(LoginRequest request, String clientIp) {
        // 查询用户
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, request.getUsername())
                        .eq(User::getIsDeleted, 0)
        );

        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        // 验证密码
        if (!PasswordUtils.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(ResultCode.PASSWORD_ERROR);
        }

        // 检查用户状态
        if (user.getStatus() != 1) {
            throw new BusinessException(ResultCode.USER_DISABLED);
        }

        // 检查租户状态
        Tenant tenant = tenantMapper.selectById(user.getTenantId());
        if (tenant == null || tenant.getStatus() != 1) {
            throw new BusinessException(ResultCode.TENANT_DISABLED);
        }

        if (tenant.getExpireTime() != null && tenant.getExpireTime().isBefore(LocalDateTime.now())) {
            throw new BusinessException(ResultCode.TENANT_EXPIRED);
        }

        // 更新登录信息
        user.setLastLoginTime(LocalDateTime.now());
        user.setLastLoginIp(clientIp);
        userMapper.updateById(user);

        // 生成令牌
        String accessToken = jwtUtils.generateToken(user.getId(), user.getUsername(),
                user.getRole().getCode(), user.getTenantId());
        String refreshToken = jwtUtils.generateRefreshToken(user.getId(), user.getUsername());

        // 构建响应
        return LoginResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(7200L) // 2小时
                .userInfo(buildUserInfo(user, tenant))
                .build();
    }

    /**
     * 用户注册
     */
    @Transactional(rollbackFor = Exception.class)
    public LoginResponse register(RegisterRequest request) {
        // 检查用户名是否已存在
        Long count = userMapper.selectCount(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, request.getUsername())
                        .eq(User::getIsDeleted, 0)
        );
        if (count > 0) {
            throw new BusinessException(ResultCode.USERNAME_EXISTS);
        }

        // 获取租户
        Tenant tenant = null;
        if (request.getTenantId() != null) {
            tenant = tenantMapper.selectById(request.getTenantId());
            if (tenant == null) {
                throw new BusinessException(ResultCode.TENANT_NOT_FOUND);
            }
            // 检查用户数限制
            if (tenant.getMaxUsers() != null && tenant.getCurrentUserCount() >= tenant.getMaxUsers()) {
                throw new BusinessException(ResultCode.TENANT_USER_LIMIT);
            }
        }

        // 创建用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(PasswordUtils.encode(request.getPassword()));
        user.setRealName(request.getRealName());
        user.setPhone(request.getPhone());
        user.setEmail(request.getEmail());
        user.setRole(request.getRole() != null ? UserRole.fromCode(request.getRole()) : UserRole.ASSISTANT);
        user.setTenantId(request.getTenantId());
        user.setStatus(1);
        userMapper.insert(user);

        // 更新租户用户数
        if (tenant != null) {
            tenant.setCurrentUserCount(tenant.getCurrentUserCount() + 1);
            tenantMapper.updateById(tenant);
        }

        // 生成令牌
        String accessToken = jwtUtils.generateToken(user.getId(), user.getUsername(),
                user.getRole().getCode(), user.getTenantId());
        String refreshToken = jwtUtils.generateRefreshToken(user.getId(), user.getUsername());

        return LoginResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(7200L)
                .userInfo(buildUserInfo(user, tenant))
                .build();
    }

    /**
     * 刷新令牌
     */
    public LoginResponse refreshToken(String refreshToken) {
        // 验证刷新令牌
        if (!jwtUtils.validateToken(refreshToken) || !jwtUtils.isRefreshToken(refreshToken)) {
            throw new BusinessException(ResultCode.TOKEN_INVALID);
        }

        // 获取用户
        Long userId = jwtUtils.getUserIdFromToken(refreshToken);
        User user = userMapper.selectById(userId);
        if (user == null || user.getStatus() != 1) {
            throw new BusinessException(ResultCode.USER_DISABLED);
        }

        // 获取租户
        Tenant tenant = tenantMapper.selectById(user.getTenantId());
        if (tenant == null || tenant.getStatus() != 1) {
            throw new BusinessException(ResultCode.TENANT_DISABLED);
        }

        // 生成新令牌
        String newAccessToken = jwtUtils.generateToken(user.getId(), user.getUsername(),
                user.getRole().getCode(), user.getTenantId());
        String newRefreshToken = jwtUtils.generateRefreshToken(user.getId(), user.getUsername());

        return LoginResponse.builder()
                .accessToken(newAccessToken)
                .refreshToken(newRefreshToken)
                .tokenType("Bearer")
                .expiresIn(7200L)
                .userInfo(buildUserInfo(user, tenant))
                .build();
    }

    /**
     * 修改密码
     */
    public void changePassword(Long userId, ChangePasswordRequest request) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        // 验证原密码
        if (!PasswordUtils.matches(request.getOldPassword(), user.getPassword())) {
            throw new BusinessException(ResultCode.PASSWORD_ERROR);
        }

        // 更新密码
        user.setPassword(PasswordUtils.encode(request.getNewPassword()));
        userMapper.updateById(user);
    }

    /**
     * 获取当前用户信息
     */
    public UserInfo getCurrentUser(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        Tenant tenant = user.getTenantId() != null ? tenantMapper.selectById(user.getTenantId()) : null;
        return buildUserInfo(user, tenant);
    }

    /**
     * 构建用户信息
     */
    private UserInfo buildUserInfo(User user, Tenant tenant) {
        return UserInfo.builder()
                .id(user.getId())
                .username(user.getUsername())
                .realName(user.getRealName())
                .phone(user.getPhone())
                .email(user.getEmail())
                .role(user.getRole())
                .roleName(user.getRole() != null ? user.getRole().getDescription() : null)
                .tenantId(user.getTenantId())
                .tenantName(tenant != null ? tenant.getName() : null)
                .avatar(user.getAvatar())
                .status(user.getStatus())
                .build();
    }
}
