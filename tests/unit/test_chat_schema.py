
import pytest
from pydantic import ValidationError

from policy_assistant.api.schemas.chat import ChatQueryRequest


def test_valid_question_is_accepted():
    request = ChatQueryRequest(
        question="How many annual leaves do employees receive?"
    )

    assert request.question == (
        "How many annual leaves do employees receive?"
    )


def test_empty_question_is_rejected():
    with pytest.raises(ValidationError):
        ChatQueryRequest(question="")


def test_whitespace_only_question_is_rejected():
    with pytest.raises(ValidationError):
        ChatQueryRequest(question="     ")


def test_question_exceeding_2000_characters_is_rejected():
    with pytest.raises(ValidationError):
        ChatQueryRequest(question="A" * 2001)


def test_question_is_trimmed():
    request = ChatQueryRequest(
        question="  How many annual leaves?  "
    )

    assert request.question == "How many annual leaves?"
