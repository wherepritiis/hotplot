#!/usr/bin/env python3
"""
Flask backend for AxiDraw plotter control.
Iteration 1: Minimal server with connect/disconnect and command execution.
"""

import threading
from flask import Flask, request, jsonify, send_from_directory
from pyaxidraw import axidraw

app = Flask(__name__, static_folder='static')

# Global AxiDraw instance
axidraw_instance = None
hardware_lock = threading.Lock()


def get_state():
    """Get current connection state."""
    if axidraw_instance is None:
        return {"connected": False}
    return {"connected": True}


@app.route('/')
def index():
    """Serve the main UI page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/state', methods=['GET'])
def state():
    """Get the current connection state."""
    return jsonify(get_state())


@app.route('/connect', methods=['POST'])
def connect():
    """Connect to the AxiDraw plotter."""
    global axidraw_instance
    
    with hardware_lock:
        if axidraw_instance is not None:
            return jsonify({"success": False, "error": "Already connected"}), 400
        
        try:
            axidraw_instance = axidraw.AxiDraw()
            axidraw_instance.interactive()
            axidraw_instance.connect()
            return jsonify({"success": True, "message": "Connected to AxiDraw"})
        except Exception as e:
            print(f"Error connecting to AxiDraw: {e}")
            axidraw_instance = None
            return jsonify({"success": False, "error": str(e)}), 500


@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Disconnect from the AxiDraw plotter."""
    global axidraw_instance
    
    with hardware_lock:
        if axidraw_instance is None:
            return jsonify({"success": False, "error": "Not connected"}), 400
        
        try:
            axidraw_instance.disconnect()
            axidraw_instance = None
            return jsonify({"success": True, "message": "Disconnected from AxiDraw"})
        except Exception as e:
            print(f"Error disconnecting from AxiDraw: {e}")
            return jsonify({"success": False, "error": str(e)}), 500


@app.route('/cmd', methods=['POST'])
def cmd():
    """Execute a command on the AxiDraw plotter."""
    global axidraw_instance
    
    data = request.get_json()
    command = data['command'].strip()
    
    with hardware_lock:
        if axidraw_instance is None:
            return jsonify({"success": False, "error": "Not connected. Connect first."}), 400
        
        try:
            parts = command.split()
            cmd_name = parts[0].lower()
            
            if cmd_name == 'moveto':
                x = float(parts[1])
                y = float(parts[2])
                axidraw_instance.moveto(x, y)
                return jsonify({"success": True, "message": f"moved to ({x}, {y})"})
            
            elif cmd_name == 'lineto':
                x = float(parts[1])
                y = float(parts[2])
                axidraw_instance.lineto(x, y)
                return jsonify({"success": True, "message": f"drew line to ({x}, {y})"})
            
            elif cmd_name == 'penup':
                axidraw_instance.penup()
                return jsonify({"success": True, "message": "pen up"})
            
            elif cmd_name == 'pendown':
                axidraw_instance.pendown()
                return jsonify({"success": True, "message": "pen down"})
            
            elif cmd_name == 'home':
                axidraw_instance.goto(0, 0)
                return jsonify({"success": True, "message": "moved to home (0, 0)"})
            
            else:
                return jsonify({"success": False, "error": f"Unknown command: {cmd_name}"}), 400
                
        except Exception as e:
            print(f"Error executing command '{command}': {e}")
            return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask server on http://localhost:3000/")
    app.run(host='127.0.0.1', port=3000, debug=True)
