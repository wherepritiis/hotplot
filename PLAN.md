# Implementation Plan

Goal: Build a minimal, working plotting tool first. Refine later.

Constraint: **At the end of every iteration, there must be a testable UI in the browser** (served at `/`) so the reviewer does not need curl/Postman.

We will implement a simple single-page “Control Panel” UI early and expand it iteratively. No build tools, no React, no bundlers.

---

## Prerequisites

### Python Version

**Python 3.14 is required.** All Python commands must use `python3.14` explicitly to ensure the correct version is used.

### Installing PyAXIDraw

PyAXIDraw is **not available via pip or npm**. It must be installed manually:

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

### Installing Other Dependencies

Install Flask and other pip-installable dependencies:
```bash
python3.14 -m pip install -r requirements.txt
```

**Important**: Always use `python3.14` (not `python`, `python3`, or `python3.13`) for all commands to ensure version consistency.

---

## Iteration 1 — Minimal Server + Basic Control Panel UI

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

## Iteration 2 — Plotting + Plot UI

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
- SVG translate offset wrapper
- Basic settings: pen up/down, speed up/down
- Layer plotting via AxiDraw options: `mode="layers"` and `layer=N`

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
