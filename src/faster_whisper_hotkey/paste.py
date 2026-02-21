import os
import time
import shutil
import subprocess
import logging

from pynput import keyboard

from . import terminal

logger = logging.getLogger(__name__)

keyboard_controller = keyboard.Controller()


def paste_x11(is_terminal: bool):
    """
    Send the paste shortcut on X11.
    """
    time.sleep(0.05)  # give clipboard time to settle
    if is_terminal:
        # Ctrl+Shift+V
        keyboard_controller.press(keyboard.Key.ctrl_l)
        keyboard_controller.press(keyboard.Key.shift)
        keyboard_controller.press("v")
        time.sleep(0.01)
        keyboard_controller.release("v")
        keyboard_controller.release(keyboard.Key.shift)
        keyboard_controller.release(keyboard.Key.ctrl_l)
    else:
        # Ctrl+V
        keyboard_controller.press(keyboard.Key.ctrl_l)
        keyboard_controller.press("v")
        time.sleep(0.01)
        keyboard_controller.release("v")
        keyboard_controller.release(keyboard.Key.ctrl_l)

def paste_wayland(is_terminal: bool):
    try:
        wtype_path = shutil.which("wtype")
        if not wtype_path:
            raise Warning("wtype not found - cannot auto-paste on Wayland.")
        modifiers = ["ctrl", "shift"] if is_terminal else ["ctrl"]
        def flat(nested):
            return [item for sublist in nested for item in sublist]
        command = [wtype_path,
            *flat([["-M", modifier] for modifier in modifiers]),
            "v",
            *flat([["-m", modifier] for modifier in reversed(modifiers)])
        ]
        subprocess.run(
            command,
            check=True,
            capture_output=True
        )
    except Exception as e:
        if isinstance(e, subprocess.CalledProcessError):
            logger.error(
                f"Auto-paste failed on Wayland (exit code={e.returncode}); stderr={e.stderr.strip().decode(errors='replace')}"
            )
        elif isinstance(e, Warning):
            logger.warning(*e.args)
        logger.warning("Falling back to X11...")
        paste_x11(is_terminal)

def paste_to_active_window():
    """
    Detect the focused window and issue the appropriate paste shortcut.
    """
    if os.getenv("WAYLAND_DISPLAY"):
        container = terminal.get_focused_container_wayland()
        is_terminal = terminal.is_terminal_window_wayland(container)
        paste_wayland(is_terminal)
    else:
        classes = terminal.get_active_window_class_x11()
        is_terminal = terminal.is_terminal_window_x11(classes)
        paste_x11(is_terminal)
