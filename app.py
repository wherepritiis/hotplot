#!/usr/bin/env python3
"""
Flask backend for AxiDraw plotter control.
Iteration 2: Plotting + Plot UI with SVG plotting, layer support, and settings.
"""

import threading
import signal
from flask import Flask, request, jsonify, send_from_directory
from pyaxidraw import axidraw

app = Flask(__name__, static_folder='static')

# Global AxiDraw instance (for interactive mode)
axidraw_instance = None
# Global plot instance (for plotting operations)
plot_instance = None
# Plot thread (minimal - just to track if plot is running)
plot_thread = None
# Paused SVG (for resume functionality)
paused_svg = None
# Flag to track if plot is active (for signal handler)
plot_active = False


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
    
    if axidraw_instance is None:
        return jsonify({"success": False, "error": "Not connected"}), 400
    
    try:
        # Disable motors before disconnecting to free them up
        try:
            # Send command to disable XY motors (EM,0,0 = Enable Motors, 0 = disable)
            axidraw_instance.usb_command("EM,0,0\r")
        except Exception as motor_error:
            # If motor disable fails, log but continue with disconnect
            print(f"Warning: Could not disable motors: {motor_error}")
        
        axidraw_instance.disconnect()
        axidraw_instance = None
        return jsonify({"success": True, "message": "Disconnected from AxiDraw"})
    except Exception as e:
        print(f"Error disconnecting from AxiDraw: {e}")
        # Ensure instance is cleared even on error
        axidraw_instance = None
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/cmd', methods=['POST'])
def cmd():
    """Execute a command on the AxiDraw plotter."""
    global axidraw_instance
    
    data = request.get_json()
    command = data['command'].strip()
    
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


def run_plot(svg, layer, pen_pos_up, pen_pos_down, speed_penup, speed_pendown):
    """Run plot in a background thread."""
    global axidraw_instance, plot_instance, paused_svg, plot_thread, plot_active
    
    try:
        # Disconnect any existing interactive session
        if axidraw_instance is not None:
            try:
                axidraw_instance.disconnect()
            except Exception as e:
                print(f"Warning: Error disconnecting interactive session: {e}")
            axidraw_instance = None
        
        # Clear any previous paused SVG
        paused_svg = None
        
        # Create new AxiDraw instance for plotting
        plot_instance = axidraw.AxiDraw()
        
        # Setup plot with SVG
        plot_instance.plot_setup(svg)
        
        # Set plot options
        if layer is not None:
            plot_instance.options.mode = "layers"
            plot_instance.options.layer = int(layer)
        else:
            plot_instance.options.mode = "plot"
        
        plot_instance.options.pen_pos_up = pen_pos_up
        plot_instance.options.pen_pos_down = pen_pos_down
        plot_instance.options.speed_penup = speed_penup
        plot_instance.options.speed_pendown = speed_pendown
        
        # Mark plot as active before starting
        plot_active = True
        
        # Execute plot with output=True to capture paused SVG if interrupted
        output_svg = plot_instance.plot_run(True)
        
        # Check error code to see if plot was paused
        error_code = plot_instance.errors.code
        if error_code == 102:  # Paused by button
            print("Plot paused by button press")
            paused_svg = output_svg
        elif error_code == 103:  # Paused by keyboard interrupt
            print("Plot paused by keyboard interrupt")
            paused_svg = output_svg
        elif error_code == 0:  # Completed normally
            print("Plot completed successfully")
            paused_svg = None
        
        # Clean up plot instance
        try:
            plot_instance.disconnect()
        except Exception as e:
            print(f"Warning: Error disconnecting after plot: {e}")
        plot_instance = None
        
    except Exception as e:
        print(f"Error in plot thread: {e}")
        # Clean up plot instance on error
        if plot_instance is not None:
            try:
                plot_instance.disconnect()
            except:
                pass
            plot_instance = None
        paused_svg = None
    finally:
        plot_active = False
        plot_thread = None


