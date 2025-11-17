import java.util.*;
import processing.sound.*;
import processing.video.*;

final int totalNodes = 3000; // total nodes
int visibleNodes = 0;

//int currentNodeIdx = 0;   // currently focused node
int focusStartTime = 0;     // when focus node was selected
int focusDuration = 3000;   // 5 seconds duration of focus

ArrayList<Node> nodes;             // 3D positions of each node (PVector has x, y, z)
ArrayList<Float> nodeSizes;           // the size (thickness) of the point representing each node
ArrayList<Integer> nodeColors;        // color of each node in HSB space
ArrayList<Float> nodesAlpha;          // opacity of each node; lets nodes fade out over time
ArrayList<Edge> edges;                // a list of all Edge objects connecting nodes
ArrayList<Integer> randomFocusNodes;  // indices of nodes currently “in focus” to draw new edges from

float angleY = 0;
float angleZ = 0;
float angleX = 0;
float targetAngleX = 0, targetAngleY = 0;

int addInterval = 5;  // controls how often a new node becomes visible (in frames)
int lastAddTime = 0;  // last time a new node was added (in frames)

FFT fft;
AudioIn in;
int bands = 512;
float[] spectrum = new float[bands];

Capture Cam;
PImage prevFrame;

// C Major
float[] cMajor = {261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88};
// A Minor
float[] aMinor = {220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00};


float B3 = 246.94;
float C4 = 261.63;
float D4 = 293.66;
float E4 = 329.63;
float F4 = 349.23;

// sequence of phrases
float[][] melodyPhrases = {
  {B3, C4, F4, E4},
  {B3, C4, E4, D4},
  {B3, C4, F4},
  {F4, D4, E4}
};

int phraseIndex = 0;  // for the music phrase
int noteIndex = 0;    // for the note inside the phrase

class Edge
{
  PVector a, b;
  float alpha;
  float brightness;
  float thickness;
  Edge(PVector a, PVector b, float brightness, float thickness)
  {
    this.a = a;
    this.b = b;
    this.alpha = 200;
    this.brightness = brightness;
    this.thickness = thickness;
  }
  void draw()
  {
    stroke(255, brightness, alpha);
    strokeWeight(thickness);
    line(a.x, a.y, a.z, b.x, b.y, b.z);
    alpha -= 10.0;
  }
}

class NodeDistance
{
  int index;
  float distance; // distance to focus node
  NodeDistance (int index, float distance)
  {
    this.index = index;
    this.distance = distance;
  }
}

class Node
{
  PVector position;
  int noteIndex;
  float currentFreq;

  public Node (float[] scale)
  {
    float radius = random(width / 5, width / 2);
    float theta = random(TWO_PI); // azimuth (hoz)
    float phi = random(PI); // polar (vert)
    float x = radius * sin(phi) * cos(theta);
    float y = radius * sin(phi) * sin(theta);
    float z = radius * cos(phi); // depth variation
    this.position = new PVector(x, y, z);
    this.noteIndex = int(random(scale.length));
    this.currentFreq = scale[noteIndex];
  }
}
// generate a random node anywhere in 3D space
// PVector randomNode()
// {
//   float radius = random(width / 5, width / 2);
//   float theta = random(TWO_PI); // azimuth (hoz)
//   float phi = random(PI); // polar (vert)
//   float x = radius * sin(phi) * cos(theta);
//   float y = radius * sin(phi) * sin(theta);
//   float z = radius * cos(phi); // depth variation
//   return new PVector(x, y, z);
// }

void playNextMelodyNote(float[][] melody)
{
  float freq = melody[phraseIndex][noteIndex];

  // playing the note
  SinOsc osc = new SinOsc(this);
  osc.freq(freq);
  osc.amp(0.25);
  osc.play();

  // stop after short time
  new Thread(() -> {
    try {
      Thread.sleep(150);
      osc.stop();
    } catch (Exception e) {}
  }).start();

  // transition to next note inside the phrase
  noteIndex++;

  // if phrase finished, go to next phrase
  if (noteIndex >= melody[phraseIndex].length)
  {
    noteIndex = 0;
    phraseIndex = (phraseIndex + 1) % melody.length; // next phrase (loop)
  }
}

