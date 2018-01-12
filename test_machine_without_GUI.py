"""Virtual Machine for Testing without a GUI

This virtual machine is intended to be run from console, its purpose is to find
problems or incongruities between the use of GUI or console. After all, this
framework was originally intended to be run from console.


Eventually, this file wil be moved to examples.

For now, this virtual machine is only initialized and displays its attributes.
In Ilan Moyer's original Gestalt Framework, a virtual machine was executed
directly from console, but now it can be also executed from a GUI.

Copyright (c) 2018 Daniel Marquina
"""

import machines
import interfaces
from utilities import notice as notice
# import test_vn


class TestVirtualMachine(machines.VirtualMachine):
    def __init__(self, *args, **kwargs):
        super(TestVirtualMachine,
              self).__init__(*args, **kwargs,)
        self.publish_settings()

    def publish_settings(self):
        init_message = ''
        if self.use_gui:
            init_message += self.name
        init_message += '\n' + 'Settings:' + '\n'
        if self.name:
            init_message += "Name: " + self.name + '\n'
        if self.interface:
            init_message += "Provided interface: True" + '\n'
        else:
            init_message += "Provided interface: False" + '\n'
        if self.use_gui:
            init_message += "GUI: " + str(self.use_gui) + '\n'
        if self.persistenceFilename:
            init_message += "Persistence file: " + self.persistenceFilename + '\n'
        notice(self, init_message, self.use_gui)

    def init_interfaces(self):
        """Initializes an interface shell if it was not specified."""
        if not self.interface:
            self.interface = interfaces.InterfaceShell()


# If executing from console:
if __name__ == '__main__':
    TestVirtualMachine(name='Testing Machine',
                       persistenceFile='test.vmp',)