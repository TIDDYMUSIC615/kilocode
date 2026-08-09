"""Internal implementations for `arsenal.connection`.

Keep implementation details in this module. Public API should live in
`arsenal.connection.__init__` as thin wrappers.
"""

from typing import Any


async def open_connection(addr: str) -> Any:
    """Placeholder async connection opener.

    Replace with transport-specific implementation.
    """
    return None
