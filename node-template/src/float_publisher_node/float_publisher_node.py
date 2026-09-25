import io
import random

import numpy as np
from PIL import Image as PilImage
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Float32, Float64

from neuraverse_sdk.node_base import NodeBase


class FloatPublisherNode(NodeBase):
    """
    Publishes random Float32 and Float64 values between 0 and 10 on each execution.
    """

    def __init__(self):
        super().__init__()

    def on_execute(self) -> None:
        float32_msg = Float32(data=random.uniform(0.0, 10.0))
        float64_msg = Float64(data=random.uniform(0.0, 10.0))
        large_float_msg = Float64(data=random.uniform(1e6, 1e9))

        self.log_info(f"Publishing Float32: {float32_msg.data:.4f}")
        self.publish("float32_output", float32_msg)

        self.log_info(f"Publishing Float64: {float64_msg.data:.4f}")
        self.publish("float64_output", float64_msg)

        self.log_info(f"Publishing large Float64: {large_float_msg.data:.4f}")
        self.publish("large_float_output", large_float_msg)

        image_msg = self._make_random_image()
        self.log_info("Publishing random image")
        self.publish("image_output", image_msg)

    def _make_random_image(self) -> CompressedImage:
        pixels = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        pil_img = PilImage.fromarray(pixels, mode="RGB")
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG")
        msg = CompressedImage()
        msg.format = "jpeg"
        msg.data = list(buf.getvalue())
        return msg

    def on_stop(self) -> None:
        self.log_info("Stopping FloatPublisherNode")

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
