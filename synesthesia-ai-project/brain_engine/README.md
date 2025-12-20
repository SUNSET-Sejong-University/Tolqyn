# Brain Engine - Synesthesia AI

Python-based audio processing and AI interpretation engine for real-time synesthesia visualization.

## Features

- **Real-time audio capture** from microphone
- **Audio feature extraction**: FFT, RMS, onset detection
- **Synesthesia mapping**: Audio → Visual parameter conversion
- **OSC communication** to visual engine (Java/Processing)
- **AI-driven mapping** rules (extensible with SpoonOS)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Audio Processor

```bash
python audio_processor.py
```

This will capture microphone input and display audio features in the console.

### 3. Test OSC Bridge

```bash
python bridge_osc.py
```

This sends test OSC messages. Make sure your visual engine is listening on port 12000.

### 4. Run Full System

```bash
python main_agent.py
```

This starts the complete synesthesia engine:
- Captures audio from microphone
- Extracts features
- Maps to visual parameters
- Sends OSC commands to visual engine

## Command Line Options

```bash
python main_agent.py --help

Options:
  --config PATH         Path to mapping rules (default: config/mapping_rules.json)
  --osc-host HOST       OSC server host (default: 127.0.0.1)
  --osc-port PORT       OSC server port (default: 12000)
  --sample-rate RATE    Audio sample rate (default: 44100)
  --buffer-size SIZE    Audio buffer size (default: 1024)
```

Example:
```bash
python main_agent.py --osc-port 12345 --buffer-size 512
```

## Architecture

```
[Microphone] 
    ↓
[AudioProcessor] - Extract features (FFT, RMS, onset)
    ↓
[SynesthesiaMapper] - Map audio → visual parameters
    ↓
[OSCBridge] - Send commands via OSC protocol
    ↓
[Visual Engine] (Java/Processing)
```

## Configuration

Edit `config/mapping_rules.json` to customize synesthesia mappings:

```json
{
  "rules": {
    "color_mapping": {
      "frequency_ranges": {
        "bass": {"hz": [20, 250], "hue": [0, 30]},
        "mid": {"hz": [250, 2000], "hue": [60, 180]},
        "treble": {"hz": [2000, 20000], "hue": [200, 280]}
      }
    },
    "motion_mapping": {
      "onset_velocity": 0.75
    },
    "particle_mapping": {
      "size_range": [5, 50]
    }
  }
}
```

## OSC Message Format

The brain engine sends these OSC messages to the visual engine:

| Address | Parameters | Description |
|---------|------------|-------------|
| `/visual/color` | r, g, b (0.0-1.0) | RGB color |
| `/visual/particles` | count, size | Particle parameters |
| `/visual/motion` | speed, angle | Movement control |
| `/visual/energy` | level (0.0-1.0) | Energy level |
| `/visual/onset` | intensity | Beat/onset event |
| `/visual/spectrum` | bass, mid, treble | Frequency bands |

## Modules

### audio_processor.py
Real-time audio capture and feature extraction.

**Key features:**
- FFT spectrum analysis
- RMS energy measurement
- Onset/beat detection
- Low latency (< 30ms target)

### bridge_osc.py
OSC communication bridge to visual engine.

**Key features:**
- Send color, particle, motion commands
- HSV ↔ RGB conversion utilities
- Custom message support

### main_agent.py
Main integration and SpoonOS agent.

**Key features:**
- Coordinates audio processing and OSC
- Loads synesthesia mapping rules
- Statistics and monitoring
- Extensible for AI learning

## Troubleshooting

### No audio input
```bash
# List available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### OSC messages not received
- Make sure visual engine is running
- Check firewall settings
- Verify port number (default: 12000)
- Test with `bridge_osc.py` standalone

### High latency
- Reduce buffer size: `--buffer-size 512`
- Increase sample rate: `--sample-rate 48000`
- Check CPU usage

## Next Steps

- Integrate SpoonOS framework for AI learning
- Add MFCC features for advanced timbre analysis
- Implement user feedback system
- Multi-source audio support

## License

See main project LICENSE file.