@app.route('/plot', methods=['POST'])
def plot():
    """Plot an SVG with optional layer selection and settings."""
    global plot_thread
    
    data = request.get_json()
    svg = data.get('svg', '').strip()
    
    if not svg:
        return jsonify({"success": False, "error": "SVG content is required"}), 400
    
    # Check if a plot is already in progress
    if plot_thread is not None and plot_thread.is_alive():
        return jsonify({"success": False, "error": "Plot operation already in progress"}), 400
    
    try:
        # Get parameters
        layer = data.get('layer')
        settings = data.get('settings', {})
        
        pen_pos_up = settings.get('pen_up', 70)
        pen_pos_down = settings.get('pen_down', 40)
        speed_penup = settings.get('speed_up', 75)
        speed_pendown = settings.get('speed_down', 25)
        
        # Start plot in background thread
        plot_thread = threading.Thread(
            target=run_plot,
            args=(svg, layer, pen_pos_up, pen_pos_down, speed_penup, speed_pendown),
            daemon=True
        )
        plot_thread.start()
        
        return jsonify({"success": True, "message": "Plot started successfully"})
        
    except Exception as e:
        print(f"Error starting plot: {e}")
        plot_thread = None
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/stop', methods=['POST'])
def stop():
    """Stop current plot operation by disconnecting (which interrupts plot_run())."""
    global plot_instance, plot_thread
    
    if plot_instance is None and (plot_thread is None or not plot_thread.is_alive()):
        return jsonify({"success": False, "error": "No plot operation in progress"}), 400
    
    try:
        # Disconnect the plot instance - this will interrupt plot_run()
        # pyaxidraw's keyboard_pause mechanism should handle this gracefully
        if plot_instance is not None:
            try:
                plot_instance.disconnect()
                print("Disconnected plot instance to stop plot")
            except Exception as e:
                print(f"Warning: Error disconnecting during stop: {e}")
            plot_instance = None
        
        plot_thread = None
        return jsonify({"success": True, "message": "Plot stopped successfully"})
    except Exception as e:
        print(f"Error stopping plot: {e}")
        plot_instance = None
        plot_thread = None
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/home', methods=['POST'])
def home():
    """Return plotter to home position using res_home mode if plot was paused, otherwise use interactive mode."""
    global axidraw_instance, plot_instance, paused_svg, plot_thread
    
    try:
        # If there's a paused plot, use res_home mode
        if paused_svg is not None:
            # Disconnect any existing instances
            if axidraw_instance is not None:
                try:
                    axidraw_instance.disconnect()
                except Exception as e:
                    print(f"Warning: Error disconnecting interactive session: {e}")
                axidraw_instance = None
            
            if plot_instance is not None:
                try:
                    plot_instance.disconnect()
                except Exception as e:
                    print(f"Warning: Error disconnecting plot session: {e}")
                plot_instance = None
            
            # Use res_home mode with paused SVG
            home_instance = axidraw.AxiDraw()
            home_instance.plot_setup(paused_svg)
            home_instance.options.mode = "res_home"
            home_instance.plot_run()
            home_instance.disconnect()
            
            return jsonify({"success": True, "message": "Returned to home position (from paused plot)"})
        
        # Otherwise, use interactive mode
        # Disconnect any existing instances
        if axidraw_instance is not None:
            try:
                axidraw_instance.disconnect()
            except Exception as e:
                print(f"Warning: Error disconnecting interactive session: {e}")
            axidraw_instance = None
        
        if plot_instance is not None:
            try:
                plot_instance.disconnect()
            except Exception as e:
                print(f"Warning: Error disconnecting plot session: {e}")
            plot_instance = None
        
        plot_thread = None
        
        # Create new interactive instance for home command
        home_instance = axidraw.AxiDraw()
        home_instance.interactive()
        home_instance.connect()
        
        # Move to home position
        home_instance.moveto(0, 0)
        
        # Disconnect
        home_instance.disconnect()
        
        return jsonify({"success": True, "message": "Returned to home position"})
        
    except Exception as e:
        print(f"Error returning to home: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def signal_handler(signum, frame):
    """Handle SIGINT (Ctrl+C) to stop active plot."""
    global plot_instance, plot_active
    if plot_active and plot_instance is not None:
        print("Interrupting plot via Ctrl+C...")
        try:
            plot_instance.disconnect()
        except:
            pass
        plot_instance = None
        plot_active = False


if __name__ == '__main__':
    # Register signal handler in main thread for Ctrl+C support
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Flask server on http://localhost:3000/")
    app.run(host='127.0.0.1', port=3000, debug=True)
