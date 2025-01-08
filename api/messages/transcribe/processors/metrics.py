from dataclasses import dataclass
import numpy as np
import math
from typing import Optional

@dataclass
class AudioChunk:
    """Represents a chunk of audio data with its metadata"""
    data: np.ndarray
    sample_rate: int
    chunk_index: int
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AudioChunk':
        """Create an AudioChunk from a dictionary (typically from WebSocket)"""
        return cls(
            data=np.array(data.get("data", []), dtype=np.float32),
            sample_rate=data.get("sampleRate", 44100),
            chunk_index=data.get("chunkIndex", 0)
        )

@dataclass
class AudioMetrics:
    """Holds audio metrics for a chunk of audio data"""
    rms: float
    db: float
    peak_amplitude: Optional[float] = None
    zero_crossings: Optional[int] = None

    @classmethod
    def from_audio_data(cls, audio_data: np.ndarray) -> 'AudioMetrics':
        """Calculate metrics from raw audio data"""
        if len(audio_data) == 0:
            return cls(rms=0.0, db=float('-inf'))
        
        # Calculate RMS (Root Mean Square)
        rms = float(np.sqrt(np.mean(np.square(audio_data))))
        
        # Calculate dB
        db = float('-inf') if rms <= 0 else 20 * math.log10(rms)
        
        # Calculate peak amplitude
        peak_amplitude = float(np.max(np.abs(audio_data)))
        
        # Calculate zero crossings
        zero_crossings = len(np.where(np.diff(np.signbit(audio_data)))[0])
        
        return cls(
            rms=rms,
            db=db,
            peak_amplitude=peak_amplitude,
            zero_crossings=zero_crossings
        )
    
    def to_dict(self) -> dict:
        """Convert metrics to a dictionary for JSON serialization"""
        return {
            "rms": float(self.rms),
            "db": str(float(self.db)),
            "peak_amplitude": float(self.peak_amplitude) if self.peak_amplitude is not None else None,
            "zero_crossings": self.zero_crossings
        }
