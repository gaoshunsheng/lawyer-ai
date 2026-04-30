package com.lawyer.api;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.config.AIServiceConfig;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;

/**
 * 测试基类
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
public abstract class BaseTest {

    @Autowired
    protected MockMvc mockMvc;

    @Autowired
    protected ObjectMapper objectMapper;

    @MockBean
    protected UserMapper userMapper;

    @MockBean
    protected AIServiceConfig aiServiceConfig;

    @BeforeEach
    void setUpBase() {
        // Mock用户信息
        User mockUser = new User();
        mockUser.setId(1L);
        mockUser.setUsername("testuser");
        mockUser.setRealName("测试用户");
        mockUser.setTenantId(1L);
        mockUser.setStatus(1);

        when(userMapper.selectById(anyLong())).thenReturn(mockUser);

        // Mock AI服务配置
        when(aiServiceConfig.getEnabled()).thenReturn(false);
        when(aiServiceConfig.getUrl()).thenReturn("http://localhost:8001");
    }

    /**
     * 创建测试用户
     */
    protected User createTestUser() {
        User user = new User();
        user.setId(1L);
        user.setUsername("testuser");
        user.setRealName("测试用户");
        user.setEmail("test@example.com");
        user.setPhone("13800138000");
        user.setTenantId(1L);
        user.setStatus(1);
        return user;
    }

    /**
     * 将对象转换为JSON字符串
     */
    protected String toJson(Object obj) throws Exception {
        return objectMapper.writeValueAsString(obj);
    }
}
