# HotPlot - AxiDraw Plotter Web Control Tool

A small tool for controlling an AxiDraw plotter from a web UI. This tool allows anyone to write p5.js sketches, preview them, export SVG, and plot directly to an AxiDraw-compatible pen plotter.

## Overview

HotPlot provides a simple web-based interface for:
- Writing JavaScript (p5.js) sketches in a browser editor
- Previewing sketches visually on a canvas
- Exporting plotter-ready SVG via p5.plotSvg
- Sending SVG directly to the plotter
- Interactively jogging and controlling the plotter
- Plotting SVG layers individually for multi-pen workflows

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

#### Option A: Install from URL (Recommended)

```bash
python3.14 -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
```

#### Option B: Manual Installation

1. Download the AxiDraw API zip file:
   - Direct link: https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
   - Or visit the [AxiDraw Python API documentation](https://axidraw.com/doc/py_api) for the latest download link

2. Unzip the archive:
   ```bash
   unzip AxiDraw_API.zip
   cd AxiDraw_API
   ```

3. Install using Python 3.14:
   ```bash
   python3.14 -m pip install .
   ```

4. Verify installation:
   ```bash
   python3.14 -c "from pyaxidraw import axidraw; print('PyAXIDraw installed successfully')"
   ```

### Step 2: Install Python Dependencies

Install Flask and other pip-installable dependencies:

```bash
python3.14 -m pip install -r requirements.txt
```

This will install:
- Flask (>=3.0.0)

### Step 3: Install JavaScript Dependencies

Install frontend JavaScript packages via npm:

```bash
npm install
npm run copy-deps
```

This will install:
- p5.js (v1.11.11)
- p5.plotSvg (v0.1.8)
- CodeMirror (v5.65.20)

The `copy-deps` script copies the necessary files to `static/vendor/` so Flask can serve them.

**Note**: If you don't have npm installed, download Node.js from [nodejs.org](https://nodejs.org/).

### Step 4: Verify Installation

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

### Basic Control Panel (Iteration 1)

The current implementation provides a basic control panel with:

1. **Connection Controls**
   - Click "Connect" to establish a connection to your AxiDraw plotter
   - Click "Disconnect" to close the connection
   - The status indicator shows whether you're connected (green) or disconnected (red)

2. **Command Execution**
   - Enter commands in the command input field
   - Supported commands:
     - `moveto x y` - Move to absolute position (x, y) with pen up
     - `lineto x y` - Draw a line to absolute position (x, y) with pen down
     - `penup` - Raise the pen
     - `pendown` - Lower the pen
     - `home` - Move to home position (0, 0)
   - Click "Send" or press Enter to execute the command
   - All responses and errors are logged in the log area

### Example Commands

```
moveto 1 1
pendown
lineto 2 2
penup
home
```

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

### JavaScript Dependencies Not Found

If you see errors about missing JavaScript libraries:

1. Ensure npm is installed: `npm --version`
2. Run `npm install` to install dependencies
3. Run `npm run copy-deps` to copy files to `static/vendor/`
4. Verify files exist in `static/vendor/`:
   - `static/vendor/p5.js`
   - `static/vendor/p5.plotSvg.js`
   - `static/vendor/codemirror/codemirror.js`
   - `static/vendor/codemirror/codemirror.css`
   - `static/vendor/codemirror/mode/javascript/javascript.js`

## Project Structure

```
hotplot/
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies (pip-installable)
├── package.json        # JavaScript dependencies (npm-installable)
├── SPEC.md             # Project specification
├── PLAN.md             # Implementation plan
├── README.md           # This file
└── static/
    ├── index.html      # Web UI
    └── vendor/         # JavaScript libraries (copied from node_modules)
```

## Development

### Current Status

**Iteration 1** ✅ Complete:
- ✅ Flask server with basic endpoints
- ✅ Connect/disconnect functionality
- ✅ Command execution interface
- ✅ Web UI for testing

**Iteration 2** ✅ Complete:
- ✅ Plot endpoint with SVG support
- ✅ Stop and Home endpoints
- ✅ Plot UI with SVG input, layer selection, offset, and settings
- ✅ SVG offset wrapping implementation
- ✅ Layer plotting support

### Future Iterations

See `PLAN.md` for details on upcoming features:
- Iteration 3: Editor + Preview + SVG Export UI
- Iteration 4: Layer Workflow UI
- Iteration 5: Interactive Mode Polishing
- Iteration 6: Export + Cleanup + Documentation

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

See project documentation for license information.