void setup()
{
  fullScreen(P3D);

  // ----- Nodes -----
  colorMode(HSB, 360, 100, 100, 255);

  nodes = new ArrayList<Node>();
  nodeSizes = new ArrayList<Float>();
  nodeColors = new ArrayList<Integer>();
  nodesAlpha = new ArrayList<Float>();
  randomFocusNodes = new ArrayList<Integer>();
  edges = new ArrayList<Edge>();

  float[] activeScale = cMajor; // default scale
  for (int i = 0; i < totalNodes; i++)
  {
    nodes.add(new Node(activeScale));
    nodeSizes.add(random(10, 20));
    nodeColors.add(color(random(360), 80, 100));
    nodesAlpha.add(255.0); // bright saturated hues across full spectrum and giving full opacity initially
  }

  noStroke();

  // ----- Audio -----
  // create an input stream which is routed into the Amplitude analyzer
  fft = new FFT(this, bands);
  in = new AudioIn(this, 0);
  // start audio input
  in.start();
  // patch the AudioIn
  fft.input(in);

  // ----- Camera -----
  Cam = new Capture(this, 320, 240);
  Cam.start();
  prevFrame = createImage(Cam.width, Cam.height, RGB);
}

void draw()
{
  background(0);
  blendMode(ADD);
  lights();
  translate(width/2, height/2, -500);          // move camera back a bit
  //rotateX(sin(frameCount * 0.002) * PI/3);     // small back-and-forth tilt
  //rotateY(angleY);                             // slow steady spin
  rotateZ(sin(frameCount * 0.0015) * PI/6);    // subtle drifting rotation
  //angleY += 0.01;
  

  // Read the camera once per frame
  if (Cam.available()) 
  {
    Cam.read();
    //image(Cam, 0, 0);
    pushMatrix();
      translate(0, 0, -10000); 
      rotateY(PI);  // mirror the camera
      imageMode(CENTER);
      image(Cam, 0, 0, width, height);
    popMatrix();

    Cam.loadPixels();
    prevFrame.loadPixels();
    
    float motionX = 0, motionY = 0, motionSum = 0;
    for (int i = 0; i < Cam.pixels.length; i++) {
      float diff = abs(brightness(Cam.pixels[i]) - brightness(prevFrame.pixels[i]));
      if (diff > 15)  // ignore tiny noise
      { 
        motionX += (i % Cam.width) * diff;
        motionY += (i / Cam.width) * diff;
        motionSum += diff;
      }
    }
    println("Motion Sum: " + motionSum);  
    float[] activeScale = cMajor; // default
    if (motionSum > 10000) 
    {
      float centroidX = motionX / motionSum;
      float centroidY = motionY / motionSum;
      float motionFactor = constrain(map(motionSum, 10000, 100000, 0.1, 1.0), 0, 1.0);

      targetAngleY = map(centroidX, 0, Cam.width, -PI/6, PI/6) * motionFactor;
      targetAngleX = map(centroidY, 0, Cam.height, -PI/6, PI/6) * motionFactor;
    
      float motionEnergy = constrain(motionSum / 10000.0, 0, 2);
      activeScale = (motionEnergy < 0.5) ? aMinor : cMajor;
    }

    // copy current frame to previous for next comparison
    prevFrame.copy(Cam, 0, 0, Cam.width, Cam.height, 0, 0, Cam.width, Cam.height);
  }

  // smooth rotation easing
  float easing = 0.1;
  angleX += (targetAngleX - angleX) * easing;
  angleY += (targetAngleY - angleY) * easing;

  // Apply rotations to scene
  rotateX(angleX + sin(frameCount * 0.002) * PI/3);
  rotateY(angleY + frameCount * 0.01);

  // ----- FFT -----
  fft.analyze(spectrum);

  // gradually making nodes visible one by one every few frames
  if (frameCount - lastAddTime > addInterval && visibleNodes < totalNodes)
  {
    visibleNodes++;
    lastAddTime = frameCount;
  }

  noStroke();

  // drawing each node as a 3D point, fading out over time
  // when fully faded, repositioning it randomly and resetting its size, color, and opacity
  float[] activeScale = cMajor;
  for (int i = 0; i < visibleNodes; i++)
  {
    Node n = nodes.get(i);
    float a = nodesAlpha.get(i);
    a -= 1.0; // slow fade rate
    pushMatrix();
    translate(n.position.x, n.position.y, n.position.z);
    stroke(nodeColors.get(i), a);
    strokeWeight(nodeSizes.get(i));
    point(0, 0, 0);
    popMatrix();
    if (a <= 0)
    {
      nodes.set(i, new Node(activeScale));
      nodeSizes.set(i, random(10, 12));
      nodeColors.set(i, color(random(0, 256), random(0, 256), random(0, 256)));
      a = 255.0;
    }
    nodesAlpha.set(i, a);
  }
  // drawing edges in reverse order to allow safe removal while iterating
  for (int i = edges.size() - 1; i >= 0; i--)
  {
    Edge e = edges.get(i);
    e.draw();
    if (e.alpha <= 0)
    {
      edges.remove(i);
    }
  }

  // create new edge based on FFT
  if (nodes.size() >= 2)
  {
    if (visibleNodes >= 2)
    {
      // picking a new focus node every 5 seconds
      if (millis() - focusStartTime >= focusDuration)
      {
        randomFocusNodes.clear(); // clearing the list first
        int randomFocusNodesCount = int(random(1, 6));  // randomizing the number of focus nodes
        for (int i = 0; i < randomFocusNodesCount; i++) randomFocusNodes.add(i, int(random(visibleNodes)));
        //currentNodeIdx = int(random(visibleNodes));
        focusStartTime = millis();

        playNextMelodyNote(melodyPhrases);
      }

      // getting the FFT amplitude average
      float amplitude = 0;
      for (int i = 0; i < bands; i++) amplitude = max(amplitude, spectrum[i]); // use the loudest band

      float threshold = 0.05; // mic sensitivity threshold

      if (amplitude > threshold)
      {
        int numEdges = int(map(amplitude, threshold, 0.05, 1, 6));  // map amplitude to number of edges
        numEdges = constrain(numEdges, 1, 3);                       // limit max edges to avoid clutter

        // for each focus node, find the pairwise distances to all other nodes
        for (int i = 0; i < randomFocusNodes.size(); i++)
        {
          PVector mainNode = nodes.get(randomFocusNodes.get(i)).position;
          ArrayList<NodeDistance> pairs = new ArrayList<NodeDistance>();
          for (int j = 0; j < visibleNodes; j++)
          {
            if (j == i) continue;
            float d = PVector.dist(mainNode, nodes.get(j).position);
            pairs.add(new NodeDistance(j, d));
          }

          //sort by distance (farthest first) using Java built-in Collections.sort() with a custom comparator to control how two items are compared when sorting
          Collections.sort(pairs, new Comparator<NodeDistance>()
          {
            public int compare(NodeDistance a, NodeDistance b)
            {
              return Float.compare(b.distance, a.distance);
            }
          }
          );

          // connect the focus node to a few of the farthest nodes
          int connectCount = min(numEdges, pairs.size());
          for (int k = 0; k < connectCount; k++)
          {
            int idx2 = pairs.get(k).index;
            Node nodeA = nodes.get(randomFocusNodes.get(i)); // main node but getting the class object for music
            Node nodeB = nodes.get(idx2);
            PVector a = mainNode;
            PVector b = nodes.get(idx2).position;

            // soft color blend from node colors
            int c1 = nodeColors.get(i);
            int c2 = nodeColors.get(idx2);
            int blended = lerpColor(c1, c2, random(0.3, 0.7));
            float brightnessBoost = random(0.8, 1.2);
            int edgeCol = color(
              hue(blended),
              saturation(blended),
              constrain(brightness(blended) * brightnessBoost, 0, 100)
              );
            float thickness = random(0.5, 1.5);
            edges.add(new Edge(a, b, edgeCol, thickness));
          }
        }
      }
    }
  }
}
