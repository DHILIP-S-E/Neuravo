"""Tests for common decorators."""

import pytest

from neuravo.core.exceptions import NeurevoError, ValidationError
from neuravo.utils.decorators import handle_errors, log_execution


@pytest.mark.asyncio
async def test_log_execution_wraps_async_function():
    @log_execution
    async def add(a: int, b: int) -> int:
        return a + b

    assert await add(2, 3) == 5


def test_log_execution_wraps_sync_function():
    @log_execution
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5


@pytest.mark.asyncio
async def test_handle_errors_passes_through_result():
    @handle_errors
    async def ok() -> str:
        return "fine"

    assert await ok() == "fine"


@pytest.mark.asyncio
async def test_handle_errors_reraises_neuravo_errors_unchanged():
    @handle_errors
    async def fails() -> None:
        raise ValidationError("bad input")

    with pytest.raises(ValidationError):
        await fails()


@pytest.mark.asyncio
async def test_handle_errors_wraps_unexpected_exceptions():
    @handle_errors
    async def fails() -> None:
        raise ValueError("boom")

    with pytest.raises(NeurevoError) as exc_info:
        await fails()

    assert "boom" in str(exc_info.value)
