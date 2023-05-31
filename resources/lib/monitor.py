"""
    Kodi video capturer for Hyperion

    Copyright (c) 2013-2016 Hyperion Team

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""
import xbmc

from resources.lib.hyperion.hyperion import Hyperion
from resources.lib.misc import MessageHandler
from resources.lib.settings import Settings


class HyperionMonitor(xbmc.Monitor):
    """Class to capture changes in settings and screensaver state."""

    def __init__(
        self, settings: Settings, player: xbmc.Player, output_handler: MessageHandler
    ) -> None:
        super().__init__()
        self.settings = settings
        self.output_handler = output_handler
        self._screensaver = xbmc.getCondVisibility("System.ScreenSaverActive")
        self._player = player
        self.show_error_message = True
        self._hyperion: Hyperion
        self._capture: xbmc.RenderCapture

    def onSettingsChanged(self) -> None:
        self.settings.read_settings()

    def onScreensaverDeactivated(self) -> None:
        self._screensaver = False

    def onScreensaverActivated(self) -> None:
        self._screensaver = True

    # TODO: onDPMSActivated/Deactivated when entering/exiting energy saving

    @property
    def grabbing(self) -> bool:
        """Checks if grabbing is requested based on the current state and settings."""
        return self.settings.enable and self._player.isPlayingVideo() \
            and (self.settings.enable_screensaver or not self._screensaver)

    def notify_error(self, label_id: int) -> None:
        if self.show_error_message:
            self.output_handler.notify(label_id)
            self.show_error_message = False

    def main_loop(self) -> None:
        state = self.disconnected_state
        while not self.abortRequested():
            state = state()

    def disconnected_state(self):
        if not self.grabbing:
            xbmc.sleep(500)
            return self.disconnected_state
        try:
            self.connect()
            return self.connected_state
        except Exception:
            self.notify_error(32100)
            return self.error_state

    def error_state(self):
        rev = self.settings.rev
        for _ in range(self.settings.timeout):
            if rev != self.settings.rev:
                break
            if self.waitForAbort(1):
                return self.error_state
        return self.disconnected_state

    def connect(self) -> None:
        self.output_handler.log("Establishing connection to hyperion")
        settings = self.settings
        self._hyperion = Hyperion(settings.address, settings.port)
        self._capture = xbmc.RenderCapture()
        self._capture.capture(
            settings.capture_width, settings.capture_height
        )

    def connected_state(self):
        if not self.grabbing:
            return self.disconnected_state

        if data := self._capture.getImage(self.settings.sleep_time):
            # v17+ use BGRA format, converting to RGB
            del data[3::4]
            data[::3], data[2::3] = data[2::3], data[::3]

            try:
                # send image to hyperion
                self._hyperion.send_image(
                    self._capture.getWidth(),
                    self._capture.getHeight(),
                    data,
                    self.settings.priority,
                    500,
                )
            except Exception:
                # unable to send image. notify and go to the error state
                self.output_handler.notify(32101)
                return self.error_state

        return self.connected_state
