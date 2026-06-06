from app.chat.context import CRISIS_REPLY, build_db_context, is_crisis_message


def test_crisis_detection():
    assert is_crisis_message("I have severe chest pain")
    assert is_crisis_message("I want to kill myself")
    assert not is_crisis_message("What is a common cold?")


def test_crisis_reply_nonempty():
    assert "emergency" in CRISIS_REPLY.lower()


def test_build_db_context_empty_without_terms(db_session):
    ctx = build_db_context(db_session, "hi")
    assert ctx == ""
