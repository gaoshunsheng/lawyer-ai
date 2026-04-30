"""
模拟LLM服务 - 用于开发和测试
"""
import logging
from typing import List, AsyncGenerator
import random
import hashlib

from app.services.llm import BaseLLMService, ChatMessage, LLMResponse

logger = logging.getLogger(__name__)


class MockLLMService(BaseLLMService):
    """模拟LLM服务"""

    # 法律知识库
    LEGAL_KNOWLEDGE = {
        "劳动合同法": {
            "第39条": "劳动者有下列情形之一的，用人单位可以解除劳动合同：(一)在试用期间被证明不符合录用条件的；(二)严重违反用人单位的规章制度的；(三)严重失职，营私舞弊，给用人单位造成重大损害的；(四)劳动者同时与其他用人单位建立劳动关系，对完成本单位的工作任务造成严重影响，或者经用人单位提出，拒不改正的；(五)因本法第二十六条第一款第一项规定的情形致使劳动合同无效的；(六)被依法追究刑事责任的。",
            "第40条": "有下列情形之一的，用人单位提前三十日以书面形式通知劳动者本人或者额外支付劳动者一个月工资后，可以解除劳动合同：(一)劳动者患病或者非因工负伤，在规定的医疗期满后不能从事原工作，也不能从事由用人单位另行安排的工作的；(二)劳动者不能胜任工作，经过培训或者调整工作岗位，仍不能胜任工作的；(三)劳动合同订立时所依据的客观情况发生重大变化，致使劳动合同无法履行，经用人单位与劳动者协商，未能就变更劳动合同内容达成协议的。",
            "第47条": "经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。六个月以上不满一年的，按一年计算；不满六个月的，向劳动者支付半个月工资的经济补偿。劳动者月工资高于用人单位所在直辖市、设区的市级人民政府公布的本地区上年度职工月平均工资三倍的，向其支付经济补偿的标准按职工月平均工资三倍的数额支付，向其支付经济补偿的年限最高不超过十二年。本条所称月工资是指劳动者在劳动合同解除或者终止前十二个月的平均工资。",
            "第48条": "用人单位违反本法规定解除或者终止劳动合同，劳动者要求继续履行劳动合同的，用人单位应当继续履行；劳动者不要求继续履行劳动合同或者劳动合同已经不能继续履行的，用人单位应当依照本法第八十七条规定支付赔偿金。",
            "第87条": "用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第四十七条规定的经济补偿标准的二倍向劳动者支付赔偿金。"
        },
        "劳动法": {
            "第44条": "有下列情形之一的，用人单位应当按照下列标准支付高于劳动者正常工作时间工资的工资报酬：(一)安排劳动者延长工作时间的，支付不低于工资的百分之一百五十的工资报酬；(二)休息日安排劳动者工作又不能安排补休的，支付不低于工资的百分之二百的工资报酬；(三)法定休假日安排劳动者工作的，支付不低于工资的百分之三百的工资报酬。"
        }
    }

    async def chat(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ) -> LLMResponse:
        """同步聊天 - 模拟响应"""
        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.role == "user":
                user_message = msg.content
                break

        # 生成模拟响应
        content = self._generate_mock_response(user_message)

        return LLMResponse(
            content=content,
            tokens_used=len(content) // 2,
            model="mock-model",
            finish_reason="stop"
        )

    async def chat_stream(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天 - 模拟响应"""
        # 获取最后一条用户消息
        user_message = ""
        for msg in reversed(messages):
            if msg.role == "user":
                user_message = msg.content
                break

        # 生成模拟响应并逐字输出
        content = self._generate_mock_response(user_message)
        for char in content:
            yield char

    async def embed(self, text: str) -> List[float]:
        """生成文本嵌入向量 - 模拟向量"""
        # 使用哈希生成固定长度的模拟向量
        text_hash = hashlib.md5(text.encode()).hexdigest()
        random.seed(int(text_hash[:8], 16))
        embedding = [random.uniform(-1, 1) for _ in range(settings.EMBEDDING_DIMENSION)]
        # 归一化
        norm = sum(x * x for x in embedding) ** 0.5
        return [x / norm for x in embedding]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入向量"""
        return [await self.embed(text) for text in texts]

    def _generate_mock_response(self, user_message: str) -> str:
        """生成模拟响应"""
        user_message_lower = user_message.lower()

        # 违法解除
        if "违法解除" in user_message or "解除劳动合同" in user_message:
            return self._generate_termination_response(user_message)

        # 加班费
        if "加班" in user_message:
            return self._generate_overtime_response(user_message)

        # 年休假
        if "年休假" in user_message or "年假" in user_message:
            return self._generate_annual_leave_response(user_message)

        # 工伤
        if "工伤" in user_message:
            return self._generate_injury_response(user_message)

        # 工资
        if "工资" in user_message or "欠薪" in user_message:
            return self._generate_wage_response(user_message)

        # 默认响应
        return self._generate_default_response(user_message)

    def _generate_termination_response(self, user_message: str) -> str:
        """生成违法解除相关响应"""
        return f"""根据您咨询的问题，分析如下：

【法律依据】
{self.LEGAL_KNOWLEDGE['劳动合同法']['第39条']}

{self.LEGAL_KNOWLEDGE['劳动合同法']['第48条']}

{self.LEGAL_KNOWLEDGE['劳动合同法']['第87条']}

【关键事实分析】
1. 用人单位以劳动者严重违纪为由解除劳动合同，应当承担举证责任
2. 需要确认用人单位是否有合法有效的规章制度
3. 规章制度是否经过民主程序制定并公示
4. 劳动者的行为是否确实构成"严重违纪"

【胜诉概率评估】⭐⭐⭐⭐ (较高)

【类似案例参考】
📄 (2023)沪01民终12345号 - 用人单位仅有口头警告记录，法院认定证据不足
📄 (2022)京02民终6789号 - 规章制度未经民主程序，解除被认定违法

【建议策略】
1. 收集公司规章制度及公示证据
2. 保存考勤记录、工作记录等证据
3. 如有录音、聊天记录等，妥善保存
4. 申请证人出庭作证

【赔偿计算】
违法解除赔偿金 = 经济补偿金 × 2
经济补偿金 = 工作年限 × 解除前12个月平均工资

如需详细计算，可使用赔偿计算器功能。"""

    def _generate_overtime_response(self, user_message: str) -> str:
        """生成加班费相关响应"""
        return f"""关于加班费问题，分析如下：

【法律依据】
{self.LEGAL_KNOWLEDGE['劳动法']['第44条']}

【加班费计算标准】
1. 工作日加班：小时工资 × 150%
2. 休息日加班（不能安排补休）：小时工资 × 200%
3. 法定节假日加班：小时工资 × 300%

【小时工资计算】
小时工资 = 月工资 ÷ 21.75 ÷ 8

【举证要点】
1. 加班事实的举证责任在劳动者
2. 需要提供的证据：
   - 考勤记录（打卡记录、钉钉记录等）
   - 加班审批单
   - 工作邮件、工作群聊天记录
   - 工作成果的时间戳
   - 证人证言

【注意事项】
1. 如用人单位掌握考勤记录，可申请法院调查取证
2. 主张加班费的仲裁时效为1年
3. 需区分"值班"与"加班"

【建议】
1. 收集并保存所有加班证据
2. 计算准确的加班时长和金额
3. 可以通过赔偿计算器精确计算

如需具体计算，请提供：月工资标准、工作日加班小时、休息日加班小时、法定节假日加班小时。"""

    def _generate_annual_leave_response(self, user_message: str) -> str:
        """生成年休假相关响应"""
        return """关于年休假问题，分析如下：

【法律依据】
《职工带薪年休假条例》第3条：
职工累计工作已满1年不满10年的，年休假5天；已满10年不满20年的，年休假10天；已满20年的，年休假15天。

《企业职工带薪年休假实施办法》第10条：
用人单位经职工同意不安排年休假或者安排职工年休假天数少于应休年休假天数，应当对本年度应休未休年休假天数，按照其日工资收入的300%支付未休年休假工资报酬。

【年休假工资计算】
未休年休假工资 = 月工资 ÷ 21.75 × 未休天数 × 300%

【注意事项】
1. 年休假一般不跨年安排
2. 单位确因工作需要不能安排的，可跨1个年度安排
3. 职工因个人原因不休年休假的，不享受300%工资
4. 累计工作年限应提供社保记录、劳动合同等证明

【举证要点】
1. 工作年限证明
2. 应休年休假天数
3. 已休年休假记录
4. 未安排年休假的证据"""

    def _generate_injury_response(self, user_message: str) -> str:
        """生成工伤相关响应"""
        return """关于工伤问题，分析如下：

【工伤认定条件】
《工伤保险条例》第14条规定的工伤情形：
1. 在工作时间和工作场所内，因工作原因受到事故伤害的
2. 工作时间前后在工作场所内，从事与工作有关的预备性或者收尾性工作受到事故伤害的
3. 在工作时间和工作场所内，因履行工作职责受到暴力等意外伤害的
4. 患职业病的
5. 因工外出期间，由于工作原因受到伤害或者发生事故下落不明的
6. 在上下班途中，受到非本人主要责任的交通事故伤害的

【工伤赔偿项目】
1. 医疗费
2. 停工留薪期工资
3. 一次性伤残补助金
4. 一次性工伤医疗补助金
5. 一次性伤残就业补助金
6. 其他（护理费、辅助器具费等）

【工伤认定程序】
1. 用人单位30日内申请工伤认定
2. 单位不申请的，职工或家属可在1年内申请
3. 工伤认定决定书
4. 劳动能力鉴定
5. 申请工伤待遇

【建议】
1. 及时就医并保留所有医疗记录
2. 收集劳动关系证据
3. 尽快申请工伤认定
4. 进行劳动能力鉴定
5. 根据鉴定等级计算赔偿金额"""

    def _generate_wage_response(self, user_message: str) -> str:
        """生成工资相关响应"""
        return """关于工资问题，分析如下：

【法律依据】
《劳动法》第50条：工资应当以货币形式按月支付给劳动者本人。不得克扣或者无故拖欠劳动者的工资。

《劳动合同法》第30条：用人单位应当按照劳动合同约定和国家规定，向劳动者及时足额支付劳动报酬。

【欠薪维权途径】
1. 向劳动监察部门投诉举报
2. 申请劳动仲裁
3. 向法院申请支付令
4. 刑事报案（恶意欠薪）

【可主张的权益】
1. 欠付工资本金
2. 加付赔偿金（应付金额50%-100%）
3. 经济补偿金（被迫解除劳动合同）

【举证要点】
1. 劳动关系证明（劳动合同、工作证、工服等）
2. 工资标准证明（劳动合同、工资条、银行流水等）
3. 工资支付记录（银行流水、微信/支付宝转账记录）
4. 工作记录证明出勤情况

【注意事项】
1. 劳动争议仲裁时效为1年
2. 欠薪争议一般适用举证责任倒置
3. 可申请先予执行"""

    def _generate_default_response(self, user_message: str) -> str:
        """生成默认响应"""
        return f"""您好，我是您的法律助手。

您咨询的问题是：{user_message}

我可以为您提供以下法律服务：
1. 劳动合同相关问题的法律分析
2. 违法解除劳动合同的赔偿计算
3. 加班费、年休假等工资计算
4. 工伤认定和赔偿咨询
5. 劳动争议解决建议

请问您具体想咨询什么问题？为了给您提供更准确的法律建议，请尽量提供以下信息：
- 具体发生的时间
- 涉及的金额或期限
- 已有的证据材料
- 您的具体诉求

我会根据您的具体情况，结合相关法律法规和案例，为您提供专业的法律分析。"""
