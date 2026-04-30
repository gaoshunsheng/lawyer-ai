package com.lawyer.api.controller;

import com.lawyer.api.BaseTest;
import com.lawyer.common.dto.user.LoginRequest;
import com.lawyer.common.dto.user.RegisterRequest;
import com.lawyer.common.enums.UserRole;
import com.lawyer.service.user.service.AuthService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 认证控制器测试
 */
class AuthControllerTest extends BaseTest {

    @MockBean
    private AuthService authService;

    @Test
    @DisplayName("用户登录 - 成功")
    void testLogin() throws Exception {
        // 准备测试数据
        LoginRequest request = new LoginRequest();
        request.setUsername("testuser");
        request.setPassword("password123");

        // Mock服务返回
        com.lawyer.api.dto.user.LoginResponse mockResponse =
            com.lawyer.api.dto.user.LoginResponse.builder()
                .accessToken("test-access-token")
                .refreshToken("test-refresh-token")
                .tokenType("Bearer")
                .expiresIn(7200L)
                .username("testuser")
                .realName("测试用户")
                .role(UserRole.LAWYER)
                .build();

        when(authService.login(any())).thenReturn(mockResponse);

        // 执行测试
        mockMvc.perform(post("/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.accessToken").value("test-access-token"));
    }

    @Test
    @DisplayName("用户注册 - 成功")
    void testRegister() throws Exception {
        // 准备测试数据
        RegisterRequest request = new RegisterRequest();
        request.setUsername("newuser");
        request.setPassword("password123");
        request.setEmail("newuser@example.com");
        request.setPhone("13800138001");
        request.setRealName("新用户");

        // Mock服务返回
        com.lawyer.api.dto.user.UserInfo mockUserInfo =
            com.lawyer.api.dto.user.UserInfo.builder()
                .id(2L)
                .username("newuser")
                .email("newuser@example.com")
                .phone("13800138001")
                .realName("新用户")
                .role(UserRole.LAWYER)
                .build();

        when(authService.register(any())).thenReturn(mockUserInfo);

        // 执行测试
        mockMvc.perform(post("/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.username").value("newuser"));
    }

    @Test
    @DisplayName("获取当前用户信息 - 成功")
    void testGetCurrentUser() throws Exception {
        // Mock服务返回
        com.lawyer.api.dto.user.UserInfo mockUserInfo =
            com.lawyer.api.dto.user.UserInfo.builder()
                .id(1L)
                .username("testuser")
                .realName("测试用户")
                .role(UserRole.LAWYER)
                .build();

        when(authService.getCurrentUser()).thenReturn(mockUserInfo);

        // 执行测试
        mockMvc.perform(get("/auth/me"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @DisplayName("刷新Token - 成功")
    void testRefreshToken() throws Exception {
        // Mock服务返回
        com.lawyer.api.dto.user.LoginResponse mockResponse =
            com.lawyer.api.dto.user.LoginResponse.builder()
                .accessToken("new-access-token")
                .refreshToken("new-refresh-token")
                .tokenType("Bearer")
                .expiresIn(7200L)
                .build();

        when(authService.refreshToken(any())).thenReturn(mockResponse);

        // 执行测试
        com.lawyer.api.dto.user.RefreshTokenRequest request =
            new com.lawyer.api.dto.user.RefreshTokenRequest();
        request.setRefreshToken("test-refresh-token");

        mockMvc.perform(post("/auth/refresh")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(toJson(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
}
