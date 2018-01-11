"""Gestalt framework for Python 3's GUI

This module extends Gestalt Framework for Python 3's usability by creating a
GUI that allows the user to select a defined virtual machine, available
interface and test communication status.

Copyright (c) 2018 Daniel Marquina
"""

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
import serial
import shutil
import glob
import sys
import pyclbr
import importlib
import os

import inspect

kivy.require('1.0.1')


class Py3GestaltGUIApp(App):
    """Gestalt framework for Python 3's GUI application class.

    Builds a Py3GestaltGUI object. Visual settings are located in 'gui.kv'.
    """
    title = StringProperty("Gestalt Framework for Python 3")

    def build(self):
        """Overrides default build method.

        Returns:
            Py3GestaltGUI: Kivy's box layout, main widget of this app.
        """
        self.load_kv('gui.kv')
        return Py3GestaltGUI()


class Py3GestaltGUI(BoxLayout):
    """ Gestalt framework for Python 3's GUI's main layout class.

    This layout contains 4 sections:
        - Virtual machine selection,
        - Interface selection,
        - Machine recognition,
        - Debugger output.

    Attributes:
        vm_bt_search (Button): Virtual machine section's 'Search' button.
        vm_bt_import (Button): Virtual machine section's 'Import' button.
        vm_fb (VirtualMachineBrowser): Virtual machine section's file browser.
        vm_source_file (str): Virtual machine's definition file's direction.
        vm_class (class): User defined virtual machine class.
        vm(vm_class): Instantiation of user defined virtual machine.
        inf_sp (Spinner): Interface section's spinner.
        inf_bt_connect (Button): Interface section's 'Connect' button.
        debugger_lb (Label): Debugger output.
    """
    vm_bt_search = ObjectProperty(Button())
    vm_bt_import = ObjectProperty(Button())
    inf_sp = ObjectProperty(Spinner())
    inf_bt_connect = ObjectProperty(Button())
    debugger_lb = ObjectProperty(Label())

    def __init__(self):
        super(Py3GestaltGUI, self).__init__()
        self.vm_fb = VirtualMachineBrowser()
        self.vm_source_file = None
        self.vm_class = None
        self.vm = None
        self.import_counter = 0

    def open_file_browser(self):
        """Open a file browser including a reference to this GUI."""
        self.vm_fb.open(self)

    def import_virtual_machine(self):
        """Import virtual machine definition.

        Makes a copy of the user's virtual machine into a folder called 'tmp',
        imports it as a module inside a package and creates a reference to
        its user-defined virtual machine class.

        Returns:
            None if virtual machine is ill defined.
        """
        self.import_counter += 1

        vm_module = self.create_vm_module()

        if self.is_vm_ill_defined(vm_module):
            self.inf_bt_connect.disabled = True
            return

        vm_imported_module = importlib.import_module(vm_module)
        for name in dir(vm_imported_module):
            cls = getattr(vm_imported_module, name)
            if inspect.isclass(cls):
                if str(cls.__bases__[0]) == "<class 'machines.VirtualMachine'>":
                    self.vm_class = cls

        with open(self.vm_source_file, 'r') as vm_definition:
            self.write_debugger(vm_definition.read())

        self.vm_bt_search.disabled = True
        self.vm_bt_import.disabled = True
        self.inf_bt_connect.disabled = False

    def create_vm_module(self):
        """Create user-defined virtual machine module.

        Makes a temporal package (directory with an '__init__.py' file) called
        'tmp' with a temporal module (file) which is a copy of the user-defined
        virtual machine.
        They are assessed as 'temporal' because they are deleted every time an
        import action is attempted.

        Note:
        The module's name is 'temp_virtual_machine_X.py', where 'X' is the
        number of import attempts. Such change of name is necessary in order
        to avoid problems next, when analyzing module's classes using 'pyclbr'.

        Returns:
            module: Temporal module's name.
        """
        package = 'tmp'
        if os.path.exists(package):
            shutil.rmtree(package, ignore_errors=True)
        os.makedirs(package)
        open(os.path.join(package, '__init__.py'), 'w').close()

        module_name = 'temp_virtual_machine_' + str(self.import_counter)
        module_location = os.path.join(package, module_name + '.py')
        open(module_location, 'w').close()
        shutil.copyfile(self.vm_source_file, module_location)
        module = package + '.' + module_name

        return module

    def is_vm_ill_defined(self, vm_module):
        """Check whether a virtual machine is well or ill defined.

        Makes sure that selected virtual machine contains one and only one
        user-defined virtual machine class, child of py3Gestalt's
        'machines.VirtualMachine' class.

        Args:
            vm_module: Virtual Machine module to be analyzed

        Returns:
            True when selected module contains none or more than a unique
            virtual machine. False otherwise.
        """
        num_of_vm_cls = 0
        for name, class_data in sorted(pyclbr.readmodule(vm_module).items(),
                                       key=lambda x: x[1].lineno):
            if class_data.super[0] == 'machines.VirtualMachine':
                num_of_vm_cls += 1

        if num_of_vm_cls == 0:
            self.write_debugger("Error: No virtual machine defined." + '\n' +
                                "Select a new file.")
            return True
        elif num_of_vm_cls > 1:
            self.write_debugger("Error: More than a unique virtual " +
                                "machine defined in a single file." + '\n' +
                                "Select a new file.")
            return True

        self.write_debugger("Virtual machine correctly defined.")

        return False

    def load_ports(self):
        """Loads available ports into interface section's spinner.

        Note: When using glob, your current terminal "/dev/tty" is excluded.
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        available_ports = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                available_ports.append(port)
            except (OSError, serial.SerialException):
                pass

        self.inf_sp.values = available_ports

    def connect_to_machine(self):
        """Connect to virtual machine."""
        self.vm = self.vm_class(gui=self)

    def check_status(self):
        """Check status of real machine."""
        pass

    def write_debugger(self, message):
        """Print in debugging section."""
        self.debugger_lb.text += message + '\n\n'


class VirtualMachineBrowser(Popup):
    """Virtual machine browser class.

    Definition of a file browser based on Kivy's FileChooserListView.

    Attributes:
        parent_gui (Py3GestaltGUI): GUI that initializes this browser.
    """
    title = StringProperty('Select your virtual machine definition')

    def __init__(self):
        super(VirtualMachineBrowser, self).__init__()
        self.parent_gui = None

    def open(self, parent_gui):
        """Overrides 'open()' function.

        This function pops up the file browser and defines parent GUI.

        Arguments:
            parent_gui: GUI that instantiated this class, aka parent GUI.
        """
        super(VirtualMachineBrowser, self).open()
        self.parent_gui = parent_gui

    def select_virtual_machine(self, path, filename):
        """Select virtual machine's definition file.

        Gives parent GUI the path and filename of virtual machine's definition
        file. Also, writes file's name and content in parent GUI's debugger.
        Last, enables parent GUI's 'Load' button.

        Arguments:
            path (str): Current working directory, more information on Kivy's
                        FileChooser's reference.
            filename (str): Name of selected file.
        """
        self.parent_gui.vm_source_file = ''
        self.parent_gui.vm_source_file = os.path.join(path, filename)
        self.parent_gui.write_debugger(filename)
        self.parent_gui.vm_bt_import.disabled = False
        self.dismiss()


if __name__ == '__main__':
    Py3GestaltGUIApp().run()
