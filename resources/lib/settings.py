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
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import xbmcaddon


class Settings:
    """Class which contains all addon settings."""

    def __init__(self, settings: xbmcaddon.Settings) -> None:
        self.rev = 0
        self._settings = settings
        self.read_settings()

    def read_settings(self) -> None:
        """Read all settings"""
        settings = self._settings
        self.enable = settings.getBool("hyperion_enable")
        self.enable_screensaver = settings.getBool("screensaver_enable")
        self.address = settings.getString("hyperion_ip")
        self.port = settings.getInt("hyperion_port")
        self.priority = settings.getInt("hyperion_priority")
        self.timeout = settings.getInt("reconnect_timeout")
        self.capture_width = settings.getInt("capture_width")
        self.capture_height = settings.getInt("capture_height")
        self.framerate = settings.getInt("framerate")
        self.sleep_time = int(1.0 / self.framerate * 1000)
        self.rev += 1
