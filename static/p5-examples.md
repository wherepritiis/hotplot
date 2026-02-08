# p5.js examples for HotPlot

Plotter-friendly sketches: `setup()`, `draw()`, and `noLoop()` for static SVG export. Canvas size 780×560 (8.125" × 5.83" at 96 dpi).

---

## 1. Geometric shapes (single color)

One stroke color; demonstrates line, rect, square, ellipse, circle, triangle, quad, arc variants, point, bezier, and curve.

```javascript
function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function draw() {
  // Line
  line(80, 80, 180, 80);

  // Rectangle
  rect(200, 60, 100, 60);

  // Square
  square(320, 60, 60);

  // Ellipse
  ellipse(450, 90, 100, 60);

  // Circle
  circle(560, 90, 60);

  // Triangle
  triangle(80, 200, 140, 140, 200, 200);

  // Quad
  quad(240, 200, 320, 160, 360, 220, 280, 260);

  // Arc (open)
  arc(450, 180, 80, 80, 0, PI);

  // Arc (chord)
  arc(560, 180, 80, 80, 0, PI, CHORD);

  // Arc (pie)
  arc(670, 180, 80, 80, 0, PI, PIE);

  // Point (optional; may not show in SVG depending on stroke)
  strokeWeight(3);
  point(80, 300);

  // Bezier
  strokeWeight(1);
  bezier(120, 320, 220, 260, 320, 380, 420, 320);

  // Curve
  curve(420, 320, 480, 380, 600, 280, 660, 340);
}
```

---

## 2. Geometric shapes (multi color)

Same shapes in **named SVG layers** via p5.plotSvg’s `beginSvgGroup(name)` / `endSvgGroup()`. Each layer gets an SVG `<g id="...">` and (when Inkscape compatibility is on) `inkscape:groupmode="layer"` and `inkscape:label`, so you can plot by layer or swap pens per layer.

```javascript
function setup() {
  createCanvas(780, 560);
  noFill();
  strokeWeight(1);
  noLoop();
}

function draw() {
  // Layer: black
  beginSvgGroup("black");
  stroke(0);
  line(80, 80, 180, 80);
  rect(200, 60, 100, 60);
  endSvgGroup();

  // Layer: red
  beginSvgGroup("red");
  stroke(255, 0, 0);
  square(320, 60, 60);
  ellipse(450, 90, 100, 60);
  endSvgGroup();

  // Layer: green
  beginSvgGroup("green");
  stroke(0, 160, 0);
  circle(560, 90, 60);
  triangle(80, 200, 140, 140, 200, 200);
  endSvgGroup();

  // Layer: blue
  beginSvgGroup("blue");
  stroke(0, 0, 255);
  quad(240, 200, 320, 160, 360, 220, 280, 260);
  arc(450, 180, 80, 80, 0, PI);
  endSvgGroup();

  // Layer: orange
  beginSvgGroup("orange");
  stroke(255, 140, 0);
  arc(560, 180, 80, 80, 0, PI, CHORD);
  arc(670, 180, 80, 80, 0, PI, PIE);
  endSvgGroup();

  // Layer: purple
  beginSvgGroup("purple");
  stroke(128, 0, 128);
  strokeWeight(2);
  bezier(120, 320, 220, 260, 320, 380, 420, 320);
  strokeWeight(1);
  curve(420, 320, 480, 380, 600, 280, 660, 340);
  endSvgGroup();
}
```

---

## 3. Mouse drawing (freehand)

Draw on the canvas with the mouse: click and drag to add strokes. Strokes are stored and redrawn each frame, so when you export SVG the current drawing is captured. Uses `beginShape()` / `vertex()` / `endShape()` so each stroke becomes a single path in the SVG.

