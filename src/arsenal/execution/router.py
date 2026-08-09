"""Order execution router that dispatches orders to registered adapters."""

from __future__ import annotations

from typing import Dict, Optional

from .adapters.base import BaseExecutionAdapter, ExecutionResult, Order


class OrderRouter:
    """Simple router: adapters are registered by name and used to execute orders.

    If `adapter_name` is omitted, tries to select adapter by symbol prefix
    mapping; otherwise raises KeyError.
    """

    def __init__(self) -> None:
        self.adapters: Dict[str, BaseExecutionAdapter] = {}
        self.symbol_map: Dict[str, str] = {}

    def register_adapter(self, name: str, adapter: BaseExecutionAdapter) -> None:
        self.adapters[name] = adapter

    def map_symbol(self, prefix: str, adapter_name: str) -> None:
        self.symbol_map[prefix.upper()] = adapter_name

    async def route(self, order: Order, adapter_name: Optional[str] = None) -> ExecutionResult:
        name = adapter_name
        if name is None:
            # choose adapter by longest matching prefix
            symbol = order["symbol"].upper()
            matched: Optional[str] = None
            for pfx, adapter in self.symbol_map.items():
                if symbol.startswith(pfx):
                    if matched is None or len(pfx) > len(matched):
                        matched = pfx
            if matched is None:
                raise KeyError("no adapter for symbol and no adapter_name provided")
            name = self.symbol_map[matched]

        adapter = self.adapters.get(name)
        if adapter is None:
            raise KeyError(f"adapter {name!r} not registered")
        return await adapter.execute(order)
