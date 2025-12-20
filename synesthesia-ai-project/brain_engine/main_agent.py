"""
Synesthesia AI - Main Agent
SpoonOS-based AI agent for audio-to-visual synesthesia mapping
Integrates audio processing, AI interpretation, and OSC visualization
"""

import json
import time
import os
from pathlib import Path
from typing import Dict, Optional

from audio_processor import AudioProcessor
from bridge_osc import OSCBridge, SynesthesiaMapper


class SynesthesiaAgent:
    """
    Main AI Agent for Synesthesia Media Art

    Workflow:
    1. Capture audio from microphone (AudioProcessor)
    2. Extract audio features (FFT, RMS, onset)
    3. Map features to visual parameters (SynesthesiaMapper)
    4. Send OSC commands to visual engine (OSCBridge)
    5. (Optional) Learn and update mapping rules with AI
    """

    def __init__(
        self,
        config_path: str = "config/mapping_rules.json",
        osc_host: str = "127.0.0.1",
        osc_port: int = 12000,
        sample_rate: int = 44100,
        buffer_size: int = 1024
    ):
        """
        Initialize Synesthesia Agent

        Args:
            config_path: Path to mapping rules JSON
            osc_host: OSC server host (visual engine)
            osc_port: OSC server port
            sample_rate: Audio sample rate
            buffer_size: Audio buffer size
        """
        print("=" * 60)
        print("SYNESTHESIA AI - Brain Engine")
        print("=" * 60)

        # Load mapping rules
        self.config_path = Path(config_path)
        self.mapping_rules = self.load_mapping_rules()

        # Initialize OSC bridge
        self.osc_bridge = OSCBridge(host=osc_host, port=osc_port)

        # Initialize synesthesia mapper
        self.mapper = SynesthesiaMapper(self.osc_bridge, self.mapping_rules)

        # Initialize audio processor with callback
        self.audio_processor = AudioProcessor(
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            callback=self.on_audio_features
        )

        # Statistics
        self.stats = {
            'frames_processed': 0,
            'onsets_detected': 0,
            'start_time': None
        }

        print("\n[✓] Synesthesia Agent initialized")
        print(f"    Config: {config_path}")
        print(f"    OSC: {osc_host}:{osc_port}")
        print(f"    Audio: {sample_rate}Hz, buffer={buffer_size}")
        print()

    def load_mapping_rules(self) -> Dict:
        """
        Load synesthesia mapping rules from JSON config

        Returns:
            Dictionary with mapping rules
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            print(f"[✓] Loaded mapping rules: {self.config_path}")
            return rules
        except FileNotFoundError:
            print(f"[!] Config file not found: {self.config_path}")
            print("    Using default mapping rules")
            return self.get_default_rules()
        except json.JSONDecodeError as e:
            print(f"[!] Invalid JSON in config: {e}")
            print("    Using default mapping rules")
            return self.get_default_rules()

    def save_mapping_rules(self):
        """
        Save current mapping rules back to JSON
        (for AI learning updates)
        """
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write with pretty formatting
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.mapping_rules, f, indent=2, ensure_ascii=False)

            print(f"[✓] Saved updated mapping rules to {self.config_path}")
        except Exception as e:
            print(f"[!] Failed to save mapping rules: {e}")
    
    def update_ai_reasoning(self):
        """
        SpoonOS 에이전트가 주기적으로 호출하여
        음악 분위기에 따라 매핑 규칙을 스스로 수정하는 함수
        """
        print("\n[🧠] AI Agent is thinking... (Updating Rules)")
        
        # 1. 현재 오디오 통계 수집 (최근 5초간의 데이터)
        if not self.recent_rms_values:
            return
            
        avg_rms = sum(self.recent_rms_values) / len(self.recent_rms_values)
        self.recent_rms_values.clear() # 초기화

        # -------------------------------------------------------------
        # [SpoonOS 영역] 실제로는 여기서 LLM에게 avg_rms 등의 데이터를 주고 판단을 요청함
        # 지금은 간단한 로직으로 시뮬레이션:
        # -------------------------------------------------------------
        
        # 예시 로직: 소리가 아주 크면(격정적) -> 입자를 크게, 색상을 붉게 변경
        if avg_rms > 0.3: 
            print("   ↳ Mood: Intense/Energetic! Increasing particles.")
            new_size_range = [20, 100] # 입자 크기 대폭 증가
            new_hue_base = 0           # 붉은색 계열 (Red)
        else:
            print("   ↳ Mood: Calm/Ambient. Decreasing particles.")
            new_size_range = [2, 10]   # 입자 크기 축소
            new_hue_base = 200         # 푸른색 계열 (Blue)

        # 2. mapping_rules 내부 값 수정 (Self-Correction)
        # self.mapping_rules는 딕셔너리이므로 직접 수정 가능
        
        # 입자 크기 규칙 수정
        self.mapping_rules["rules"]["particle_mapping"]["size_range"] = new_size_range
        
        # 베이스(저음) 색상 규칙 수정
        self.mapping_rules["rules"]["color_mapping"]["frequency_ranges"]["bass"]["hue"] = [new_hue_base, new_hue_base + 30]

        # 3. 매퍼(Mapper)에게 변경된 규칙 즉시 적용
        # (중요: 이걸 해줘야 SynesthesiaMapper가 바뀐 규칙으로 계산함)
        self.mapper.rules = self.mapping_rules
        
        # (선택) 변경된 규칙 저장
        # self.save_mapping_rules()
        
    def on_audio_features(self, features: Dict):
        """
        Callback when audio features are extracted
        This is called by AudioProcessor in real-time

        Args:
            features: Dictionary with audio features
        """
        # Update statistics
        self.stats['frames_processed'] += 1
        if features.get('onset', False):
            self.stats['onsets_detected'] += 1

        # Map audio features to visual parameters and send OSC
        self.mapper.process_audio_features(features)

        # Optional: Print status every N frames
        if self.stats['frames_processed'] % 50 == 0:
            self.print_status(features)

    def print_status(self, features: Dict):
        """
        Print current status (for monitoring)

        Args:
            features: Latest audio features
        """
        elapsed = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        fps = self.stats['frames_processed'] / elapsed if elapsed > 0 else 0

        print(f"[{self.stats['frames_processed']:05d}] "
              f"RMS: {features.get('rms', 0):.3f} | "
              f"Freq: {features.get('dominant_freq', 0):.1f}Hz | "
              f"Onsets: {self.stats['onsets_detected']} | "
              f"FPS: {fps:.1f}")

    def start(self):
        """
        Start the synesthesia engine
        """
        print("[→] Starting Synesthesia Engine...")
        print("    Listening to microphone...")
        print("    Press Ctrl+C to stop\n")

        self.stats['start_time'] = time.time()

        # Start audio processing
        self.audio_processor.start()

        try:
            # Keep running
            while True:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n[!] Stopping...")
        finally:
            self.stop()

    def stop(self):
        """
        Stop the synesthesia engine
        """
        # Stop audio processor
        self.audio_processor.stop()

        # Print final statistics
        elapsed = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        print("\n" + "=" * 60)
        print("SESSION STATISTICS")
        print("=" * 60)
        print(f"Duration:        {elapsed:.1f} seconds")
        print(f"Frames:          {self.stats['frames_processed']}")
        print(f"Onsets detected: {self.stats['onsets_detected']}")
        if elapsed > 0:
            print(f"Avg FPS:         {self.stats['frames_processed'] / elapsed:.1f}")
        print("=" * 60)

    @staticmethod
    def get_default_rules() -> Dict:
        """
        Get default mapping rules if config file is missing

        Returns:
            Default mapping rules dictionary
        """
        return {
            "version": "1.0",
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "rules": {
                "color_mapping": {
                    "frequency_ranges": {
                        "bass": {
                            "hz": [20, 250],
                            "hue": [0, 30],
                            "saturation": 0.8
                        },
                        "mid": {
                            "hz": [250, 2000],
                            "hue": [60, 180],
                            "saturation": 0.6
                        },
                        "treble": {
                            "hz": [2000, 20000],
                            "hue": [200, 280],
                            "saturation": 0.9
                        }
                    }
                },
                "motion_mapping": {
                    "onset_velocity": 0.75,
                    "decay_rate": 0.95
                },
                "particle_mapping": {
                    "energy_to_count": "exponential",
                    "size_range": [5, 50]
                }
            },
            "learning_params": {
                "adaptation_rate": 0.1,
                "user_feedback_weight": 0.3
            }
        }
        


def main():
    """
    Main entry point
    """
    # Parse command line arguments (optional)
    import argparse

    parser = argparse.ArgumentParser(description="Synesthesia AI - Brain Engine")
    parser.add_argument(
        '--config',
        default='config/mapping_rules.json',
        help='Path to mapping rules config (default: config/mapping_rules.json)'
    )
    parser.add_argument(
        '--osc-host',
        default='127.0.0.1',
        help='OSC host for visual engine (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--osc-port',
        type=int,
        default=12000,
        help='OSC port for visual engine (default: 12000)'
    )
    parser.add_argument(
        '--sample-rate',
        type=int,
        default=44100,
        help='Audio sample rate (default: 44100)'
    )
    parser.add_argument(
        '--buffer-size',
        type=int,
        default=1024,
        help='Audio buffer size (default: 1024)'
    )

    args = parser.parse_args()

    # Create and start agent
    agent = SynesthesiaAgent(
        config_path=args.config,
        osc_host=args.osc_host,
        osc_port=args.osc_port,
        sample_rate=args.sample_rate,
        buffer_size=args.buffer_size
    )

    agent.start()
    
    


if __name__ == "__main__":
    main()
