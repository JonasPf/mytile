#!/usr/bin/python
"""mytile

Usage:
  mytile tile
  mytile fullscreen
  mytile focus_next
  mytile focus_prev
  mytile (-h | --help)
  mytile --version

Options:
  -h --help             Show this screen.
  --version             Show version.

"""
from __future__ import print_function

import collections
import pprint
import json
import os
from docopt import docopt
from sarge import capture_stdout, run


"""
Development Information
=======================

TODO:
    - The order of the windows is messed up. Should sort them based on x/y top left to bottom right
    - Reaction time can be a bit slow after pressing a button. This is mainly because Python starts takes a while to start. Possible solutions would be:
        - Reduce imports and use optimize
        - Compile using nuitka
        - Make it a server running in the background and communicate via named pipes or tcp
    - Remember floating window position and make it possible to revert to them

Links:
    - http://blog.spiralofhope.com/1042/wmctrl-user-documentation.html
"""

PATH = os.path.expanduser("~") + '/.mytile.json'

Desktop = collections.namedtuple('Desktop', ['id', 'active', 'dimensions'])
Window = collections.namedtuple('Window', ['id', 'desktop', 'name', 'geometry'])
Geometry = collections.namedtuple('Geometry', ['x', 'y', 'w', 'h'])

def get_screen_size():
    """Returns the size of the screen.

    With multiple monitors it returns the size of the combined surfaces of the monitors.

    Returns:
        An instance of Gemoetry with x=0, y=0, w=Width of screen, h=Height of screen
    """        
    stdout = capture_stdout('wmctrl -d').stdout.text
    stdout_lines = stdout.split('\n')

    # Example string: '0  - DG: 1366x768  VP: N/A  WA: 0,31 1366x737  1'
    size = stdout_lines[0].split()[3]

    # Example string: '1366x768'
    sizes = size.split('x')

    width = int(sizes[0])
    height = int(sizes[1])

    return Geometry(0, 0, width, height)


def list_desktops():
    """Returns a list of all desktops.

    Returns:
        List of Dekstop instances.
    """
    stdout = capture_stdout('wmctrl -d').stdout.text
    stdout_lines = stdout.split('\n')

    result = []

    for line in stdout_lines:
        if line:
            columns = line.split()

            result.append(Desktop(
                id = int(columns[0]),
                active = (columns[1] == '*'),
                dimensions = columns[3]
                ))

    return result

def list_windows():
    """Returns a list of all windows.

    Returns:
        List of Window instances.
    """
    stdout = capture_stdout('wmctrl -lG').stdout.text
    stdout_lines = stdout.split('\n')

    result = []

    for line in stdout_lines:
        if line:
            columns = line.split()


            result.append(Window(
                id = columns[0],
                desktop = int(columns[1]),
                geometry = Geometry(x=int(columns[2]), y=int(columns[3]), w=int(columns[4]), h=int(columns[5])),
                name = ' '.join(columns[7:])
                ))

    return result

def find_active_desktop(desktops):
    """Returns the currently active desktop.

    Args:
        desktops: A list containing all Desktop instances.

    Returns:
        An instance of Desktop representing the currently active desktop or None if it can't be found.
    """
    for d in desktops:
        if d.active:
            return d

def find_active_window(windows):
    """Returns the currently active (focused) window.

    Args:
        windows: A list containing all Windows instances.

    Returns:
        An instance of Window representing the currently active window or None if it can't found.
    """
    stdout = capture_stdout('xdotool getactivewindow').stdout.text
    windows_id = '0x0' + hex(int(stdout))[2:]

    for w in windows:
        if w.id == windows_id:
            return w

def find_windows_in_desktop(windows, desktop):
    """Returns all windows in a given desktop.
    
    Args:
        windows: A list containing all Windows instances.
        desktop: An instance of Desktop.

    Returns:
        A list of Window instances. 
    """
    return [w for w in windows if w.desktop == desktop.id]

def focus_window(window):
    """Focus a specific window.

    Args:
        window: An instance of Window.
    """
    run('wmctrl -ia ' + window.id)

def move_window(window, geometry, config):
    """Move or resize a window to a different position.

    If the window is maximized, it will be unmaximized first. Maximized windows always
    take up the full screen.

    Args:
        window: An instance of Window.
        geometry: An instance of Geometry containing the new position and size 
                  of the window (incl. the decorations).
    """

    geometry = remove_window_decorations(geometry, config)

    # Unmaximize the window
    p = run('wmctrl -i -r {} -b "remove,maximized_vert,maximized_horz"'.format(window.id))

    # Change the geometry
    p = run('wmctrl -i -r {id} -e "0,{x},{y},{w},{h}"'.format(
        id = window.id,
        x = int(geometry.x),
        y = int(geometry.y),
        w = int(geometry.w),
        h = int(geometry.h)
        ))

def remove_window_decorations(geometry, config):
    """Removes the size of the window titlebar and border from a Geometry.

    When resizing/positioning a window it is important to leave space for 
    decorations (titlebar, border). This can be done using this function.

    Args:
        geometry: An instance of Geometry describing the gemoetry of a window
                  with its decorations.
        config: The config dictionary.

    Returns:
        A new instance of Geometry descibing the geometry of a window without
        its decorations.

    """
    border = config['border']
    titlebar = config['titlebar']
    vertical_thickness = border + titlebar
    horizontal_thickness = border * 2
 
    return Geometry(geometry.x, 
        geometry.y, 
        geometry.w - horizontal_thickness, 
        geometry.h - vertical_thickness)

