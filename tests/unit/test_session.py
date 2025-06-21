import types
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.adapters.orm.session import get_session


@pytest.mark.asyncio
async def test_get_session_yields_asyncsession() -> None:
    """
    GIVEN a patched async engine and session
    WHEN get_session is called and the generator is iterated
    THEN it should yield an AsyncSession instance
    """
    fake_engine = MagicMock()
    with patch("app.adapters.orm.session.get_async_engine", return_value=fake_engine):
        session_gen = get_session()
        assert callable(session_gen)
        # The returned function should be an async generator
        agen = session_gen()
        assert isinstance(agen, types.AsyncGeneratorType)
        # Patch AsyncSession to avoid real DB
        with patch("app.adapters.orm.session.AsyncSession", autospec=True) as mock_session:
            mock_session.return_value.__aenter__.return_value = MagicMock(spec=AsyncSession)
            async for sess in agen:
                assert isinstance(sess, AsyncSession)
                break
