from neuraverse_sdk.node_base import NodeBase


class FloatMonitorNode(NodeBase):
    """
    Reads Float32 and Float64 inputs and logs their values on each execution.
    """

    def __init__(self):
        super().__init__()

    def on_execute(self) -> None:
        float32_msg = self.get_data("float32_input")
        if float32_msg:
            self.log_info(f"[Float32] {float32_msg.data:.4f}")

        float64_msg = self.get_data("float64_input")
        if float64_msg:
            self.log_info(f"[Float64] {float64_msg.data:.4f}")

    def on_stop(self) -> None:
        self.log_info("Stopping FloatMonitorNode")

    def on_cleanup(self) -> None:
        pass

    def on_configure(self, config, dynamic_config=None) -> None:
        pass

    def on_get_configuration(self):
        return {}

    def on_pause(self) -> None:
        pass

    def on_resume(self) -> None:
        pass
