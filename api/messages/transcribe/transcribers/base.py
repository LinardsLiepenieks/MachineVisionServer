from abc import ABC, abstractmethod
import numpy as np
from typing import Optional


class BaseTranscriber(ABC):
    """Abstract base class for audio transcription implementations."""

    pre_emphasis: float = 0.9

    @abstractmethod
    def process_chunk(self, audio_data: np.ndarray, sample_rate: int) -> Optional[str]:
        """
        Process an audio chunk and return transcribed text if ready.

        Args:
            audio_data (np.ndarray): Array of audio samples
            sample_rate (int): Sample rate of the audio

        Returns:
            Optional[str]: Transcribed text if available, None otherwise
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the transcriber's internal state."""
        pass

    def apply_pre_emphasis(self, audio: np.ndarray) -> np.ndarray:
        """Apply pre-emphasis filter using the difference equation:
        y[n] = x[n] - α * x[n-1]
        where α is the pre-emphasis coefficient (typically 0.95-0.97)"""
        if len(audio) < 2:
            return audio

        return np.append(audio[0], audio[1:] - self.pre_emphasis * audio[:-1])
