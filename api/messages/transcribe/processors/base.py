from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import numpy as np
from .metrics import AudioMetrics, AudioChunk
from ..transcribers.base import BaseTranscriber

class AudioProcessor:
    """
    Base class for audio processing operations.
    Handles both metrics calculation and transcription.
    """
    def __init__(self, transcriber: BaseTranscriber):

        self.transcriber = transcriber
        self._reset_state()

    def _reset_state(self):
        """Reset internal state of the processor"""
        self.last_metrics: Optional[AudioMetrics] = None
        self.cumulative_rms = 0
        self.processed_chunks = 0

    def process_chunk(self, chunk: AudioChunk) -> Tuple[AudioMetrics, Optional[str]]:
        """
        Process a single chunk of audio data.
        Returns metrics and any transcription result.
        """
        # Calculate metrics
        metrics = AudioMetrics.from_audio_data(chunk.data)
        
        # Update running statistics
        self.processed_chunks += 1
        self.cumulative_rms += metrics.rms
        self.last_metrics = metrics

        # Process transcription
        transcription = self.transcriber.process_chunk(
            chunk.data, 
            chunk.sample_rate
        )

        return metrics, transcription

    def get_average_metrics(self) -> Dict[str, float]:
        """Get average metrics across all processed chunks"""
        if self.processed_chunks == 0:
            return {
                "average_rms": 0.0,
                "average_db": float("-inf")
            }

        avg_rms = self.cumulative_rms / self.processed_chunks
        avg_db = -float("inf") if avg_rms <= 0 else 20 * np.log10(avg_rms)

        return {
            "average_rms": float(avg_rms),
            "average_db": float(avg_db)
        }
