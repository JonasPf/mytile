# MyTile

A simple python script to easily tile windows. I use it together with XFCE4/XFWM.

## Installation

```
python setup.py install
```

The idea is to bind keyboard shortcuts to the individual commands.

## Usage

```
mytile tile
mytile fullscreen
mytile focus_next
mytile focus_prev
mytile (-h | --help)
mytile --version
```

## Command description

- _mytile tile_ will arange the currently focused window on the left half of the screen and every other window on the right.
- _mytile fullscreen_ will maximize all windows.
- _mytile focus_next_ will focus the next window.
- _mytile focus_prev_ will focus the previous window.

## Development Information

### Links

- http://blog.spiralofhope.com/1042/wmctrl-user-documentation.html

### Todo

- The order of the windows is messed up. Should sort them based on x/y top left to bottom right
- Reaction time can be a bit slow after pressing a button. This is mainly because Python starts takes a while to start. Possible solutions would be:
  - Reduce imports and use optimize
  - Compile using nuitka
  - Make it a server running in the background and communicate via named pipes or tcp
- Remember floating window position and make it possible to revert to them
- Write a lot more documentation and show use cases
