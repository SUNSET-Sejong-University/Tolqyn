"""
Real-time Audio Processor for Synesthesia AI
Captures microphone input and extracts audio features (FFT, RMS, MFCC, onset detection)
Target latency: < 30ms
"""

import numpy as np
import sounddevice as sd
from scipy import signal
from scipy.fft import fft, fftfreq
import time
from typing import Dict, Optional, Callable
import threading
import queue


class AudioProcessor:
    """
    Real-time audio feature extraction engine

    Features:
    - FFT (Fast Fourier Transform): Frequency spectrum analysis
    - RMS (Root Mean Square): Sound intensity measurement
    - MFCC: Mel-Frequency Cepstral Coefficients (timbre analysis)
    - Onset Detection: Beat/rhythm detection
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 1024,
        callback: Optional[Callable] = None
    ):
        
        
        """
        Initialize audio processor

        Args:
            sample_rate: Audio sampling rate (Hz)
            buffer_size: Audio buffer size (samples) - smaller = lower latency
            callback: Function to call when features are extracted
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.callback = callback

        # Audio stream
        self.stream = None
        self.is_running = False

        # Feature extraction state
        self.audio_queue = queue.Queue(maxsize=10)
        self.previous_rms = 0.0
        self.onset_threshold = 0.3  # Threshold for beat detection

        # FFT settings
        self.fft_size = buffer_size
        self.freq_bins = fftfreq(self.fft_size, 1/self.sample_rate)
        
        self.cached_window = signal.windows.hann(self.buffer_size)

        print(f"AudioProcessor initialized: {sample_rate}Hz, buffer={buffer_size}")

    def audio_callback(self, indata, frames, time_info, status):
        """
        Called by sounddevice when audio data is available
        This runs in a separate thread - keep it fast!
        """
        if status:
            print(f"Audio callback status: {status}")

        # Copy audio data and put in queue for processing
        try:
            audio_data = indata[:, 0].copy()  # Use mono (first channel)
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            pass  # Drop frame if queue is full (shouldn't happen normally)

    def start(self):
        """Start audio capture"""
        if self.is_running:
            print("Audio processor already running")
            return

        self.is_running = True

        # Start audio input stream
        self.stream = sd.InputStream(
            channels=1,  # Mono
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            callback=self.audio_callback
        )
        self.stream.start()

        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_loop)
        self.processing_thread.start()

        print("Audio capture started")

    def stop(self):
        """Stop audio capture"""
        if not self.is_running:
            return

        self.is_running = False

        if self.stream:
            self.stream.stop()
            self.stream.close()

        if hasattr(self, 'processing_thread'):
            self.processing_thread.join()

        print("Audio capture stopped")

    def _process_loop(self):
        """Main processing loop (runs in separate thread)"""
        while self.is_running:
            try:
                # Get audio data from queue (block with timeout)
                audio_data = self.audio_queue.get(timeout=0.1)

                # Extract features
                features = self.extract_features(audio_data)

                # Call user callback if provided
                if self.callback:
                    self.callback(features)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in processing loop: {e}")

    def extract_features(self, audio_data: np.ndarray) -> Dict:
        """
        Extract all audio features from buffer

        Returns:
            Dictionary with:
                - timestamp: Unix timestamp
                - spectrum: FFT magnitudes
                - dominant_freq: Main frequency (Hz)
                - rms: Sound intensity
                - onset: Beat detected (bool)
        """
        timestamp = time.time()

        # 1. FFT - Frequency spectrum
        spectrum = self.compute_fft(audio_data)

        # 2. Dominant frequency
        dominant_freq = self.find_dominant_freq(spectrum)

        # 3. RMS - Sound intensity
        rms = self.compute_rms(audio_data)

        # 4. Onset detection - Beat/rhythm
        onset = self.detect_onset(rms)

        # Package results
        features = {
            'timestamp': timestamp,
            'spectrum': spectrum.tolist(),  # Convert to list for JSON serialization
            'dominant_freq': float(dominant_freq),
            'rms': float(rms),
            'onset': onset,
            'sample_rate': self.sample_rate,
        }

        return features

    def compute_fft(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Compute FFT and return magnitude spectrum

        Returns:
            Array of magnitudes for positive frequencies
        """
        
        n = len(audio_data)
        
        if n == self.buffer_size:
            window = self.cached_window
        else:
            # 크기가 다르면 어쩔 수 없이 새로 계산 (느림, 하지만 안전함)
            # 예: 스트림 시작/종료 시점 등
            window = signal.windows.hann(n)
            
        # 윈도우 적용
        windowed = audio_data * window
        

        # Compute FFT
        fft_result = fft(windowed)

        # Get magnitude spectrum (only positive frequencies)
        magnitude = np.abs(fft_result[:len(fft_result)//2])

        # Normalize
        magnitude = magnitude / n

        return magnitude

    def find_dominant_freq(self, spectrum: np.ndarray) -> float:
        """
        Find the dominant frequency in the spectrum

        Returns:
            Frequency in Hz
        """
        # Find peak frequency (excluding DC component)
        positive_freqs = self.freq_bins[:len(spectrum)]

        # Ignore very low frequencies (< 20 Hz)
        min_idx = np.searchsorted(positive_freqs, 20)

        # Find peak
        peak_idx = np.argmax(spectrum[min_idx:]) + min_idx
        dominant_freq = positive_freqs[peak_idx]

        return dominant_freq

    def compute_rms(self, audio_data: np.ndarray) -> float:
        """
        Compute RMS (Root Mean Square) - sound intensity

        Returns:
            RMS value (0.0 to 1.0 range typically)
        """
        rms = np.sqrt(np.mean(audio_data**2))
        return rms

    def detect_onset(self, current_rms: float) -> bool:
        """
        Simple onset detection based on RMS energy increase

        Args:
            current_rms: Current RMS value

        Returns:
            True if onset detected (beat/rhythm)
        """
        # Detect sudden energy increase
        delta = current_rms - self.previous_rms
        onset = delta > self.onset_threshold

        # Update state
        self.previous_rms = current_rms

        return onset

    def get_frequency_bands(self, spectrum: np.ndarray) -> Dict[str, float]:
        """
        Split spectrum into frequency bands (bass, mid, treble)
        Useful for synesthesia mapping

        Returns:
            Dict with 'bass', 'mid', 'treble' energy levels
        """
        freqs = self.freq_bins[:len(spectrum)]

        # Define frequency ranges (Hz)
        bass_range = (20, 250)
        mid_range = (250, 2000)
        treble_range = (2000, 20000)

        # Get indices for each band
        bass_idx = np.where((freqs >= bass_range[0]) & (freqs < bass_range[1]))[0]
        mid_idx = np.where((freqs >= mid_range[0]) & (freqs < mid_range[1]))[0]
        treble_idx = np.where((freqs >= treble_range[0]) & (freqs < treble_range[1]))[0]

        # Calculate average energy in each band
        bands = {
            'bass': float(np.mean(spectrum[bass_idx])) if len(bass_idx) > 0 else 0.0,
            'mid': float(np.mean(spectrum[mid_idx])) if len(mid_idx) > 0 else 0.0,
            'treble': float(np.mean(spectrum[treble_idx])) if len(treble_idx) > 0 else 0.0,
        }

        return bands


# Test function
def test_audio_processor():
    """
    Test the audio processor with live microphone input
    """
    print("=== Audio Processor Test ===")
    print("Speak into your microphone...")
    print("Press Ctrl+C to stop\n")

    def on_features(features):
        """Callback to print extracted features"""
        print(f"RMS: {features['rms']:.3f} | "
              f"Freq: {features['dominant_freq']:.1f} Hz | "
              f"Onset: {'BEAT!' if features['onset'] else '----'}")

    # Create processor
    processor = AudioProcessor(
        sample_rate=44100,
        buffer_size=1024,
        callback=on_features
    )

    try:
        processor.start()

        # Run for a while
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        processor.stop()
        print("Test complete")


if __name__ == "__main__":
    test_audio_processor()
