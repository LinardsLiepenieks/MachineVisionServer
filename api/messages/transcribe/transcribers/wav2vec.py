from typing import Optional
import numpy as np
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from .base import BaseTranscriber

class Wav2VecTranscriber(BaseTranscriber):
    """Wav2Vec 2.0 based speech recognition implementation."""
    
    def __init__(self, model_name: str = "facebook/wav2vec2-base-960h", device: str = 'cpu'):
        """
        Initialize Wav2Vec transcriber.
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to run model on ('cpu' or 'cuda')
        """
        self.device = torch.device(device)
        self.sample_rate = 16000  # Wav2Vec expects 16kHz
        self.audio_buffer = []
        
        self.load_model(model_name)
        
    def load_model(self, model_name: str):
        """Load the Wav2Vec model and processor."""
        try:
            self.processor = Wav2Vec2Processor.from_pretrained(model_name)
            self.model = Wav2Vec2ForCTC.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            print(f"Successfully loaded Wav2Vec model: {model_name}")
            
        except Exception as e:
            print(f"Error loading Wav2Vec model: {str(e)}")
            raise
    
    def process_chunk(self, audio_data: np.ndarray, sample_rate: int) -> Optional[str]:
        """
        Process an audio chunk and return transcribed text if available.
        
        Args:
            audio_data: Audio chunk data
            sample_rate: Sample rate of the audio
            
        Returns:
            Optional[str]: Transcribed text if ready, None if more audio needed
        """
        if sample_rate != self.sample_rate:
            if len(audio_data.shape) == 2:
                audio_data = audio_data.mean(axis=1)  # Convert stereo to mono
            audio_data = torchaudio.functional.resample(
                torch.tensor(audio_data), 
                sample_rate, 
                self.sample_rate
            ).numpy()
        
        audio_data = self.apply_pre_emphasis(audio_data)
        self.audio_buffer.extend(audio_data.tolist())
        
        if len(self.audio_buffer) >= self.sample_rate * 2:  
            try:
                audio_tensor = torch.tensor(self.audio_buffer)
                inputs = self.processor(
                    audio_tensor, 
                    sampling_rate=self.sample_rate, 
                    return_tensors="pt"
                ).input_values.to(self.device)
                
                with torch.no_grad():
                    logits = self.model(inputs).logits
                    predicted_ids = torch.argmax(logits, dim=-1)
                    transcription = self.processor.batch_decode(predicted_ids)[0]
                
                self.audio_buffer = []
                return transcription
                
            except Exception as e:
                print(f"Error during transcription: {str(e)}")
                self.audio_buffer = []
                return None
                
        return None
    
    def reset(self) -> None:
        """Reset the transcriber's internal state."""
        self.audio_buffer = []