# HotPlot - AxiDraw Plotter Web Control Tool

A small tool for controlling an AxiDraw plotter from a web UI. This tool allows anyone to write p5.js sketches, preview them, copy/export as SVG, and plot directly using a pen plotter.

## Overview

HotPlot provides a simple web-based interface for:
- Writing JavaScript (p5.js) sketches in a browser editor
- Previewing sketches visually on a canvas
- Exporting plotter-ready SVG via p5.plotSvg
- Sending SVG directly to the plotter
- Plotting SVG layers individually for multi-pen workflows
- Interactively jogging and commanding the plotter


## Prerequisites

### Python 3.14

**Python 3.14 is required.** This project uses Python 3.14 specifically, and all commands must use `python3.14` explicitly to ensure version consistency.

To check your Python version:
```bash
python3.14 --version
```

If Python 3.14 is not installed, download it from [python.org](https://www.python.org/downloads/).

### AxiDraw Hardware

This tool requires an AxiDraw-compatible pen plotter connected via USB.

## Installation

### Step 1: Install PyAXIDraw

**Important**: PyAXIDraw is **not available via pip or npm**. It must be installed manually from a zip file.

#### Install from URL (Recommended)

```bash
python3.14 -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
```

### Step 2: Install Python Dependencies

Install Flask and other pip-installable dependencies:

```bash
python3.14 -m pip install -r requirements.txt
```

This will install:
- Flask (>=3.0.0)

### Step 3: Verify Installation

Verify that all dependencies are installed correctly:

```bash
python3.14 -c "import flask; from pyaxidraw import axidraw; print('All dependencies installed successfully')"
```

## Running the Server

Start the Flask server using Python 3.14:

```bash
python3.14 app.py
```

The server will start on `http://localhost:3000/`

Open your web browser and navigate to:
```
http://localhost:3000/
```

## Usage

### Connection and status

Click the **logo** to connect or disconnect the AxiDraw. The logo reflects connection status.

### Interactive mode (commands)

When connected, switch to **Interactive** mode to jog and command the plotter:

- Enter commands in the REPL environment (e.g. `moveto 1 1`, `lineto 2 2`, `penup`, `pendown`, `home`)
- Examples of supported commands:
  - `moveto x y` - Move to (x, y) with pen up
  - `lineto x y` - Draw to (x, y) with pen down
  - `penup` - Raise the pen
  - `pendown` - Lower the pen
  - `home` - Move to home (0, 0)
- Press Send to run the command; responses and errors appear in the log area


## Troubleshooting

### PyAXIDraw Not Found

If you see an error message about PyAXIDraw not being available:

1. Verify PyAXIDraw is installed:
   ```bash
   python3.14 -c "from pyaxidraw import axidraw"
   ```

2. If it fails, reinstall PyAXIDraw following Step 1 above.

3. Make sure you're using `python3.14` (not `python`, `python3`, or `python3.13`)

### Wrong Python Version

If you see a warning about Python version:

- Ensure you're using Python 3.14
- Check version: `python3.14 --version`
- Always use `python3.14` explicitly in all commands

### Connection Issues

If you cannot connect to the AxiDraw:

1. Ensure the AxiDraw is powered on and connected via USB
2. Check that no other application is using the plotter
3. Try disconnecting and reconnecting the USB cable
4. Restart the Flask server

### Port Already in Use

If port 3000 is already in use:

1. Stop any other applications using port 3000
2. Or modify `app.py` to use a different port:
   ```python
   app.run(host='127.0.0.1', port=3001, debug=True)
   ```

## Project Structure

```
hotplot/
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies (pip-installable)
├── SPEC.md             # Project specification
├── README.md           # This file
└── static/
    ├── index.html      # Web UI
    └── vendor/         # JavaScript libraries (p5.js, p5.plotSvg, CodeMirror; included in repo)
```

## Features

- **Connection**: Click the logo to connect or disconnect; the logo shows connection status
- **Interactive commands**: Command plotter via REPL environment
- **Plot**: Paste and send SVG to plotter
- **Layer selection**: Plot all layers or one or more selected layers (dropdown); layers discovered from SVG (e.g. p5 `beginSvgGroup("N name")`)
- **Pause / Resume / Home**: Pause a plot, resume, or return carriage to home
- **Code editor**: CodeMirror-based p5.js editor
- **Preview**: Run sketch in iframe and see canvas output
- **Plot from editor**: Generate SVG from sketch and send to plotter
- **Export**: Download SVG or copy SVG to clipboard


## Important Notes

- **Always use `python3.14`** for all Python commands (not `python`, `python3`, or other versions)
- This tool is designed for **localhost only** - no authentication or remote access
- **Single user, single plotter** - not designed for multi-user or multi-device scenarios
- All errors are printed to the Python console/terminal

## Resources

- [AxiDraw Python API Documentation](https://axidraw.com/doc/py_api)
- [AxiDraw Official Website](https://axidraw.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

This project is licensed under **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0): you may share and adapt the work for **non-commercial** use with attribution and under the same license. See [LICENSE](LICENSE) for details.

Third-party components (p5.js, p5.plotSvg, Flask, pyaxidraw, etc.) have their own licenses; see their respective documentation.
