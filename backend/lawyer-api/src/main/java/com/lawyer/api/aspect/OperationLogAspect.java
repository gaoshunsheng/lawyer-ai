package com.lawyer.api.aspect;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lawyer.common.annotation.Log;
import com.lawyer.common.utils.SecurityUtils;
import com.lawyer.service.log.entity.OperationLog;
import com.lawyer.service.log.service.OperationLogService;
import com.lawyer.service.user.entity.User;
import com.lawyer.service.user.mapper.UserMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.multipart.MultipartFile;

import java.lang.reflect.Method;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 操作日志切面
 * 自动记录Controller层的操作日志
 */
@Slf4j
@Aspect
@Component
@RequiredArgsConstructor
public class OperationLogAspect {

    private final OperationLogService operationLogService;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;

    /**
     * 切入点：所有Controller层的public方法
     */
    @Pointcut("execution(public * com.lawyer.api.controller.*.*(..))")
    public void controllerPointcut() {
    }

    /**
     * 需要记录日志的方法（带有@Log注解的方法）
     */
    @Pointcut("@annotation(com.lawyer.common.annotation.Log)")
    public void logPointcut() {
    }

    /**
     * 后置通知：方法执行后记录日志
     */
    @AfterReturning(pointcut = "controllerPointcut() && logPointcut()", returning = "result")
    public void doAfterReturning(JoinPoint joinPoint, Object result) {
        handleLog(joinPoint, null, result);
    }

    /**
     * 异常通知：方法异常时记录日志
     */
    @AfterThrowing(pointcut = "controllerPointcut() && logPointcut()", throwing = "e")
    public void doAfterThrowing(JoinPoint joinPoint, Exception e) {
        handleLog(joinPoint, e, null);
    }

    /**
     * 处理日志记录
     */
    private void handleLog(JoinPoint joinPoint, Exception e, Object result) {
        try {
            // 获取注解
            MethodSignature signature = (MethodSignature) joinPoint.getSignature();
            Method method = signature.getMethod();
            Log logAnnotation = method.getAnnotation(Log.class);
            if (logAnnotation == null) {
                return;
            }

            // 获取请求信息
            HttpServletRequest request = getRequest();
            if (request == null) {
                return;
            }

            // 构建日志对象
            OperationLog operationLog = OperationLog.builder()
                    .operationType(logAnnotation.operationType().getCode())
                    .operationDesc(logAnnotation.description())
                    .requestMethod(request.getMethod())
                    .requestUrl(request.getRequestURI())
                    .requestParams(getRequestParams(joinPoint))
                    .responseStatus(e == null ? HttpServletResponse.SC_OK : HttpServletResponse.SC_INTERNAL_SERVER_ERROR)
                    .ipAddress(getClientIp(request))
                    .userAgent(request.getHeader("User-Agent"))
                    .createdAt(LocalDateTime.now())
                    .build();

            // 设置用户信息
            setUserInfo(operationLog);

            // 异步保存日志
            operationLogService.recordLogAsync(operationLog);

        } catch (Exception ex) {
            log.error("记录操作日志异常: {}", ex.getMessage());
        }
    }

    /**
     * 获取请求对象
     */
    private HttpServletRequest getRequest() {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        return attributes != null ? attributes.getRequest() : null;
    }

    /**
     * 获取请求参数
     */
    private String getRequestParams(JoinPoint joinPoint) {
        try {
            MethodSignature signature = (MethodSignature) joinPoint.getSignature();
            String[] paramNames = signature.getParameterNames();
            Object[] args = joinPoint.getArgs();

            if (paramNames == null || args == null) {
                return null;
            }

            Map<String, Object> params = new HashMap<>();
            for (int i = 0; i < paramNames.length; i++) {
                Object arg = args[i];
                if (arg instanceof HttpServletRequest
                        || arg instanceof HttpServletResponse
                        || arg instanceof MultipartFile) {
                    continue;
                }
                params.put(paramNames[i], arg);
            }

            String json = objectMapper.writeValueAsString(params);
            if (json.length() > 2000) {
                json = json.substring(0, 2000) + "...";
            }
            return json;
        } catch (Exception e) {
            log.warn("获取请求参数失败: {}", e.getMessage());
            return null;
        }
    }

    /**
     * 获取客户端IP
     */
    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("WL-Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("HTTP_CLIENT_IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("HTTP_X_FORWARDED_FOR");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        if (ip != null && ip.contains(",")) {
            ip = ip.split(",")[0].trim();
        }
        return ip;
    }

    /**
     * 设置用户信息
     */
    private void setUserInfo(OperationLog operationLog) {
        try {
            Long userId = SecurityUtils.getCurrentUserId();
            if (userId != null) {
                operationLog.setUserId(userId);
                User user = userMapper.selectById(userId);
                if (user != null) {
                    operationLog.setUsername(user.getUsername());
                    operationLog.setTenantId(user.getTenantId());
                }
            }
        } catch (Exception e) {
            log.warn("获取用户信息失败: {}", e.getMessage());
        }
    }
}
