"""
OSC Bridge for Synesthesia AI
Sends visual commands from Python brain to Java/Processing visualizer
Uses OSC (Open Sound Control) protocol for low-latency communication
"""

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import time
from typing import Tuple, Optional


class OSCBridge:
    """
    OSC communication bridge to visual engine

    Message formats:
    - /visual/color r g b          # RGB color (0.0-1.0)
    - /visual/particles count size # Particle parameters
    - /visual/motion speed angle   # Movement control
    - /visual/energy level         # Energy level (0.0-1.0)
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 12000):
        """
        Initialize OSC client

        Args:
            host: IP address of visual engine (default: localhost)
            port: OSC port number (default: 12000)
        """
        self.host = host
        self.port = port
        self.client = udp_client.SimpleUDPClient(host, port)

        print(f"OSC Bridge initialized: {host}:{port}")

    def send_color(self, r: float, g: float, b: float):
        """
        Send color command to visualizer

        Args:
            r, g, b: RGB values (0.0 to 1.0)
        """
        self.client.send_message("/visual/color", [r, g, b])

    def send_color_hsv(self, h: float, s: float, v: float):
        """
        Send color in HSV format

        Args:
            h: Hue (0-360)
            s: Saturation (0.0-1.0)
            v: Value/Brightness (0.0-1.0)
        """
        # Convert HSV to RGB
        r, g, b = self.hsv_to_rgb(h, s, v)
        self.send_color(r, g, b)

    def send_particles(self, count: int, size: float):
        """
        Send particle parameters

        Args:
            count: Number of particles
            size: Particle size
        """
        self.client.send_message("/visual/particles", [count, size])

    def send_motion(self, speed: float, angle: float):
        """
        Send motion parameters

        Args:
            speed: Movement speed
            angle: Direction angle (degrees)
        """
        self.client.send_message("/visual/motion", [speed, angle])

    def send_energy(self, level: float):
        """
        Send energy level

        Args:
            level: Energy level (0.0 to 1.0)
        """
        self.client.send_message("/visual/energy", level)

    def send_spectrum(self, bass: float, mid: float, treble: float):
        """
        Send frequency band levels

        Args:
            bass, mid, treble: Energy levels for each band (0.0-1.0)
        """
        self.client.send_message("/visual/spectrum", [bass, mid, treble])

    def send_onset(self, intensity: float):
        """
        Send beat/onset event

        Args:
            intensity: Beat intensity (0.0-1.0)
        """
        self.client.send_message("/visual/onset", intensity)

    def send_raw_message(self, address: str, *args):
        """
        Send custom OSC message

        Args:
            address: OSC address (e.g., "/custom/message")
            *args: Message arguments
        """
        self.client.send_message(address, list(args))

    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
        """
        Convert HSV to RGB

        Args:
            h: Hue (0-360)
            s: Saturation (0.0-1.0)
            v: Value (0.0-1.0)

        Returns:
            (r, g, b) tuple with values 0.0-1.0
        """
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (r + m, g + m, b + m)

    @staticmethod
    def rgb_to_hsv(r: float, g: float, b: float) -> Tuple[float, float, float]:
        """
        Convert RGB to HSV

        Args:
            r, g, b: RGB values (0.0-1.0)

        Returns:
            (h, s, v) tuple - h in 0-360, s and v in 0.0-1.0
        """
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        delta = max_c - min_c

        # Hue
        if delta == 0:
            h = 0
        elif max_c == r:
            h = 60 * (((g - b) / delta) % 6)
        elif max_c == g:
            h = 60 * (((b - r) / delta) + 2)
        else:
            h = 60 * (((r - g) / delta) + 4)

        # Saturation
        s = 0 if max_c == 0 else delta / max_c

        # Value
        v = max_c

        return (h, s, v)


class SynesthesiaMapper:
    """
    Maps audio features to visual parameters using OSC bridge
    Implements synesthesia rules from mapping_rules.json
    """

    def __init__(self, osc_bridge: OSCBridge, mapping_rules: dict):
        """
        Initialize mapper

        Args:
            osc_bridge: OSCBridge instance
            mapping_rules: Rules from config/mapping_rules.json
        """
        self.bridge = osc_bridge
        self.rules = mapping_rules

    def map_frequency_to_color(self, dominant_freq: float, intensity: float) -> Tuple[float, float, float]:
        """
        Map frequency to HSV color based on synesthesia rules

        Args:
            dominant_freq: Dominant frequency (Hz)
            intensity: Sound intensity (0.0-1.0)

        Returns:
            (h, s, v) tuple
        """
        color_rules = self.rules.get("rules", {}).get("color_mapping", {}).get("frequency_ranges", {})

        # Determine which frequency band
        if dominant_freq < 250:
            # Bass → warm colors (red-orange)
            band = color_rules.get("bass", {})
        elif dominant_freq < 2000:
            # Mid → yellow-cyan
            band = color_rules.get("mid", {})
        else:
            # Treble → cool colors (blue-purple)
            band = color_rules.get("treble", {})

        # Get hue range
        hue_range = band.get("hue", [0, 360])
        hue = (hue_range[0] + hue_range[1]) / 2  # Use middle of range

        # Saturation from rules
        saturation = band.get("saturation", 0.8)

        # Value (brightness) from intensity
        value = min(intensity * 2, 1.0)  # Scale intensity to brightness

        return (hue, saturation, value)

    def map_rms_to_particles(self, rms: float) -> Tuple[int, float]:
        """
        Map RMS energy to particle count and size

        Args:
            rms: RMS value (0.0-1.0)

        Returns:
            (count, size) tuple
        """
        particle_rules = self.rules.get("rules", {}).get("particle_mapping", {})
        size_range = particle_rules.get("size_range", [5, 50])

        # Exponential mapping for particle count
        count = int(10 + rms * rms * 100)  # 10-110 particles

        # Linear mapping for size
        size = size_range[0] + rms * (size_range[1] - size_range[0])

        return (count, size)

    def map_onset_to_motion(self, onset: bool, rms: float) -> Tuple[float, float]:
        """
        Map onset detection to motion parameters

        Args:
            onset: Whether onset detected
            rms: Current RMS

        Returns:
            (speed, angle) tuple
        """
        motion_rules = self.rules.get("rules", {}).get("motion_mapping", {})
        onset_velocity = motion_rules.get("onset_velocity", 0.75)

        if onset:
            speed = onset_velocity * (1 + rms)
            angle = (time.time() * 30) % 360  # Slowly rotating angle
        else:
            speed = 0.1  # Minimal movement
            angle = 0

        return (speed, angle)

    def process_audio_features(self, features: dict):
        """
        Process audio features and send OSC commands

        Args:
            features: Dictionary from AudioProcessor.extract_features()
        """
        # Extract features
        dominant_freq = features.get("dominant_freq", 440.0)
        rms = features.get("rms", 0.0)
        onset = features.get("onset", False)

        # Map to visual parameters
        h, s, v = self.map_frequency_to_color(dominant_freq, rms)
        count, size = self.map_rms_to_particles(rms)
        speed, angle = self.map_onset_to_motion(onset, rms)

        # Send OSC messages
        self.bridge.send_color_hsv(h, s, v)
        self.bridge.send_particles(count, size)
        self.bridge.send_motion(speed, angle)
        self.bridge.send_energy(rms)

        if onset:
            self.bridge.send_onset(rms)


# Test function
def test_osc_bridge():
    """
    Test OSC bridge by sending test messages
    Make sure visual engine is running on port 12000
    """
    print("=== OSC Bridge Test ===")
    print("Make sure visual engine is listening on port 12000\n")

    bridge = OSCBridge()

    try:
        print("Sending test messages...")

        # Test color changes
        for i in range(10):
            hue = (i * 36) % 360
            bridge.send_color_hsv(hue, 0.8, 0.9)
            print(f"Color: Hue={hue}")
            time.sleep(0.5)

        # Test particles
        for count in range(10, 100, 20):
            bridge.send_particles(count, 10 + count/10)
            print(f"Particles: count={count}")
            time.sleep(0.3)

        # Test onset
        for i in range(5):
            bridge.send_onset(0.8)
            print("ONSET!")
            time.sleep(0.5)

        print("\nTest complete")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_osc_bridge()
