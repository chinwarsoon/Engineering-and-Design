"""
EKS Message Manager - thin subclass of common BaseMessageManager.
"""
from ..logging.logger import EKSLogger, log_depth
from common.library.core.messages.message_manager import BaseMessageManager


class MessageManager(BaseMessageManager):
    _catalog_filename = "eks_message_config.json"

    def __init__(self, config_dir=None, logger=None, verbosity=1):
        if logger is None:
            logger = EKSLogger("MessageManager", level=1)
        super().__init__(config_dir=config_dir, logger=logger, verbosity=verbosity)

    @log_depth
    def show(self, msg_id: str, **kwargs) -> None:
        super().show(msg_id, **kwargs)

    @log_depth
    def load_catalog(self) -> None:
        self.reload_catalog()
        total = len(self._messages_dict())
        self._logger.status(f"Loaded message catalog: {total} messages")
