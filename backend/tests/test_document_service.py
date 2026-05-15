import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.services import document_service
from app.services.document_service import (
    SEED_TEMPLATES,
    seed_templates,
    list_templates,
    get_template,
    list_documents,
    get_document,
    create_document,
    update_document,
    create_version,
)
from app.models.document import Document, DocumentTemplate


# ── SEED_TEMPLATES constant tests ──


def test_seed_templates_count():
    """Should contain exactly 10 seed templates."""
    assert len(SEED_TEMPLATES) == 10


def test_seed_templates_have_required_fields():
    """Each seed template must include name, doc_type, content_template,
    variables_schema, category, and sort_order."""
    for tmpl in SEED_TEMPLATES:
        assert "name" in tmpl
        assert "doc_type" in tmpl
        assert "content_template" in tmpl
        assert "variables_schema" in tmpl
        assert "category" in tmpl
        assert "sort_order" in tmpl


def test_seed_templates_have_variable_placeholders():
    """Every content_template must contain at least one {{variable}} placeholder."""
    for tmpl in SEED_TEMPLATES:
        assert "{{" in tmpl["content_template"], f"Template '{tmpl['name']}' has no placeholders"


def test_seed_templates_sort_orders_are_unique():
    """Sort orders should be unique to avoid ambiguity."""
    orders = [t["sort_order"] for t in SEED_TEMPLATES]
    assert len(orders) == len(set(orders))


def test_seed_templates_categories():
    """Templates cover expected categories."""
    categories = {t["category"] for t in SEED_TEMPLATES}
    assert "申请类" in categories
    assert "起诉类" in categories
    assert "协议类" in categories


# ── seed_templates() service tests ──


@pytest.mark.asyncio
async def test_seed_templates_inserts_when_none_exist():
    """Should add all 10 templates when no system templates exist."""
    mock_db = AsyncMock()

    # First call: count query returns 0
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    mock_db.execute.return_value = count_result

    await seed_templates(mock_db)

    # db.add should have been called 10 times (once per template)
    assert mock_db.add.call_count == 10
    mock_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_seed_templates_skips_when_already_present():
    """Should not insert anything if system templates already exist."""
    mock_db = AsyncMock()

    count_result = MagicMock()
    count_result.scalar.return_value = 5  # already have templates
    mock_db.execute.return_value = count_result

    await seed_templates(mock_db)

    mock_db.add.assert_not_called()
    mock_db.flush.assert_not_awaited()


# ── list_templates() tests ──


@pytest.mark.asyncio
async def test_list_templates_returns_list():
    """Should return a list of templates."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await list_templates(mock_db)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_templates_filters_by_category():
    """When category is provided, the query should still execute successfully."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await list_templates(mock_db, category="申请类")
    assert isinstance(result, list)
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_templates_with_tenant_id():
    """When tenant_id is provided, templates for that tenant + system are returned."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    tid = uuid.uuid4()
    result = await list_templates(mock_db, tenant_id=tid)
    assert isinstance(result, list)


# ── get_template() tests ──


@pytest.mark.asyncio
async def test_get_template_returns_template():
    """Should return the template when found."""
    mock_db = AsyncMock()
    fake_template = MagicMock(spec=DocumentTemplate)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_template
    mock_db.execute.return_value = mock_result

    result = await get_template(mock_db, uuid.uuid4())
    assert result is fake_template


@pytest.mark.asyncio
async def test_get_template_returns_none_when_not_found():
    """Should return None when template does not exist."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await get_template(mock_db, uuid.uuid4())
    assert result is None


# ── list_documents() tests ──


@pytest.mark.asyncio
async def test_list_documents_returns_tuple():
    """Should return (items, total) tuple."""
    mock_db = AsyncMock()

    # First call: count query
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    # Second call: data query
    data_result = MagicMock()
    data_result.scalars.return_value.all.return_value = []

    mock_db.execute.side_effect = [count_result, data_result]

    items, total = await list_documents(mock_db, tenant_id=uuid.uuid4())
    assert isinstance(items, list)
    assert total == 0


@pytest.mark.asyncio
async def test_list_documents_with_case_id_filter():
    """Should apply case_id filter and return results."""
    mock_db = AsyncMock()
    tenant_id = uuid.uuid4()
    case_id = uuid.uuid4()

    count_result = MagicMock()
    count_result.scalar.return_value = 1

    fake_doc = MagicMock(spec=Document)
    data_result = MagicMock()
    data_result.scalars.return_value.all.return_value = [fake_doc]

    mock_db.execute.side_effect = [count_result, data_result]

    items, total = await list_documents(mock_db, tenant_id=tenant_id, case_id=case_id)
    assert len(items) == 1
    assert total == 1