```javascript
let paths = [];      // array of strokes; each stroke is array of [x, y]
let currentPath = []; // points for the stroke being drawn

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function draw() {
  background(255);
  // Redraw all finished strokes
  for (let i = 0; i < paths.length; i++) {
    const path = paths[i];
    if (path.length < 2) continue;
    beginShape();
    for (let j = 0; j < path.length; j++) {
      vertex(path[j][0], path[j][1]);
    }
    endShape();
  }
  // Draw current stroke in progress
  if (currentPath.length >= 2) {
    beginShape();
    for (let k = 0; k < currentPath.length; k++) {
      vertex(currentPath[k][0], currentPath[k][1]);
    }
    endShape();
  }
}

function mousePressed() {
  if (mouseX >= 0 && mouseX <= width && mouseY >= 0 && mouseY <= height) {
    currentPath = [[mouseX, mouseY]];
    redraw();
  }
}

function mouseDragged() {
  if (mouseX >= 0 && mouseX <= width && mouseY >= 0 && mouseY <= height) {
    currentPath.push([mouseX, mouseY]);
    redraw();
  }
}

function mouseReleased() {
  if (currentPath.length > 0) {
    paths.push(currentPath);
    currentPath = [];
    redraw();
  }
}
```

---

# Hatching

## 4. Hatching: Diagonal (single color)

Diagonal parallel lines at 45° inside overlapping rhombus and quadrilaterals. Helper clips each line to each polygon.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 8;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
  }
  for (let k = -400; k <= 800; k += spacing) {
    for (const pts of SHAPES) {
      const seg = clipLineToPoly(-200, -200 + k, 900, 700 + k, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
  }
}
```

---

## 5. Hatching: Diagonal (multi-layer)

Same diagonal hatch with outlines and hatch in separate SVG layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 8;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let k = -400; k <= 800; k += spacing) {
      const seg = clipLineToPoly(-200, -200 + k, 900, 700 + k, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    endSvgGroup();
  }
}
```

---

## 6. Hatching: Cross-hatch (single color)

Two diagonal directions (45° and -45°) inside overlapping rhombus and quads.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 10;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
  }
  for (let k = -400; k <= 800; k += spacing) {
    for (const pts of SHAPES) {
      let seg = clipLineToPoly(-200, -200 + k, 900, 700 + k, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
      seg = clipLineToPoly(-200, 700 + k, 900, -200 + k, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
  }
}
```

---

## 7. Hatching: Cross-hatch (multi-layer)

Same cross-hatch with outline and each diagonal direction as separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 10;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let k = -400; k <= 800; k += spacing) {
      const seg = clipLineToPoly(-200, -200 + k, 900, 700 + k, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    for (let k = -400; k <= 800; k += spacing) {
      const seg = clipLineToPoly(-200, 700 + k, 900, -200 + k, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    endSvgGroup();
  }
}
```

---

## 8. Hatching: Horizontal (single color)

Horizontal lines clipped inside overlapping rhombus and quads.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 10;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
  }
  for (let y = 0; y <= 560; y += spacing) {
    for (const pts of SHAPES) {
      const seg = clipLineToPoly(0, y, 780, y, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
  }
}
```

---

## 9. Hatching: Horizontal (multi-layer)

Outline and horizontal hatch as separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 10;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let y = 0; y <= 560; y += spacing) {
      const seg = clipLineToPoly(0, y, 780, y, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    endSvgGroup();
  }
}
```

---

## 10. Hatching: Vertical (single color)

Vertical lines clipped inside overlapping rhombus and quads.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 10;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
  }
  for (let x = 0; x <= 780; x += spacing) {
    for (const pts of SHAPES) {
      const seg = clipLineToPoly(x, 0, x, 560, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
  }
}
```

---

## 11. Hatching: Vertical (multi-layer)

Outline and vertical hatch as separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 10;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let x = 0; x <= 780; x += spacing) {
      const seg = clipLineToPoly(x, 0, x, 560, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    endSvgGroup();
  }
}
```

---

## 12. Hatching: Grid (single color)

Horizontal and vertical lines inside overlapping rhombus and quads.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 14;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
  }
  for (let y = 0; y <= 560; y += spacing) {
    for (const pts of SHAPES) {
      const seg = clipLineToPoly(0, y, 780, y, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
  }
  for (let x = 0; x <= 780; x += spacing) {
    for (const pts of SHAPES) {
      const seg = clipLineToPoly(x, 0, x, 560, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
  }
}
```

---

## 13. Hatching: Grid (multi-layer)

Outline, horizontal lines, and vertical lines as three separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 14;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let y = 0; y <= 560; y += spacing) {
      const seg = clipLineToPoly(0, y, 780, y, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    for (let x = 0; x <= 780; x += spacing) {
      const seg = clipLineToPoly(x, 0, x, 560, pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    endSvgGroup();
  }
}
```

---

## 14. Hatching: Contour (single color)

Inset contours inside overlapping rhombus and quads—each shape gets concentric inner polygons.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function centroid(pts) {
  let sx = 0, sy = 0;
  for (const p of pts) { sx += p[0]; sy += p[1]; }
  return [sx / pts.length, sy / pts.length];
}

function insetPoly(pts, t) {
  const [cx, cy] = centroid(pts);
  return pts.map(p => [p[0] + (cx - p[0]) * t, p[1] + (cy - p[1]) * t]);
}

function draw() {
  const steps = 5;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let i = 1; i < steps; i++) {
      const inner = insetPoly(pts, i / steps);
      beginShape();
      for (const p of inner) vertex(p[0], p[1]);
      endShape(CLOSE);
    }
  }
}
```

---

## 15. Hatching: Contour (multi-layer)

Outline and inset contours as separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function centroid(pts) {
  let sx = 0, sy = 0;
  for (const p of pts) { sx += p[0]; sy += p[1]; }
  return [sx / pts.length, sy / pts.length];
}

function insetPoly(pts, t) {
  const [cx, cy] = centroid(pts);
  return pts.map(p => [p[0] + (cx - p[0]) * t, p[1] + (cy - p[1]) * t]);
}

function draw() {
  const steps = 5;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let i = 1; i < steps; i++) {
      const inner = insetPoly(pts, i / steps);
      beginShape();
      for (const p of inner) vertex(p[0], p[1]);
      endShape(CLOSE);
    }
    endSvgGroup();
  }
}
```

---

## 16. Hatching: Stipple (single color)

Dots inside overlapping rhombus and quads (point-in-polygon test).

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1.5);
  noLoop();
}

