# MyTile

A simple python script to easily arrange windows. I use it together with XFCE4/XFWM to create a semi-tiling window manager experience. It might work with other WMs/DEs but I haven't tested it.

It provides the following functionalities:

- Arrange windows in master/slave fashion
- Maximize all windows
- Focus next window
- Focus previous window
- Multi-monitor support through tiling areas (see below)

_Warning_: This is not production ready software. It will likely change and break in the future and it has some pretty rough edges. I recommend it only to people who know what they are doing.

## Similar software

Some alternatives I found:

- http://www.giuspen.com/x-tile
- https://github.com/TheWanderer/stiler
- https://github.com/BurntSushi/pytyle1
- https://github.com/BurntSushi/pytyle3
- http://wumwum.sourceforge.net

A few more can be found here:
- http://www.liquisearch.com/tiling_window_manager/prominent_tiling_window_managers/third_party_tiling_applications_on_xorg

## Installation

Make sure the following commands are available on your system:

- wmctrl
- xdotool

After that install as follows:

```
git clone https://github.com/JonasPf/mytile
cd mytile
python setup.py install
```

## How to setup MyTile with XFCE4/XFWM

This is my personal configuration which is similar to the default XMonad configuration. You will likely want to do things somewhat different according to your own preferences.

### Setting up keyboard shortcuts

1. Run *xfce4-keyboard-settings*.
2. Click on *Application Shortcuts*.
3. Click *Add* to add new shortcuts.

I use the following shortcuts:

- Super+J maps to *mytile focus_next* which focuses the next window.
- Super+K maps to *mytile focus_prev* which focuses the previous window.
- Super+Space maps to *mytile fullscreen* which maximizes all windows.
- Super+Return maps to *mytile tile* which arranges the windows so that the currently focused window takes up the left half of the screen and all other windows take up the rest of the screen. Pressing the shortcut again while focusing a different window will switch that window with the window on the left.

In addition to the MyTile shortcuts I use the following shortcuts frequently:

- Shift+Super+Return maps to *xfce4-terminal* which opens a new terminal.
- Super+D maps to *xfce4-popup-whiskermenu* which allows me to start applications. For this to work, the whiskermenu needs to be added to the panel .

### Tweaking XFWM

1. Run *xfwm4-tweaks-settings*.
2. Under *Cycling* select *Cycle through windows on all workspaces*. This allows me to use ALT+Tab if I every get lost and need to quickly find a specific window.
3. Under *Focus* select *Switch to window's workspace*. This is mainly my own preference.
4. Under *Accesibility* set the *Key used to grap and move windows* to *Super*. This allows me to hold Super and move windows by dragging with the left mousebutton as well as resizing them with the right mousebutton. I use this very often to arrange windows myself, when I need a bit more freedom to arrange windows the way I want.
5. Under *Compositor* deselect *Show shadows under regular windows*. This looks better when windows are arranged next to each other without gap.

### Installing theme

I created a very simple XFWM4 theme. All it does is to display a two pixel border around each window. No titlebar or other decorations. It works very well with MyTile and saves valuable screen space.

To install it copy the directory *supersimple* to *~/themes/*. Use the *-P* parameter to preserve links (since everything is just a 2 pixel image, the theme consists of only two images. The rest are just links to those two images).

```
cp -Pr supersimple/ ~/.themes/
```

### Configuring XFWM

1. Run *xfwm4-settings*
2. Under *Style* select the theme *supersimple*.
3. Under keyboard, configure the following shortcuts:
	- Shift+Super+C maps to *Close window*
	- Alt+Tab maps to *Cycle windows*. This allows me to find a window quickly.
	- Repeat for every workspace:
		* Super+1 maps to *Workspace 1*. This allows me to quickly switch workspaces.
		* Shift+Super+! (that is the 1 key with shift pressed at the same time) maps to *Move window to workspace 1*.
4. Under *Focus* select *Click to focus*. Unfortunatly *Focus follows mouse* would interfere with the *mytile focus_next/prev* commands.

### Configuring MyTile

Create the file *~/.mytile.json* with the following content:

```
{
	"border": 2,
	"titlebar": 2
}
```

This tells MyTile that the window decorations are 2 pixels wide on each side. These settings work with the supersimple theme. If you use a different theme you may need to adjust them.

## How to deal with panels and docks

MyTile by default will use the whole screen to arrange windows. As a result they will overlap panels. To avoid this, MyTile has the concept of tiling areas. A tiling area is a specific area on the screen in which window tiling takes place.

Tiling areas can be configured in the file *~/.mytile.json* as follows:

```
{
	"border": 2, 
	"titlebar": 2,
	"tiling_areas": [
		{
			"x": 0,
			"y": 0,
			"w": 2560,
			"h": 1600
		}
	]
}
```

If you have a panel on the top that is 32 pixel high and a screen resolution of 2560x1600 your configuration could look like this:


```
{
	"border": 2, 
	"titlebar": 2,
	"tiling_areas": [
		{
			"x": 0,
			"y": 32,
			"w": 2560,
			"h": 1536
		}
	]
}
```

The downside is that windows outside of the tiling area will be ignored by MyTile. If you move a window manually so that its top/left corner is outside of a tiling area, the window will be ignored. I'm open for suggestions on how to solve this use-case in a better (but simple) way.

## How to use MyTile with multiple monitors

As described in [above](#how-to-deal-with-panels-and-docks) MyTile just uses the whole screen to arrange windows. When using multiple monitors this means windows get arranged across monitors. I.e. one half of a window could be on one monitor and the other half on the other monitor. We can use tiling areas to avoid this. Just configure a tiling area for each monitor and it will arrange windows independently of the other monitor.

```
{
	"border": 2, 
	"titlebar": 2,
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
```


## Development Information

### Links

- http://blog.spiralofhope.com/1042/wmctrl-user-documentation.html

### Todo / Roadmap

- The order of the windows is messed up. Should sort them based on x/y top left to bottom right
- Reaction time can be a bit slow after pressing a button. This is mainly because Python takes a while to start. Possible solutions would be:
  - Reduce imports and use optimize
  - Compile using nuitka
  - Make it a server running in the background and communicate via named pipes or tcp
- Remember floating window position and make it possible to revert to them
- Instead of configuring the window border/titlebar it would be nice if they could be determined automatically. 
