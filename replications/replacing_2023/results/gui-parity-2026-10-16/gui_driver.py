"""Drive the original Tk menu and Play button without modifying model rules."""
import json
from pathlib import Path
import runpy
import sys

engine = Path(sys.argv[1]).resolve()
config = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(engine))
import gui

class AutomatedGUI(gui.GUI):
    def configureWindow(self):
        super().configureWindow()
        self.window.after(1000, self.start_from_widgets)

    def start_from_widgets(self):
        menu = self.widgets['agentColorMenu']
        assert menu.entrycget(1, 'label') == 'Disease'
        menu.invoke(1)
        assert self.activeColorOptions['agent'] == 'Disease'
        assert self.sugarscape.timestep == 0
        assert self.sugarscape.run is False
        (config.parent / 'gui-action.json').write_text(json.dumps({
            'timestep': self.sugarscape.timestep,
            'color': self.activeColorOptions['agent'],
            'action': 'Original Disease menu invocation followed by original Play button invocation',
            'window_exists': self.window.winfo_exists(),
            'canvas_items': len(self.canvas.find_all()),
        }, indent=2) + '\n')
        self.widgets['playButton'].invoke()

gui.GUI = AutomatedGUI
sys.argv = [str(engine / 'sugarscape.py'), '--conf', str(config)]
runpy.run_path(str(engine / 'sugarscape.py'), run_name='__main__')
