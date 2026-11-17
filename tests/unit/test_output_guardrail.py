
import pytest

from policy_assistant.application.services.output_guardrail import (
    OutputGuardrail,
)


def test_normal_answer_passes():
    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Employees receive 20 annual leaves."
    )

    assert result.is_safe is True
    assert result.reason is None


def test_gemini_api_key_is_blocked():
    guardrail = OutputGuardrail()
    answer = "The API key is AIza" + "A" * 35

    result = guardrail.validate(answer)

    assert result.is_safe is False
    assert "secret" in result.reason.lower()


def test_password_is_blocked():
    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Employee credentials: password=secret123"
    )

    assert result.is_safe is False


def test_bearer_token_is_blocked():
    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123"
    )

    assert result.is_safe is False


def test_unapproved_email_is_blocked():
    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Contact employee@example.com for details."
    )

    assert result.is_safe is False
    assert "email" in result.reason.lower()


def test_approved_email_is_allowed():
    guardrail = OutputGuardrail(
        allowed_emails={"hr@company.com"}
    )

    result = guardrail.validate(
        "Contact HR at HR@Company.com."
    )

    assert result.is_safe is True


def test_indian_phone_number_is_blocked():
    guardrail = OutputGuardrail()

    result = guardrail.validate(
        "Contact the employee at +91 9876543210."
    )

    assert result.is_safe is False
    assert "phone" in result.reason.lower()


@pytest.mark.parametrize("answer", ["", "   ", "\n"])
def test_empty_answer_is_blocked(answer):
    guardrail = OutputGuardrail()

    result = guardrail.validate(answer)

    assert result.is_safe is False