def get_config(path):
    """
    Returns the configuration.

    Configuration is read from a json file. If the file is does not exist
    or if values are missing, defaults will be used.

    Example configuration file:

        {
            "border": 3, 
            "titlebar": 28,
            "tiling_areas": [
                {
                    "x": 0,
                    "y": 0,
                    "w": 2560,
                    "h": 1600
                },
                {
                    "x": 2560,
                    "y": 0,
                    "w": 1200,
                    "h": 1920
                }
            ]
        }

    Configuration options:

        - border: The size of the border of windows in pixels. Defaults to 0.
        - titlebar: The size of the titlebar of windows in pixels. Defaults
                    to 0.
        - tiling_areas: A list of dictionaries containing descriptions of
                        available tiling areas. A tiling area is a describes
                        an area in which windows can be tiled.
                        Defaults to the current screen size.

    Tiling areas:

        Tiling happens only for windows in the currently active tiling area.
        
        This allows for the following use cases:
        
        - Multi monitor setup: 
          Have one tiling area on each monitor. Without tiling areas the 
          windows would be tiled across the monitors (overlapping from one to
          the other).

        - Leave gaps on the sides for e.g. panels by configuring a tiling area
          which starts next to the panel. E.g. if there is a panel that occupies
          the top 30 pixels, the tiling area could be:
          {
                "x": 0,
                "y": 30,
                "w": 2560,
                "h": 1570    
          }

          Remember to remove the gap (30 pixels) from the height!

    Args:
        path: A string containing the file path

    Returns:
        A dictionary with all configuration values from the file plus defaults
        if something is missing.
    """
    data = {}

    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)

    # Defaults
    if 'border' not in data:
        data['border'] = 0

    if 'titlebar' not in data:
        data['titlebar'] = 0

    if 'tiling_areas' not in data:
        data['tiling_areas'] = []

    # Convert x,y,w,h to Geometry
    tmp = []
    for area in data['tiling_areas']:
        tmp.append(Geometry(x=area['x'], y=area['y'], w=area['w'], h=area['h']))
    data['tiling_areas'] = tmp

    # Use screen size if there are no tiling areas configured. With single monitor setups that's usually correct.
    if not data['tiling_areas']:
        data['tiling_areas'].append(get_screen_size())

    return data

def is_window_in_area(window, area):
    """
    Checks if a window is within an area.

    To determine whether a window is within an area it checks if the x and y of
    the window are within that area. This means a window can "hang out" of an
    area but still be considered to be in the area.

    Args:
        window: A Window instance
        area: A Geometry instance

    Returns:
        True or False
    """
    return window.geometry.x >= area.x and \
        window.geometry.y >= area.y and \
        window.geometry.x < area.x + area.w and \
        window.geometry.y < area.y + area.h


def tile(area, master_window, windows, config):
    """Tiles windows into an area.

    The area is split into two halfs. The master window will be moved to the
    left half of the area. The rest of the windows will share the right half
    of the area.

    Args:
        area: A Gemoetry instance.
        master_window: A Window instance that will take the 'master' position.
        windows: A list of Window instances to be tiled.
        config: The config dictionary.

    """
    half_width = area.w / 2

    geometry = Geometry(area.x, area.y, half_width, area.h)
    move_window(master_window, geometry, config)

    total_height = area.h
    slave_windows = (len(windows) - 1)
    window_height = total_height / slave_windows

    y = area.y
    for window in windows:
        if window != master_window:
            geometry = Geometry(area.x + half_width, y, half_width, window_height)
            move_window(window, geometry, config)
            y += window_height

def fullscreen(windows):
    """Maximizes windows.

    Args:
        windows: A list of window instances to be maximized.
    """
    for window in windows:
        run('wmctrl -i -r {} -b "add,maximized_vert,maximized_horz"'.format(window.id))

def find_tiling_area_for_window(window, config):
    """Returns the tiling area in which this window is located.

    Args:
        window: A window instance.
        config: The config dictionary

    Returns:
        An instance of Geometry describing the tiling area or None if no matching tiling area can be found.
    """

    for area in config['tiling_areas']:
        if is_window_in_area(window, area):
            return area

def find_windows_in_tiling_area(windows, area):
    """"Returns all windows in a tiling area.

    Args:
        windows: A list of window instances.
        area: A Gemoetry instance.

    Returns:
        A list with all windows in the given tiling area.
    """
    return [w for w in windows if is_window_in_area(w, area)]


def main():
    """Main entry point for the CLI tool """

    arguments = docopt(__doc__, version='1.0')

    config = get_config(PATH)
    desktops = list_desktops()
    windows = list_windows()
    active_desktop = find_active_desktop(desktops)
    active_window = find_active_window(windows)
    windows_in_active_desktop = find_windows_in_desktop(windows, active_desktop)
    active_window_index = windows_in_active_desktop.index(active_window)

    if arguments['focus_next']:
        next_window_index = active_window_index + 1
        if next_window_index >= len(windows_in_active_desktop):
            next_window_index = 0

        focus_window(windows_in_active_desktop[next_window_index])
    elif arguments['focus_prev']:
        previous_window_index = active_window_index - 1
        if previous_window_index < 0:
            previous_window_index = len(windows_in_active_desktop) - 1

        focus_window(windows_in_active_desktop[previous_window_index])
    else:
        active_tiling_area = find_tiling_area_for_window(active_window, config)

        if active_tiling_area:
            affected_windows = find_windows_in_tiling_area(windows_in_active_desktop, active_tiling_area)

            if arguments['tile']:
                # For some unkown reason there are sometimes gaps the first
                # time I call the function. Calling two time to avoid that
                tile(active_tiling_area, active_window, affected_windows, config)
                tile(active_tiling_area, active_window, affected_windows, config)
            elif arguments['fullscreen']:
                fullscreen(affected_windows)

        else:
            print("No active tiling area found. Check you configuration!")


if __name__ == '__main__':
    main()