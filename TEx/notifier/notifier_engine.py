"""Notifier Modules."""
from __future__ import annotations

from configparser import ConfigParser
from typing import Dict, List

from telethon.events import NewMessage

from TEx.notifier.discord_notifier import DiscordNotifier
from TEx.notifier.elastic_search_notifier import ElasticSearchNotifier
from TEx.notifier.notifier_base import BaseNotifier


class NotifierEngine:
    """Primary Notification Engine."""

    def __init__(self) -> None:
        """Initialize Finder Engine."""
        self.notifiers: Dict = {}

    def __load_notifiers(self, config: ConfigParser) -> None:
        """Load all Registered Notifiers."""
        registered_notifiers: List[str] = [item for item in config.sections() if 'NOTIFIER.' in item]

        for register in registered_notifiers:
            if 'DISCORD' in register:

                notifier: DiscordNotifier = DiscordNotifier()
                notifier.configure(url=config[register]['webhook'], config=config[register])

                self.notifiers.update({
                    register: {'instance': notifier},
                    })

            if 'ELASTIC_SEARCH' in register:
                notifier_es: ElasticSearchNotifier = ElasticSearchNotifier()
                notifier_es.configure(config=config[register])

                self.notifiers.update({
                    register: {'instance': notifier_es},
                    })

    def configure(self, config: ConfigParser) -> None:
        """Configure Finder."""
        self.__load_notifiers(config)

    async def run(self, notifiers: List[str], message: NewMessage.Event, rule_id: str, source: str) -> None:
        """Dispatch all Notifications.

        :param notifiers:
        :param message: Message Object
        :param rule_id: Triggered Rule ID
        :param source: Source Account/Phone Number
        :return:
        """
        if len(notifiers) == 0:
            return

        for dispatcher_name in notifiers:

            target_notifier: BaseNotifier = self.notifiers[dispatcher_name]['instance']
            await target_notifier.run(message=message, rule_id=rule_id, source=source)