@pytest.mark.asyncio
async def test_list_documents_with_status_filter():
    """Should apply status filter."""
    mock_db = AsyncMock()
    tenant_id = uuid.uuid4()

    count_result = MagicMock()
    count_result.scalar.return_value = 2

    data_result = MagicMock()
    data_result.scalars.return_value.all.return_value = [MagicMock(spec=Document), MagicMock(spec=Document)]

    mock_db.execute.side_effect = [count_result, data_result]

    items, total = await list_documents(mock_db, tenant_id=tenant_id, status="draft")
    assert total == 2
    assert len(items) == 2


# ── get_document() tests ──


@pytest.mark.asyncio
async def test_get_document_returns_document():
    """Should return the document when found."""
    mock_db = AsyncMock()
    fake_doc = MagicMock(spec=Document)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_doc
    mock_db.execute.return_value = mock_result

    result = await get_document(mock_db, uuid.uuid4())
    assert result is fake_doc


@pytest.mark.asyncio
async def test_get_document_returns_none_when_not_found():
    """Should return None when document does not exist."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await get_document(mock_db, uuid.uuid4())
    assert result is None


# ── create_document() tests ──


@pytest.mark.asyncio
async def test_create_document_sets_fields():
    """Should create a document with the provided fields."""
    mock_db = AsyncMock()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    data = {
        "title": "测试文书",
        "doc_type": "complaint",
    }
    content = {"body": "hello"}

    doc = await create_document(mock_db, tenant_id=tenant_id, user_id=user_id, data=data, content=content)
    mock_db.add.assert_called_once()
    mock_db.flush.assert_awaited_once()

    # Inspect the object that was added
    added_doc = mock_db.add.call_args[0][0]
    assert added_doc.title == "测试文书"
    assert added_doc.doc_type == "complaint"
    assert added_doc.tenant_id == tenant_id
    assert added_doc.user_id == user_id
    assert added_doc.content == content


@pytest.mark.asyncio
async def test_create_document_without_optional_fields():
    """Should create document without content or template_id."""
    mock_db = AsyncMock()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    data = {"title": "空白文书", "doc_type": "defense_letter"}

    doc = await create_document(mock_db, tenant_id=tenant_id, user_id=user_id, data=data)
    added_doc = mock_db.add.call_args[0][0]
    assert added_doc.content is None


# ── update_document() tests ──


@pytest.mark.asyncio
async def test_update_document_sets_non_none_fields():
    """Should update only fields with non-None values."""
    mock_db = AsyncMock()
    doc = MagicMock(spec=Document)

    await update_document(mock_db, doc, {"title": "新标题", "status": "published"})
    assert doc.title == "新标题"
    assert doc.status == "published"
    mock_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_document_skips_none_fields():
    """Should not set attributes when the value is None."""
    mock_db = AsyncMock()
    # Use a simple object instead of MagicMock(spec=Document) so setattr is trackable
    doc = MagicMock()
    doc.title = "original"
    doc.status = "draft"

    await update_document(mock_db, doc, {"title": None, "status": "published"})
    # title should remain unchanged (value was None), status should be updated
    assert doc.title == "original"
    assert doc.status == "published"
    mock_db.flush.assert_awaited_once()


# ── create_version() tests ──


@pytest.mark.asyncio
async def test_create_version_increments_version():
    """New version should have version = old version + 1."""
    mock_db = AsyncMock()

    original_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    original = MagicMock(spec=Document)
    original.id = original_id
    original.tenant_id = tenant_id
    original.user_id = user_id
    original.title = "仲裁申请书"
    original.doc_type = "arbitration_application"
    original.template_id = None
    original.content = {"body": "original content"}
    original.variables = {"applicant_name": "张三"}
    original.version = 3
    original.case_id = None

    new_doc = await create_version(mock_db, original)

    added_doc = mock_db.add.call_args[0][0]
    assert added_doc.version == 4
    assert added_doc.parent_id == original_id
    assert added_doc.status == "draft"
    assert added_doc.title == "仲裁申请书"
    assert added_doc.doc_type == "arbitration_application"
    assert added_doc.content == {"body": "original content"}
    assert added_doc.variables == {"applicant_name": "张三"}


@pytest.mark.asyncio
async def test_create_version_copies_all_fields():
    """New version should copy tenant_id, user_id, template_id, case_id, content, variables."""
    mock_db = AsyncMock()

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    template_id = uuid.uuid4()
    case_id = uuid.uuid4()
    original_id = uuid.uuid4()

    original = MagicMock(spec=Document)
    original.id = original_id
    original.tenant_id = tenant_id
    original.user_id = user_id
    original.title = "起诉状"
    original.doc_type = "complaint"
    original.template_id = template_id
    original.content = {"section": "facts"}
    original.variables = {"plaintiff": "李四"}
    original.version = 1
    original.case_id = case_id

    await create_version(mock_db, original)

    added = mock_db.add.call_args[0][0]
    assert added.tenant_id == tenant_id
    assert added.user_id == user_id
    assert added.template_id == template_id
    assert added.case_id == case_id
    assert added.content == {"section": "facts"}
    assert added.variables == {"plaintiff": "李四"}
