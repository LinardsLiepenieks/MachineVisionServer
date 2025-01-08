from typing import Optional
import numpy as np
import torch
from .base import BaseTranscriber


class SileroTranscriber(BaseTranscriber):
    def __init__(
        self, language: str = "en", device: str = "cpu", buffer_size: float = 1
    ):
        self.device = torch.device(device)
        self.language = language
        self.sample_rate = 16000
        self.buffer_size = int(
            buffer_size * self.sample_rate
        )  # Configurable buffer size
        self.audio_buffer = []

        self.load_model()

    def load_model(self):
        self.model, self.decoder, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_stt",
            language=self.language,
            device=self.device,
        )
        _, _, _, self.prepare_model_input = utils
        self.model.eval()

    @torch.no_grad()
    def process_chunk(self, audio_data: np.ndarray, sample_rate: int) -> Optional[str]:
        # Check if audio_data is empty
        if audio_data.size == 0:
            return None

        if len(audio_data.shape) == 2:
            audio_data = audio_data.mean(axis=1)

        audio_data = self.apply_pre_emphasis(audio_data)
        self.audio_buffer.extend(audio_data.tolist())

        if len(self.audio_buffer) >= self.buffer_size:
            try:
                # Process without batching
                audio_tensor = torch.tensor(
                    self.audio_buffer, device=self.device
                ).unsqueeze(0)
                input_tensor = self.prepare_model_input(
                    audio_tensor, device=self.device
                )

                output = self.model(input_tensor)
                transcription = self.decoder(output[0])

                # Keep last 0.5 seconds for context
                overlap = int(0.5 * self.sample_rate)
                self.audio_buffer = self.audio_buffer[-overlap:] if overlap > 0 else []

                return transcription

            except Exception as e:
                print(f"Error during transcription: {str(e)}")
                self.audio_buffer = []

        return None

    def reset(self) -> None:
        self.audio_buffer = []
