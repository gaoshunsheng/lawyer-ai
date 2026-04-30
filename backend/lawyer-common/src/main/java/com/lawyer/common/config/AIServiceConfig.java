package com.lawyer.common.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * AI服务配置
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "ai.service")
public class AIServiceConfig {

    /**
     * AI服务地址
     */
    private String url = "http://localhost:8001";

    /**
     * 连接超时时间（毫秒）
     */
    private Integer connectTimeout = 5000;

    /**
     * 读取超时时间（毫秒）
     */
    private Integer readTimeout = 60000;

    /**
     * 是否启用AI服务
     */
    private Boolean enabled = true;

    /**
     * 默认模型
     */
    private String defaultModel = "gpt-4-turbo-preview";

    /**
     * 默认温度
     */
    private Double defaultTemperature = 0.7;

    /**
     * 最大Token数
     */
    private Integer maxTokens = 4000;
}
