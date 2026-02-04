# Pen Plotter Web Tool — Specification

## Overview

This project is a local, single-user web application for creating SVG drawings and plotting them on an AxiDraw-compatible pen plotter.

The system consists of:

- A Python backend (Flask)
- A browser-based JavaScript UI
- p5.js for creative coding
- p5.plotSvg for generating plotter-compatible SVG
- pyaxidraw for communicating with the physical plotter

The environment is assumed to be:

- High trust
- Localhost only
- One plotter
- One user at a time
- No authentication
- No multi-device support

The goal is simplicity and educational usability.

---

## Core Capabilities

1. Write JavaScript (p5.js) sketches in a browser editor.
2. Preview sketches visually on a canvas.
3. Export plotter-ready SVG via p5.plotSvg.
4. Send SVG directly to the plotter.
5. Interactively jog and control the plotter.
6. Plot SVG layers individually for multi-pen workflows.
7. Apply basic plot settings.
8. Export SVG files for saving work.

No cloud features. No user accounts. No job queue. No safety sandboxing.

---

## Coordinate System

- Origin: top-left
- +X → right
- +Y → down

Same convention for:

- Canvas
- SVG
- Interactive commands

No coordinate conversion.

---

## SVG Handling

### Source of Truth

SVG is generated entirely in the browser using p5.plotSvg.

Backend receives SVG as a string.

Backend does not persist SVG files unless explicitly exported by the user.

### Scaling / Units

Convention A:

> Whatever p5.plotSvg exports is plotted directly.

No backend scaling or unit conversion.

**p5.plotSvg Defaults**:
- Resolution: 96 DPI (set via `setSvgResolutionDPI(96)`)
- Units: Inches internally (96 pixels = 1 inch)
- Document size: Defaults to canvas dimensions from `createCanvas()`, or can be set explicitly with `setSvgDocumentSize(w, h)`

**pyaxidraw Units**:
- Default: Inches (`options.units = 0`)
- Alternative: Centimeters (`options.units = 1`) or Millimeters (`options.units = 2`)
- Interactive commands automatically convert units based on `options.units`

Students are responsible for canvas sizing. The backend accepts SVG coordinates as-is and plots them using pyaxidraw's default inch units.

---

## SVG Offset (Initial X/Y)

Initial plot offset is implemented by wrapping the SVG contents:

<g transform="translate(x,y)">
  ...original SVG...
</g>

- x and y are in SVG coordinate units (same as canvas pixels).
- This happens on the backend before plotting.

No physical jogging before plotting.

---

## Layering

Layering is handled entirely via:

- p5.plotSvg named SVG groups
- AxiDraw "layers" mode

### p5.plotSvg Group Functions

Students create groups using:

```javascript
beginSvgGroup("1 black")
// ... drawing commands ...
endSvgGroup()
```

**Rules**:
- Group names MUST begin with a numeric prefix (1, 2, 3, etc).
- Everything after the number is arbitrary (e.g., "1 black", "2 red", "5 Outlines").
- Groups can be nested, but only top-level groups are considered layers by pyaxidraw.
- When `setSvgInkscapeCompatibility(true)` (default), groups include Inkscape layer attributes (`inkscape:groupmode="layer"` and `inkscape:label`).
- `setSvgMergeNamedGroups(true)` (default) merges groups with the same name at the same hierarchical level.

### Backend Layer Plotting

Backend plotting uses:

```python
ad.options.mode = "layers"
ad.options.layer = N  # N is an integer from 1 to 1000
```

**Layer Matching**: pyaxidraw matches layers whose names begin with the specified number. For example:
- Layer number `5` matches: "5-red", "5 Outlines", "5-blue pen"
- Layer number `5` does NOT match: "55", "guide lines", "2 black"

Only visible layers matching the number are plotted. Multiple layers can match a single number (e.g., both "5-red" and "5 Outlines" will plot when `layer=5`).

---

## Backend Architecture

Python 3.14 + Flask.

Single global AxiDraw instance.

Single threading lock to prevent concurrent hardware access.

No WebSockets.

HTTP only.

Errors are printed to Python console.

### Code Philosophy

