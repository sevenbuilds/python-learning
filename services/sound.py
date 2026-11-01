import math
import os
import struct
import tempfile
import wave

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

_effect = None


def _make_wav(path):
    rate = 44100
    notes = [(880.00, 0.18), (1174.66, 0.40)]          # A5 then D6
    frames = bytearray()
    for freq, duration in notes:
        for i in range(int(rate * duration)):
            t = i / rate
            fade = math.exp(-5 * t / duration) * min(1, i / 200)
            frames += struct.pack("<h", int(math.sin(2 * math.pi * freq * t) * fade * 0.6 * 32767))
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(bytes(frames))


def play_reminder_sound():
    global _effect
    if _effect is None:
        path = os.path.join(tempfile.gettempdir(), "dayos_reminder.wav")
        if not os.path.exists(path):
            _make_wav(path)
        _effect = QSoundEffect()
        _effect.setSource(QUrl.fromLocalFile(path))
        _effect.setVolume(0.8)
    _effect.play()