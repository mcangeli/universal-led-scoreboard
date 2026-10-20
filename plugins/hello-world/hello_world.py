"""Minimal native ULS screen example. No network, hardware, or external dependencies."""

from universal_led.display import Framebuffer


class HelloWorldScreen:
    """Render a predictable 64x32 frame for previews and integration tests."""

    name = "hello-world"

    def render(self) -> Framebuffer:
        frame = Framebuffer(64, 32)
        frame.text("HELLO", 17, 7, (239, 195, 95))
        frame.text("WORLD", 17, 18, (235, 235, 225))
        return frame