- **Simplicity first**: Code is kept simple and readable, assuming dependencies are properly installed.
- **Minimal error handling**: Only handle errors where meaningful (plotter connection failures, command execution errors).
- **No defensive checks**: Assume files exist, dependencies are installed, and the environment is correctly configured.
- **Readable code**: Written for clarity, especially for those new to Python.

### Dependencies

- **Python**: Version 3.14 is required. All Python commands must use `python3.14` to ensure the correct version.
- **Flask**: Installed via pip using Python 3.14.
- **pyaxidraw**: **Not available via pip or npm**. Must be installed manually from a zip file downloaded from the AxiDraw website. See installation instructions in PLAN.md and the [AxiDraw Python API documentation](https://axidraw.com/doc/py_api).

---

## Backend API

### Endpoints

- `GET /state` - Get current connection state
- `POST /connect` - Connect to AxiDraw plotter (interactive mode)
- `POST /disconnect` - Disconnect from AxiDraw plotter
- `POST /cmd` - Execute interactive command (moveto, lineto, penup, pendown, home)
- `POST /plot` - Plot SVG with optional layer selection, offset, and settings
- `POST /stop` - Stop current plot operation and raise pen
- `POST /home` - Return plotter to home position (0, 0)

### pyaxidraw API Reference

The backend uses pyaxidraw (version 3.9.6) which provides two distinct operation contexts:

#### Interactive Context

Used for direct XY motion control commands. Requires a persistent session:

- **Initialization**: `ad.interactive()` - Sets `options.mode = "interactive"`, `options.units = 0` (inches), `options.preview = False`
- **Connection**: `ad.connect()` - Opens USB serial connection, initializes motors, raises pen. Returns `True` on success.
- **Disconnection**: `ad.disconnect()` - Closes USB serial session
- **Update Options**: `ad.update()` - Applies changes to options after connection
- **Motion Commands**:
  - `ad.moveto(x, y)` - Absolute pen-up move to (x, y)
  - `ad.lineto(x, y)` - Absolute pen-down move to (x, y)
  - `ad.goto(x, y)` - Absolute move (maintains current pen state)
  - `ad.move(dx, dy)` - Relative pen-up move
  - `ad.line(dx, dy)` - Relative pen-down move
  - `ad.go(dx, dy)` - Relative move (maintains current pen state)
- **Pen Control**:
  - `ad.penup()` - Raise pen
  - `ad.pendown()` - Lower pen
- **Utilities**:
  - `ad.delay(time_ms)` - Execute timed delay
  - `ad.turtle_pos()` - Report last known turtle position
  - `ad.current_pos()` - Report last known physical position
  - `ad.draw_path(vertex_list)` - Draw a path from coordinate list

#### Plot Context

Used for plotting SVG files:

- **Setup**: `ad.plot_setup(svg_input)` - Parses SVG file or string, initializes plot context
  - `svg_input` can be a file path or SVG string
- **Execution**: `ad.plot_run(output=False)` - Plots the document
  - Returns SVG string if `output=True`
  - Available modes: `"plot"` (default), `"layers"`, `"res_plot"`
- **Options**:
  - `ad.options.mode = "layers"` - Plot only selected layer(s)
  - `ad.options.layer = N` - Layer number (1-1000) - matches layers whose names begin with N
  - `ad.options.preview = True/False` - Enable preview mode (no physical plotting)
  - `ad.options.speed_pendown` - Maximum XY speed when pen is down
  - `ad.options.speed_penup` - Maximum XY speed when pen is up
  - `ad.options.pen_pos_down` - Pen height when down
  - `ad.options.pen_pos_up` - Pen height when up
  - `ad.options.units` - 0=inches (default), 1=centimeters, 2=millimeters

**Important**: Interactive and Plot contexts are mutually exclusive. An instance must be in one mode or the other. Switching between contexts requires creating a new instance or properly disconnecting/reinitializing.

### Implementation Notes

- **Connection Management**: The `/connect` endpoint creates an interactive AxiDraw session using `ad.interactive()` then `ad.connect()`. The `/plot` endpoint automatically disconnects any existing interactive session before plotting, as plotting requires a Plot context instance.

- **Plotting**: The `/plot` endpoint creates a new AxiDraw instance for each plot operation. It uses `plot_setup()` with the SVG string, sets options (mode, layer, speeds, pen heights), then calls `plot_run()`. SVG offset is applied by wrapping the SVG content in a transform group before passing to `plot_setup()`.

- **Layer Plotting**: When a layer number is specified, the backend sets `ad.options.mode = "layers"` and `ad.options.layer = N`. pyaxidraw matches layers whose names begin with the specified number (e.g., layer 5 matches "5-red", "5 Outlines" but not "55" or "guide lines").

- **Stop/Home**: Both `/stop` and `/home` endpoints disconnect the current AxiDraw instance. The `/home` endpoint creates a new interactive instance, uses `moveto(0, 0)` to return to origin, then disconnects.

---

## Pause / Resume

Not implemented initially.

Physical plotter pause button is used.

---

## Frontend

### Current Implementation (Iterations 1-2)

- Connection controls (Connect/Disconnect buttons)
- Status indicator (connected/disconnected)
- Interactive command console with log area
- Plot section with:
  - SVG textarea input (for pasting SVG content)
  - Layer number input (optional)
  - Offset X/Y inputs
  - Plot settings (pen up/down heights, speeds)
  - Plot, Stop, and Home buttons

### Planned (Iteration 3+)

- Code editor (CodeMirror) for writing p5.js sketches
- Canvas preview (p5.js) for visual preview
- SVG export functionality using p5.plotSvg:
  - `beginRecordSvg(p5Instance, filename)` - Start recording
  - `endRecordSvg()` - End recording and return SVG string
  - `pauseRecordSvg(bPause)` - Pause/unpause recording
- Layer workflow UI helpers

### p5.plotSvg API Reference

The frontend uses p5.plotSvg (version 0.1.8) for SVG generation:

**Core Functions**:
- `beginRecordSvg(p5Instance, filename)` - Begin recording SVG output
  - `filename` can be a string (saves file), `null` (no file save), or omitted (defaults to "output.svg")
- `endRecordSvg()` - End recording, generate SVG, restore p5 functions. Returns SVG string.
- `pauseRecordSvg(bPause)` - Pause/unpause recording

**Grouping Functions**:
- `beginSvgGroup(gname)` - Begin named group (for layer workflow)
- `endSvgGroup()` - End current group
- `isRecordingSVG()` - Check if recording is active

**Configuration Functions** (typically called in `setup()`):
- `setSvgDocumentSize(w, h)` - Set SVG dimensions in pixels
- `setSvgResolutionDPI(dpi)` - Set resolution (default: 96 DPI)
- `setSvgResolutionDPCM(dpcm)` - Set resolution in dots per cm
- `setSvgInkscapeCompatibility(bEnabled)` - Enable Inkscape layer attributes (default: `true`)
- `setSvgDefaultStrokeColor(col)` - Set default stroke color (CSS color string)
- `setSvgDefaultStrokeWeight(wei)` - Set default stroke weight
- `setSvgBackgroundColor(col)` - Set optional background color (CSS color string)
- `setSvgGroupByStrokeColor(bEnabled)` - Group elements by stroke color (default: `false`)
- `setSvgMergeNamedGroups(bEnabled)` - Merge groups with same name (default: `true`)
- `setSvgFlattenTransforms(b)` - Flatten transforms vs. hierarchical groups (default: `false`)
- `setSvgCoordinatePrecision(p)` - Decimal digits for coordinates (default: 4)
- `setSvgTransformPrecision(p)` - Decimal digits for transforms (default: 6)
- `setSvgPointRadius(radius)` - Radius for point elements (default: 0.25)
- `setSvgExportPolylinesAsPaths(b)` - Export polylines as `<path>` elements (default: `false`)

**Important Notes**:
- p5.plotSvg only exports vector paths (lines, arcs, shapes, curves). Fills, images, transparency, filters, gradients, and stroke weights are not exported.
- Default stroke color is `black` (can be changed with `setSvgDefaultStrokeColor()`).
- `fill()` commands are ignored; use hatching techniques for filled shapes.
- Alpha/transparency values are stripped from colors.

---

## Non-Goals

- Multi-user support
- Authentication
- Remote access
- Safety sandboxing
- Advanced pause/resume
- Job queues
- Previewing pen-up paths
- SVG clipping or bounds checking

---

End of spec.
