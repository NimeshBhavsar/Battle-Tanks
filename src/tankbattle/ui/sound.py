"""Short synthesized sound effects (no external audio files needed).

Each sound is a decaying sine tone built as raw 16-bit PCM samples. If the
platform has no audio device, loading/playing silently no-ops rather than
crashing the client.
"""

import array
import math

import pygame

_SAMPLE_RATE = 22050


def _make_tone(frequency: float, duration: float, volume: float = 0.5) -> pygame.mixer.Sound:
    n_samples = int(_SAMPLE_RATE * duration)
    samples = array.array("h", [0] * n_samples * 2)  # interleaved stereo, 16-bit signed
    amplitude = int(volume * 32767)
    for i in range(n_samples):
        t = i / _SAMPLE_RATE
        envelope = 1.0 - (i / n_samples)  # linear decay, avoids a harsh click at the end
        value = int(amplitude * envelope * math.sin(2 * math.pi * frequency * t))
        samples[2 * i] = value
        samples[2 * i + 1] = value
    return pygame.mixer.Sound(buffer=samples)


def load_sounds() -> dict[str, pygame.mixer.Sound]:
    try:
        pygame.mixer.init(frequency=_SAMPLE_RATE, size=-16, channels=2)
        return {
            "fire": _make_tone(880.0, 0.12, volume=0.4),
            "explosion": _make_tone(120.0, 0.35, volume=0.6),
        }
    except pygame.error:
        return {}


def play(sounds: dict[str, pygame.mixer.Sound], name: str) -> None:
    sound = sounds.get(name)
    if sound is None:
        return
    try:
        sound.play()
    except pygame.error:
        pass
