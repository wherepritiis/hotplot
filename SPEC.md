# Pen Plotter Web Tool — Specification

## Overview

This project is a local, single-user web application for creating SVG drawings and plotting them on an AxiDraw-compatible pen plotter.

The system consists of:

- A Python backend (Flask)
- A browser-based JavaScript UI
- p5.js for creative coding
- p5.plotSvg for generating plotter-compatible SVG
- PyAXIDraw for communicating with the physical plotter

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

Default p5.plotSvg behavior (96 DPI, inches internally) is accepted as-is.

Students are responsible for canvas sizing.

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

Students create groups such as:

beginSvgGroup("1 black")
...
endSvgGroup()

Rules:

- Group names MUST begin with a numeric prefix (1, 2, 3, etc).
- Everything after the number is arbitrary.

Backend plotting uses:

ad.options.mode = "layers"
ad.options.layer = N

Only that numbered layer is plotted.

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
- **PyAXIDraw**: **Not available via pip or npm**. Must be installed manually from a zip file downloaded from the AxiDraw website. See installation instructions in PLAN.md and the [AxiDraw Python API documentation](https://axidraw.com/doc/py_api).

---

## Backend API

POST /connect
POST /disconnect
POST /cmd
POST /plot
POST /stop
POST /home

---

## Pause / Resume

Not implemented initially.

Physical plotter pause button is used.

---

## Frontend

- Code editor (CodeMirror)
- Canvas preview (p5.js)
- Plot modal with settings
- Interactive console

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