function pointInPoly(x, y, pts) {
  let n = pts.length, inside = false;
  for (let i = 0, j = n - 1; i < n; j = i++) {
    const xi = pts[i][0], yi = pts[i][1];
    const xj = pts[j][0], yj = pts[j][1];
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside;
  }
  return inside;
}

function draw() {
  const spacing = 8;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
  }
  for (let x = 0; x <= 780; x += spacing) {
    for (let y = 0; y <= 560; y += spacing) {
      for (const pts of SHAPES) {
        if (pointInPoly(x, y, pts)) { point(x, y); break; }
      }
    }
  }
}
```

---

## 17. Hatching: Stipple (multi-layer)

Outline and stipple dots as separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1.5);
  noLoop();
}

function pointInPoly(x, y, pts) {
  let n = pts.length, inside = false;
  for (let i = 0, j = n - 1; i < n; j = i++) {
    const xi = pts[i][0], yi = pts[i][1];
    const xj = pts[j][0], yj = pts[j][1];
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside;
  }
  return inside;
}

function draw() {
  const spacing = 8;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let x = 0; x <= 780; x += spacing) {
      for (let y = 0; y <= 560; y += spacing) {
        if (pointInPoly(x, y, pts)) point(x, y);
      }
    }
    endSvgGroup();
  }
}
```

---

## 18. Hatching: Radial (single color)

