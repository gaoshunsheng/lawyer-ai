package com.lawyer.service.ai.service;

import com.lawyer.common.dto.ai.*;
import com.lawyer.common.client.AIServiceClient;
import com.lawyer.service.cases.entity.Case;
import com.lawyer.service.cases.mapper.CaseMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AI文书服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AIDocumentService {

    private final AIServiceClient aiServiceClient;
    private final CaseMapper caseMapper;

    /**
     * 生成文书
     *
     * @param templateId 模板ID
     * @param caseId     案件ID
     * @param variables  变量
     * @param style      风格
     * @return 生成的文书
     */
    public DocumentGenerateResponse generateDocument(String templateId, Long caseId,
                                                      Map<String, Object> variables, String style) {
        // 如果关联了案件，自动填充案件信息
        if (caseId != null && variables == null) {
            variables = new HashMap<>();
            Case caseEntity = caseMapper.selectById(caseId);
            if (caseEntity != null) {
                variables.putAll(extractCaseVariables(caseEntity));
            }
        }

        DocumentGenerateRequest request = DocumentGenerateRequest.builder()
                .templateId(templateId)
                .caseId(caseId)
                .variables(variables)
                .style(style != null ? style : "formal")
                .build();

        return aiServiceClient.generateDocument(request);
    }

    /**
     * 生成仲裁申请书
     *
     * @param caseId 案件ID
     * @return 生成的文书
     */
    public DocumentGenerateResponse generateArbitrationApplication(Long caseId) {
        return generateDocument("arbitration_application", caseId, null, "formal");
    }

    /**
     * 生成起诉状
     *
     * @param caseId 案件ID
     * @return 生成的文书
     */
    public DocumentGenerateResponse generateComplaint(Long caseId) {
        return generateDocument("complaint", caseId, null, "formal");
    }

    /**
     * 生成答辩状
     *
     * @param caseId 案件ID
     * @return 生成的文书
     */
    public DocumentGenerateResponse generateDefenseStatement(Long caseId) {
        return generateDocument("defense_statement", caseId, null, "formal");
    }

    /**
     * 生成律师函
     *
     * @param variables 变量
     * @return 生成的文书
     */
    public DocumentGenerateResponse generateLawyerLetter(Map<String, Object> variables) {
        return generateDocument("lawyer_letter", null, variables, "formal");
    }

    /**
     * 生成和解协议
     *
     * @param caseId   案件ID
     * @param variables 变量
     * @return 生成的文书
     */
    public DocumentGenerateResponse generateSettlementAgreement(Long caseId, Map<String, Object> variables) {
        return generateDocument("settlement_agreement", caseId, variables, "formal");
    }

    /**
     * 分析文书
     *
     * @param content 文书内容
     * @param docType 文书类型
     * @return 分析结果
     */
    public Map<String, Object> analyzeDocument(String content, String docType) {
        return aiServiceClient.analyzeDocument(content, docType);
    }

    /**
     * 获取文书模板列表
     *
     * @return 模板列表
     */
    public List<Map<String, Object>> getDocumentTemplates() {
        return aiServiceClient.getDocumentTemplates();
    }

    /**
     * 从案件实体提取变量
     */
    private Map<String, Object> extractCaseVariables(Case caseEntity) {
        Map<String, Object> variables = new HashMap<>();

        variables.put("案号", caseEntity.getCaseNumber());
        variables.put("案件类型", caseEntity.getCaseType() != null ? caseEntity.getCaseType().getName() : "");
        variables.put("案由", caseEntity.getCaseType() != null ? caseEntity.getCaseType().getName() : "");
        variables.put("标的金额", caseEntity.getClaimAmount());
        variables.put("案件简介", caseEntity.getDescription());

        // 当事人信息
        if (caseEntity.getPlaintiff() != null) {
            variables.put("申请人", caseEntity.getPlaintiff().get("name"));
            variables.put("申请人信息", caseEntity.getPlaintiff());
        }
        if (caseEntity.getDefendant() != null) {
            variables.put("被申请人", caseEntity.getDefendant().get("name"));
            variables.put("被申请人信息", caseEntity.getDefendant());
        }

        return variables;
    }
}
