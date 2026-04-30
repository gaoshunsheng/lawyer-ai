package com.lawyer.api.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.dto.user.LoginRequest;
import com.lawyer.common.dto.user.LoginResponse;
import com.lawyer.common.dto.user.RegisterRequest;
import com.lawyer.common.enums.UserRole;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 认证流程集成测试
 * 测试完整的用户注册、登录、Token刷新流程
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class AuthIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserMapper userMapper;

    private static String accessToken;
    private static String refreshToken;
    private static Long userId;

    @Test
    @Order(1)
    @DisplayName("完整注册流程")
    void testFullRegistrationFlow() throws Exception {
        // 1. 准备注册数据
        RegisterRequest registerRequest = new RegisterRequest();
        registerRequest.setUsername("integration_test_user");
        registerRequest.setPassword("Test@123456");
        registerRequest.setEmail("integration@test.com");
        registerRequest.setPhone("13900139000");
        registerRequest.setRealName("集成测试用户");

        // 2. 执行注册
        MvcResult result = mockMvc.perform(post("/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(registerRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.id").exists())
                .andExpect(jsonPath("$.data.username").value("integration_test_user"))
                .andReturn();

        // 3. 提取用户ID
        String response = result.getResponse().getContentAsString();
        userId = objectMapper.readTree(response).path("data").path("id").asLong();
    }

    @Test
    @Order(2)
    @DisplayName("登录流程")
    void testLoginFlow() throws Exception {
        // 1. 准备登录数据
        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername("integration_test_user");
        loginRequest.setPassword("Test@123456");

        // 2. 执行登录
        MvcResult result = mockMvc.perform(post("/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginRequest)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.accessToken").exists())
                .andExpect(jsonPath("$.data.refreshToken").exists())
                .andExpect(jsonPath("$.data.tokenType").value("Bearer"))
                .andReturn();

        // 3. 提取Token
        String response = result.getResponse().getContentAsString();
        accessToken = objectMapper.readTree(response).path("data").path("accessToken").asText();
        refreshToken = objectMapper.readTree(response).path("data").path("refreshToken").asText();

        Assertions.assertNotNull(accessToken, "Access token should not be null");
        Assertions.assertNotNull(refreshToken, "Refresh token should not be null");
    }

    @Test
    @Order(3)
    @DisplayName("使用Token访问受保护资源")
    void testAccessProtectedResource() throws Exception {
        // 使用Token访问用户信息
        mockMvc.perform(get("/auth/me")
                        .header("Authorization", "Bearer " + accessToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.username").value("integration_test_user"));
    }

    @Test
    @Order(4)
    @DisplayName("Token刷新流程")
    void testRefreshTokenFlow() throws Exception {
        // 1. 准备刷新Token请求
        String requestBody = String.format("{\"refreshToken\":\"%s\"}", refreshToken);

        // 2. 执行刷新
        MvcResult result = mockMvc.perform(post("/auth/refresh")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.accessToken").exists())
                .andReturn();

        // 3. 更新Token
        String response = result.getResponse().getContentAsString();
        String newAccessToken = objectMapper.readTree(response).path("data").path("accessToken").asText();
        Assertions.assertNotNull(newAccessToken, "New access token should not be null");
    }

    @Test
    @Order(5)
    @DisplayName("登出流程")
    void testLogoutFlow() throws Exception {
        // 执行登出
        mockMvc.perform(post("/auth/logout")
                        .header("Authorization", "Bearer " + accessToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }

    @Test
    @Order(6)
    @DisplayName("登录失败 - 错误密码")
    void testLoginWithWrongPassword() throws Exception {
        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername("integration_test_user");
        loginRequest.setPassword("WrongPassword");

        mockMvc.perform(post("/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginRequest)))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @Order(7)
    @DisplayName("注册失败 - 用户名已存在")
    void testRegisterWithExistingUsername() throws Exception {
        RegisterRequest registerRequest = new RegisterRequest();
        registerRequest.setUsername("integration_test_user");
        registerRequest.setPassword("Test@123456");
        registerRequest.setEmail("another@test.com");
        registerRequest.setPhone("13900139001");

        mockMvc.perform(post("/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(registerRequest)))
                .andExpect(status().isBadRequest());
    }

    @AfterAll
    static void cleanup(@Autowired UserMapper userMapper) {
        // 清理测试数据
        // 实际项目中可以使用@Transactional自动回滚
    }
}