Rays from each shape’s centroid to its boundary, inside overlapping rhombus and quads.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function centroid(pts) {
  let sx = 0, sy = 0;
  for (const p of pts) { sx += p[0]; sy += p[1]; }
  return [sx / pts.length, sy / pts.length];
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const n = 48;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    const [cx, cy] = centroid(pts);
    for (let i = 0; i < n; i++) {
      const a = (i / n) * TWO_PI;
      const far = 500;
      const seg = clipLineToPoly(cx, cy, cx + far * cos(a), cy + far * sin(a), pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
  }
}
```

---

## 19. Hatching: Radial (multi-layer)

Outline and radial hatch as separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function centroid(pts) {
  let sx = 0, sy = 0;
  for (const p of pts) { sx += p[0]; sy += p[1]; }
  return [sx / pts.length, sy / pts.length];
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const n = 48;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    const [cx, cy] = centroid(pts);
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let i = 0; i < n; i++) {
      const a = (i / n) * TWO_PI;
      const far = 500;
      const seg = clipLineToPoly(cx, cy, cx + far * cos(a), cy + far * sin(a), pts);
      if (seg) line(seg[0], seg[1], seg[2], seg[3]);
    }
    endSvgGroup();
  }
}
```

---

## 20. Hatching: Wavy (single color)

Sine-wave lines clipped inside overlapping rhombus and quads; each horizontal band is a wavy path.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 12;
  const waveAmp = 14;
  const waveFreq = 0.025;
  noFill();
  stroke(0);
  for (const pts of SHAPES) {
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
  }
  for (let y = 0; y <= 560; y += spacing) {
    for (const pts of SHAPES) {
      const seg = clipLineToPoly(0, y, 780, y, pts);
      if (!seg) continue;
      const x0 = seg[0], x1 = seg[2];
      const steps = max(2, floor((x1 - x0) / 5));
      beginShape();
      for (let i = 0; i <= steps; i++) {
        const x = x0 + (i / steps) * (x1 - x0);
        vertex(x, y + waveAmp * sin(x * waveFreq));
      }
      endShape();
    }
  }
}
```

---

## 21. Hatching: Wavy (multi-layer)

Outline and wavy hatch as separate layers.

```javascript
const SHAPES = [
  [[280, 120], [400, 280], [280, 440], [160, 280]],
  [[380, 100], [620, 180], [600, 420], [360, 400]],
  [[160, 320], [340, 480], [520, 440], [400, 240]]
];

