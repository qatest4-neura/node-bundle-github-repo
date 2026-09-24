"""No-op trigger adapter for testing nodes without MQTT trigger infrastructure."""

from typing import Any, Callable

from neuraverse.models.v1.gen.business.node_graph_pb2 import TriggerNodeEntry
from neuraverse_sdk.trigger.i_trigger import ITrigger, TriggerType


class MockTrigger(ITrigger):
    """
    No-op ITrigger implementation that records trigger_next_node calls
    for inspection. Does not connect to any external system.
    """

    def __init__(self):
        super().__init__()
        self.triggered: list[TriggerType] = []

    def init(self, configuration: Any) -> None:
        pass

    def configure(self, trigger_node_entry: TriggerNodeEntry) -> None:
        # Store outgoing trigger mappings for inspection
        for trigger_name, topic in trigger_node_entry.outputTriggers.items():
            try:
                trigger_type = TriggerType(trigger_name)
                self._outgoing_triggers[trigger_type] = topic
            except ValueError:
                pass

    def trigger_next_node(self, type: TriggerType) -> None:
        self.triggered.append(type)

    def destroy(self) -> None:
        self.triggered.clear()

    def get_triggered(self) -> list[str]:
        """Return list of trigger type names that were fired."""
        return [t.value for t in self.triggered]
