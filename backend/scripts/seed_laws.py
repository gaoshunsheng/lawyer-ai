"""种子脚本：导入核心劳动法律法规"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.config import settings
from app.models import Law, LawArticle, Tenant

LAWS = [
    {
        "title": "中华人民共和国劳动合同法",
        "law_type": "law",
        "promulgating_body": "全国人民代表大会常务委员会",
        "articles": [
            {"number": "第十条", "content": "建立劳动关系，应当订立书面劳动合同。已建立劳动关系，未同时订立书面劳动合同的，应当自用工之日起一个月内订立书面劳动合同。"},
            {"number": "第十四条", "content": "无固定期限劳动合同，是指用人单位与劳动者约定无确定终止时间的劳动合同。用人单位与劳动者协商一致，可以订立无固定期限劳动合同。"},
            {"number": "第三十六条", "content": "用人单位与劳动者协商一致，可以解除劳动合同。"},
            {"number": "第三十九条", "content": "劳动者有下列情形之一的，用人单位可以解除劳动合同：（一）在试用期间被证明不符合录用条件的；（二）严重违反用人单位的规章制度的；（三）严重失职，营私舞弊，给用人单位造成重大损害的。"},
            {"number": "第四十条", "content": "有下列情形之一的，用人单位提前三十日以书面形式通知劳动者本人或者额外支付劳动者一个月工资后，可以解除劳动合同：（一）劳动者患病或者非因工负伤，在规定的医疗期满后不能从事原工作，也不能从事由用人单位另行安排的工作的；（二）劳动者不能胜任工作，经过培训或者调整工作岗位，仍不能胜任工作的。"},
            {"number": "第四十六条", "content": "有下列情形之一的，用人单位应当向劳动者支付经济补偿：（一）劳动者依照本法第三十八条规定解除劳动合同的；（二）用人单位依照本法第三十六条规定向劳动者提出解除劳动合同并与劳动者协商一致解除劳动合同的；（三）用人单位依照本法第四十条规定解除劳动合同的；（四）用人单位依照本法第四十一条第一款规定解除劳动合同的。"},
            {"number": "第四十七条", "content": "经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。六个月以上不满一年的，按一年计算；不满六个月的，向劳动者支付半个月工资的经济补偿。劳动者月工资高于用人单位所在直辖市、设区的市级人民政府公布的本地区上年度职工月平均工资三倍的，按职工月平均工资三倍的数额支付，向其支付经济补偿的年限最高不超过十二年。"},
            {"number": "第四十八条", "content": "用人单位违反本法规定解除或者终止劳动合同，劳动者要求继续履行劳动合同的，用人单位应当继续履行；劳动者不要求继续履行劳动合同或者劳动合同已经不能继续履行的，用人单位应当依照本法第八十七条规定支付赔偿金。"},
            {"number": "第八十七条", "content": "用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第四十七条规定的经济补偿标准的二倍向劳动者支付赔偿金。"},
            {"number": "第八十二条", "content": "用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，应当向劳动者每月支付二倍的工资。"},
        ],
    },
    {
        "title": "中华人民共和国劳动法",
        "law_type": "law",
        "promulgating_body": "全国人民代表大会",
        "articles": [
            {"number": "第三十六条", "content": "国家实行劳动者每日工作时间不超过八小时、平均每周工作时间不超过四十四小时的工时制度。"},
            {"number": "第三十八条", "content": "用人单位应当保证劳动者每周至少休息一日。"},
            {"number": "第四十一条", "content": "用人单位由于生产经营需要，经与工会和劳动者协商后可以延长工作时间，一般每日不得超过一小时；因特殊原因需要延长工作时间的，在保障劳动者身体健康的条件下延长工作时间每日不得超过三小时，但是每月不得超过三十六小时。"},
            {"number": "第四十四条", "content": "有下列情形之一的，用人单位应当按照下列标准支付高于劳动者正常工作时间工资的工资报酬：（一）安排劳动者延长工作时间的，支付不低于工资的百分之一百五十的工资报酬；（二）休息日安排劳动者工作又不能安排补休的，支付不低于工资的百分之二百的工资报酬；（三）法定休假日安排劳动者工作的，支付不低于工资的百分之三百的工资报酬。"},
            {"number": "第四十五条", "content": "国家实行带薪年休假制度。劳动者连续工作一年以上的，享受带薪年休假。具体办法由国务院规定。"},
        ],
    },
    {
        "title": "职工带薪年休假条例",
        "law_type": "regulation",
        "promulgating_body": "国务院",
        "articles": [
            {"number": "第二条", "content": "机关、团体、企业、事业单位、民办非企业单位、有雇工的个体工商户等单位的职工连续工作1年以上的，享受带薪年休假。单位应当保证职工享受年休假。"},
            {"number": "第三条", "content": "职工累计工作已满1年不满10年的，年休假5天；已满10年不满20年的，年休假10天；已满20年的，年休假15天。国家法定休假日、休息日不计入年休假的假期。"},
            {"number": "第五条", "content": "单位确因工作需要不能安排职工休年休假的，经职工本人同意，可以不安排职工休年休假。对职工应休未休的年休假天数，单位应当按照该职工日工资收入的300%支付年休假工资报酬。"},
        ],
    },
    {
        "title": "工伤保险条例",
        "law_type": "regulation",
        "promulgating_body": "国务院",
        "articles": [
            {"number": "第十四条", "content": "职工有下列情形之一的，应当认定为工伤：（一）在工作时间和工作场所内，因工作原因受到事故伤害的；（二）工作时间前后在工作场所内，从事与工作有关的预备性或者收尾性工作受到事故伤害的；（三）在工作时间和工作场所内，因履行工作职责受到暴力等意外伤害的。"},
            {"number": "第三十条", "content": "职工因工作遭受事故伤害或者患职业病进行治疗，享受工伤医疗待遇。职工治疗工伤应当在签订服务协议的医疗机构就医，情况紧急时可以先到就近医疗机构急救。"},
            {"number": "第三十五条", "content": "职工因工致残被鉴定为一级至四级伤残的，保留劳动关系，退出工作岗位，享受以下待遇：（一）从工伤保险基金按伤残等级支付一次性伤残补助金，标准为：一级伤残为27个月的本人工资，二级伤残为25个月的本人工资，三级伤残为23个月的本人工资，四级伤残为21个月的本人工资。"},
            {"number": "第三十七条", "content": "职工因工致残被鉴定为七级至十级伤残的，享受以下待遇：（一）从工伤保险基金按伤残等级支付一次性伤残补助金，标准为：七级伤残为13个月的本人工资，八级伤残为11个月的本人工资，九级伤残为9个月的本人工资，十级伤残为7个月的本人工资。"},
        ],
    },
]


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Law).limit(1))
        if result.scalar_one_or_none():
            print("法律法规已存在，跳过种子")
            await engine.dispose()
            return

        for law_data in LAWS:
            law = Law(
                title=law_data["title"],
                law_type=law_data["law_type"],
                promulgating_body=law_data.get("promulgating_body"),
                full_text="\n".join(a["content"] for a in law_data["articles"]),
                status="effective",
            )
            db.add(law)
            await db.flush()

            for art in law_data["articles"]:
                article = LawArticle(
                    law_id=law.id,
                    article_number=art["number"],
                    content=art["content"],
                )
                db.add(article)

            print(f"  导入: {law_data['title']} ({len(law_data['articles'])}条)")

        await db.commit()
        print("种子数据导入完成！")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