function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToPoly(x1, y1, x2, y2, pts) {
  const dx = x2 - x1, dy = y2 - y1;
  const ts = [];
  for (let i = 0; i < pts.length; i++) {
    const ax = pts[i][0], ay = pts[i][1];
    const bx = pts[(i + 1) % pts.length][0], by = pts[(i + 1) % pts.length][1];
    const ex = bx - ax, ey = by - ay;
    const den = dx * ey - dy * ex;
    if (abs(den) < 1e-10) continue;
    const t = ((ax - x1) * ey - (ay - y1) * ex) / den;
    const s = ((x1 - ax) * dy - (y1 - ay) * dx) / (-den);
    if (s >= -1e-6 && s <= 1 + 1e-6) ts.push(t);
  }
  if (ts.length < 2) return null;
  ts.sort((a, b) => a - b);
  const t0 = max(0, min(1, ts[0]));
  const t1 = max(0, min(1, ts[ts.length - 1]));
  if (t0 >= t1 - 1e-6) return null;
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  const spacing = 12;
  const waveAmp = 14;
  const waveFreq = 0.025;
  noFill();
  stroke(0);
  for (let s = 0; s < SHAPES.length; s++) {
    const pts = SHAPES[s];
    beginSvgGroup("shape-" + s);
    beginShape();
    for (const p of pts) vertex(p[0], p[1]);
    endShape(CLOSE);
    for (let y = 0; y <= 560; y += spacing) {
      const seg = clipLineToPoly(0, y, 780, y, pts);
      if (!seg) continue;
      const x0 = seg[0], x1 = seg[2];
      const steps = max(2, floor((x1 - x0) / 5));
      beginShape();
      for (let i = 0; i <= steps; i++) {
        const x = x0 + (i / steps) * (x1 - x0);
        vertex(x, y + waveAmp * sin(x * waveFreq));
      }
      endShape();
    }
    endSvgGroup();
  }
}
```

---

# Classical pieces

## 22. Classical: Frieder Nake — Walk-Through-Raster (1966)

Inspired by Nake’s plotter series: a raster grid with a “walk” of marks through each cell. Multi-layer: grid, then walk (one layer for grid lines, one for cell marks).

```javascript
function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function draw() {
  randomSeed(2201);
  const cols = 24, rows = 18;
  const cellW = width / cols, cellH = height / rows;

  beginSvgGroup("grid");
  for (let i = 0; i <= cols; i++) line(i * cellW, 0, i * cellW, height);
  for (let j = 0; j <= rows; j++) line(0, j * cellH, width, j * cellH);
  endSvgGroup();

  beginSvgGroup("walk");
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      const cx = (i + 0.5) * cellW;
      const cy = (j + 0.5) * cellH;
      const len = min(cellW, cellH) * 0.35;
      const a = random(TWO_PI);
      line(cx - len * cos(a), cy - len * sin(a), cx + len * cos(a), cy + len * sin(a));
    }
  }
  endSvgGroup();
}
```



---

## 23. Classical: Michael Noll — Computer Composition With Lines (1964)

After Noll’s piece: circular boundary with dense horizontal and vertical segments of varying length (maze-like, L- and T-shapes). [Early Generative Art – A. Michael Noll](https://uk.pinterest.com/pin/993677105283799375/). Layers: boundary, vertical, horizontal. Lines clipped to circle.

```javascript
function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function clipLineToCircle(x1, y1, x2, y2, cx, cy, r) {
  const dx = x2 - x1, dy = y2 - y1;
  const a = dx * dx + dy * dy;
  if (a < 1e-10) return null;
  const b = 2 * ((x1 - cx) * dx + (y1 - cy) * dy);
  const c = (x1 - cx) ** 2 + (y1 - cy) ** 2 - r * r;
  let d = b * b - 4 * a * c;
  if (d < 0) return null;
  d = sqrt(d);
  let t0 = (-b - d) / (2 * a), t1 = (-b + d) / (2 * a);
  if (t0 > 1 || t1 < 0) return null;
  t0 = max(0, min(1, t0));
  t1 = max(0, min(1, t1));
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function draw() {
  randomSeed(2401);
  const cx = 390, cy = 280, r = 250;
  const nVert = 90, nHoriz = 95;

  beginSvgGroup("boundary");
  beginShape();
  for (let a = 0; a < TWO_PI; a += 0.05) vertex(cx + r * cos(a), cy + r * sin(a));
  endShape(CLOSE);
  endSvgGroup();

  beginSvgGroup("vertical");
  for (let i = 0; i < nVert; i++) {
    const x = cx - r + random(2 * r);
    const len = 8 + random(r * 0.6);
    const y0 = cy - r + random(2 * r - len);
    const seg = clipLineToCircle(x, y0, x, y0 + len, cx, cy, r);
    if (seg) line(seg[0], seg[1], seg[2], seg[3]);
  }
  endSvgGroup();

  beginSvgGroup("horizontal");
  for (let i = 0; i < nHoriz; i++) {
    const y = cy - r + random(2 * r);
    const len = 8 + random(r * 0.6);
    const x0 = cx - r + random(2 * r - len);
    const seg = clipLineToCircle(x0, y, x0 + len, y, cx, cy, r);
    if (seg) line(seg[0], seg[1], seg[2], seg[3]);
  }
  endSvgGroup();
}
```

---

## 24. Classical: Michael Noll — Vertical-Horizontal Number Three (1964)

After Noll’s piece: a dense vertical column of overlapping black outlines of rectangles and squares (narrow tall, wider short, approximate squares), concentrated upper-middle/right with empty space on the left. [The Interview | A. Michael Noll](https://uk.pinterest.com/pin/993677105283799358/). Layers: tall-rectangles, wide-rectangles, squares.

```javascript
function setup() {
  createCanvas(780, 560);
  noFill();
  stroke(0);
  strokeWeight(1);
  noLoop();
}

function draw() {
  randomSeed(2501);
  const colCenterX = 520;
  const colTop = 40, colBottom = 520;
  const colWidth = 220;
  const tall = [], wide = [], squares = [];

  for (let i = 0; i < 85; i++) {
    const w = 6 + random(55);
    const h = 12 + random(90);
    const x = colCenterX - colWidth / 2 + random(colWidth - w);
    const y = colTop + random(colBottom - colTop - h);
    if (h > w * 1.4) tall.push({ x, y, w, h });
    else if (w > h * 1.4) wide.push({ x, y, w, h });
    else squares.push({ x, y, w, h });
  }

  beginSvgGroup("tall-rectangles");
  for (const r of tall) rect(r.x, r.y, r.w, r.h);
  endSvgGroup();

  beginSvgGroup("wide-rectangles");
  for (const r of wide) rect(r.x, r.y, r.w, r.h);
  endSvgGroup();

  beginSvgGroup("squares");
  for (const r of squares) rect(r.x, r.y, r.w, r.h);
  endSvgGroup();
}
```

---

## 25. Classical: Vera Molnár — (Des)Ordres (1974)

Inspired by Molnár’s 20×20 grid of concentrically displaced squares. One layer per color group (6 layers). randomSeed for reproducibility.

```javascript
function setup() {
  createCanvas(780, 560);
  noFill();
  strokeWeight(1);
  noLoop();
}

function draw() {
  randomSeed(2601);
  const gridN = 20;
  const margin = 60;
  const cellSize = (min(width, height) - 2 * margin) / gridN;
  const ox = (width - gridN * cellSize) / 2 + cellSize / 2;
  const oy = (height - gridN * cellSize) / 2 + cellSize / 2;
  const layers = 6;
  const colors = [[0,0,0], [200,50,50], [50,120,80], [220,140,0], [200,50,150], [40,80,180]];

  for (let L = 0; L < layers; L++) {
    stroke(colors[L][0], colors[L][1], colors[L][2]);
    beginSvgGroup("color-" + L);
    for (let i = 0; i < gridN; i++) {
      for (let j = 0; j < gridN; j++) {
        if ((i * gridN + j) % layers !== L) continue;
        const cx = ox + i * cellSize;
        const cy = oy + j * cellSize;
        const maxR = cellSize * 0.4;
        const dx = random(-6, 6);
        const dy = random(-6, 6);
        for (let r = maxR; r > 4; r -= 5) {
          const rr = r * 0.9;
          rect(cx + dx - rr/2, cy + dy - rr/2, rr, rr);
        }
      }
    }
    endSvgGroup();
  }
}
```

---

## 26. Classical: Vera Molnár — (Des)Ordres, small grid

Smaller 10×10 grid, 3 color layers. Same concentric squares with random displacement.

```javascript
function setup() {
  createCanvas(780, 560);
  noFill();
  strokeWeight(1);
  noLoop();
}

function draw() {
  randomSeed(2701);
  const gridN = 10;
  const margin = 80;
  const cellSize = (min(width, height) - 2 * margin) / gridN;
  const ox = (width - gridN * cellSize) / 2 + cellSize / 2;
  const oy = (height - gridN * cellSize) / 2 + cellSize / 2;
  const layers = 3;
  const colors = [[0,0,0], [180,60,60], [50,100,160]];

  for (let L = 0; L < layers; L++) {
    stroke(colors[L][0], colors[L][1], colors[L][2]);
    beginSvgGroup("color-" + L);
    for (let i = 0; i < gridN; i++) {
      for (let j = 0; j < gridN; j++) {
        if ((i * gridN + j) % layers !== L) continue;
        const cx = ox + i * cellSize;
        const cy = oy + j * cellSize;
        const maxR = cellSize * 0.42;
        const dx = random(-8, 8);
        const dy = random(-8, 8);
        for (let r = maxR; r > 5; r -= 6) {
          const rr = r * 0.88;
          rect(cx + dx - rr/2, cy + dy - rr/2, rr, rr);
        }
      }
    }
    endSvgGroup();
  }
}
```

*More examples will be added here.*
