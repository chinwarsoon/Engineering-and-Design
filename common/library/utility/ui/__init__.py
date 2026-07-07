"""
common.library.utility.ui — UI contract base classes.

Exports
-------
UIRequest           L14  Standardized UI request dataclass with from_json()
UIResponse          L14  Standardized UI response dataclass with to_json()
UIContractManager   L14  Manager: validate_selection(), run_pipeline(), run_from_ui_request()

Sources
-------
dcc: core_engine/ui/ui_contract.py  (UIRequest, UIResponse, UIContractManager — reference impl)
eks: ui/backend/phase1_server.py    (inline Flask handlers — no formal contracts, gap)
"""

from common.library.utility.ui.contracts import UIRequest, UIResponse, UIContractManager

__all__ = ["UIRequest", "UIResponse", "UIContractManager"]
