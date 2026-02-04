# Implementation Plan

Goal: Build a minimal, working plotting tool first. Refine later.

Constraint: **At the end of every iteration, there must be a testable UI in the browser** (served at `/`) so the reviewer does not need curl/Postman.

We will implement a simple single-page “Control Panel” UI early and expand it iteratively. No build tools, no React, no bundlers.

---

## Prerequisites

### Python Version

**Python 3.14 is required.** All Python commands must use `python3.14` explicitly to ensure the correct version is used.

### Installing pyaxidraw

pyaxidraw (version 3.9.6) is **not available via pip or npm**. It must be installed manually:

1. Download the AxiDraw API zip file from: https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
   - Or visit the [AxiDraw Python API documentation](https://axidraw.com/doc/py_api) for the latest download link and installation instructions.
2. Unzip the archive.
3. Navigate into the unzipped directory.
4. Install using Python 3.14:
   ```bash
   python3.14 -m pip install .
   ```

Alternatively, you can install directly from the URL:
```bash
python3.14 -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
```

**pyaxidraw Requirements**:
- Python 3.7 or newer (we use 3.14)
- Pyserial 3.5 or newer
- The package includes `pyaxidraw.axidraw.AxiDraw` class and related modules

**Documentation**: Reference documentation is available in `docs/pyaxidraw/documentation/axidraw_python.html` (included in downloaded package).

### Installing Other Dependencies

Install Flask and other pip-installable dependencies:
```bash
python3.14 -m pip install -r requirements.txt
```

### Frontend Dependencies

The frontend requires:
- **p5.js** - Creative coding library (version 1.4.2 through 1.11.11 compatible)
- **p5.plotSvg** - SVG export library for p5.js (version 0.1.8)
  - Available via CDN: https://cdn.jsdelivr.net/npm/p5.plotsvg@latest/lib/p5.plotSvg.js
  - Or download from: https://raw.githubusercontent.com/golanlevin/p5.plotSvg/refs/heads/main/lib/p5.plotSvg.js
- **CodeMirror** (for Iteration 3+) - Code editor component

**p5.plotSvg Documentation**: Reference documentation is available in `docs/plotsvg/documentation.md`.

**Important**: Always use `python3.14` (not `python`, `python3`, or `python3.13`) for all commands to ensure version consistency.

---

## Iteration 1 — Minimal Server + Basic Control Panel UI ✅ COMPLETE

### Goals
- Flask server runs locally using Python 3.14.
- AxiDraw can be connected/disconnected from a browser UI.
- A basic “Command” input exists in the UI.

### Backend
- Global AxiDraw instance + `threading.Lock()`.
- Endpoints:
  - `GET /state`
  - `POST /connect`
  - `POST /disconnect`
  - `POST /cmd`
- Error handling only for plotter connection and command execution errors.

### Frontend (Required)
Serve `/` with a minimal HTML page that includes:
- “Connect” button
- “Disconnect” button
- Command input (e.g., `moveto 1 1`) and “Send” button
- Log area to show responses/errors
- State indicator (connected/disconnected)

### Running the Server

Start the Flask server using Python 3.14:
```bash
python3.14 app.py
```

The server will be available at `http://localhost:3000/`

### Review Point
Open `/` in a browser and verify connect/disconnect and a command works.

---

## Iteration 2 — Plotting + Plot UI ✅ COMPLETE

### Goals
- Plot an SVG from the browser.
- Apply basic settings and offsets.
- Plot a specified layer number.

### Backend
Add endpoints:
- `POST /plot`
- `POST /stop`
- `POST /home`

Implement:
- SVG translate offset wrapper (wrap SVG in `<g transform="translate(x,y)">`)
- Basic settings: pen up/down heights (`pen_pos_up`, `pen_pos_down`), speeds (`speed_penup`, `speed_pendown`)
- Layer plotting via pyaxidraw options:
  - `ad.options.mode = "layers"` - Enable layer mode
  - `ad.options.layer = N` - Select layer number (1-1000, matches layers whose names begin with N)
- Plot workflow:
  1. Create new AxiDraw instance
  2. Call `plot_setup(svg_string)` with offset-wrapped SVG
  3. Set options (mode, layer, speeds, pen heights)
  4. Call `plot_run()` to execute plot
  5. Disconnect instance

### Frontend (Required)
Add a Plot section on `/`:
- Textarea to paste SVG (temporary, until editor exists)
- Inputs: layer number (optional), offset X/Y, pen up/down, speed up/down
- Buttons:
  - Plot
  - Stop (non-resumable)
  - Home

### Review Point
Open `/`, paste a known-good SVG, plot it, and test Stop/Home.

**Status**: All features implemented and tested. The plot endpoint handles SVG offset wrapping via transform groups, layer selection, and plotter settings (pen up/down heights, speeds). The UI includes all required inputs and buttons. The backend properly manages AxiDraw instance lifecycle (disconnects interactive session before plotting, creates new instance for plot operations).

---

## Iteration 3 — Editor + Preview + SVG Export UI

### Goals
- Write p5.js code in the browser.
- Preview on a canvas.
- Generate SVG using p5.plotSvg and view it.

### Backend
No major changes required (keep Iteration 2 endpoints).

### Frontend (Required)
Enhance `/` with:
- Code editor (CodeMirror)
- Preview area (iframe running p5 sketch)
- Buttons:
  - Run Preview
  - Export SVG (captures via beginRecordSvg/endRecordSvg)
- Exported SVG shown in a textarea (and downloadable)

Also:
- “Use Exported SVG” button to load it into the Plot section

### Review Point
Open `/`, write code, preview, export SVG, then plot without copy/paste.

---

## Iteration 4 — Layer Workflow UI

### Goals
- Support multi-pen layer workflow cleanly.

### Backend
No changes required if layer plotting is already supported in `/plot`.

### Frontend (Required)
Add a Layer helper in the Plot section:
- A simple list input where student enters layer numbers and labels (manual list).
  - Example rows: `1 black`, `2 red`
- Clicking a row sets the layer number input automatically.
- “Next Layer” convenience button (optional).

### Review Point
Open `/`, plot layer 1, change pen, plot layer 2.

---

## Iteration 5 — Interactive Mode Polishing

### Goals
- Make interactive controls clearer and easier.

### Backend
No major changes required.

### Frontend (Required)
Improve Interactive section:
- Buttons: Pen Up, Pen Down
- Jog controls (simple): small step buttons for X/Y
- Command history (optional)
- Clear “Connected” indicator

### Review Point
Open `/`, jog plotter and control pen without typing commands.

---

## Iteration 6 — Export + Cleanup + Documentation

### Goals
- Make prototype student-ready.

### Tasks
- Export/download SVG
- Save/load sketch code (localStorage is fine)
- Basic README usage steps
- Minimal error messaging

### Review Point
A student can open the page, write code, export, and plot with minimal explanation.

---

## Development Rules

- **Simplicity first**: Code is kept simple and readable, assuming dependencies are properly installed.
- **Minimal error handling**: Only handle errors where meaningful (plotter connection failures, command execution errors).
- **No defensive checks**: Assume files exist, dependencies are installed, and the environment is correctly configured.
- Keep code flat and readable.
- Avoid abstractions.
- Prefer simple globals over architecture.
- No async complexity.
- No websockets.
- No databases.
- Serve UI as static files from Flask.

---

## Deferred Features

Only after core works:
- Software pause/resume
- Auto-detect layers from SVG
- Plot previews (pen-up paths)
- Resume plotting
