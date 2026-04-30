package com.lawyer.api;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * 律师AI助手启动类
 */
@SpringBootApplication
@ComponentScan(basePackages = "com.lawyer")
@MapperScan(basePackages = "com.lawyer.*.mapper")
public class LawyerAiApplication {

    public static void main(String[] args) {
        SpringApplication.run(LawyerAiApplication.class, args);
        System.out.println("======================================");
        System.out.println("   律师AI助手启动成功！");
        System.out.println("   API文档: http://localhost:8080/api/doc.html");
        System.out.println("======================================");
    }
}
