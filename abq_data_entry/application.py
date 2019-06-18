import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
from datetime import datetime
from . import views as v
from . import models as m


class Application(tk.Tk):
    """Application root window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('ABQ Data Entry Application')
        self.resizable(width=False, height=False)

        ttk.Label(self, text='ABQ Data Entry Application', font=('TkDefaultFont', 16)).grid(row=0, pady=5)
        datestring = datetime.today().strftime('%Y-%m-%d')
        default_filename = f'abq_data_record_{datestring}.csv'
        self.filename = tk.StringVar(value=default_filename)
        self.data_model = m.CSVModel(filename=self.filename.get())

        self.settings_model = m.SettingModel()
        self.load_settings()

        self.callbacks = {
            'file->select': self.on_file_select,
            'file->quit': self.quit
        }
        menu = v.MainMenu(self, self.settings, self.callbacks)
        self.config(menu=menu)

        self.recordform = v.DataRecordForm(self, m.CSVModel.fields, self.settings)
        self.recordform.grid(row=1, padx=10, sticky='NSEW')

        self.recordlist = v.RecordList(self, self.callbacks)
        self.recordlist.grid(row=1, padx=10, sticky='NSEW')

        self.savebutton = ttk.Button(self, text='Save', command=self.on_save)
        self.savebutton.grid(sticky=tk.E, row=2, padx=10)

        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(sticky=(tk.W + tk.E), row=3, padx=10)

        self.records_saved = 0

    def load_settings(self):
        """Load settings into our self.settings dict."""
        vartypes = {
            'bool': tk.BooleanVar,
            'str': tk.StringVar,
            'int': tk.IntVar,
            'float': tk.DoubleVar
        }

        self.settings = {}
        for key, data in self.settings_model.variables.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])

        for var in self.settings.values():
            var.trace('w', self.save_settings)

    def save_settings(self, *args):
        """Save the current settings to a preferences file"""
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
        self.settings_model.save()

    def on_save(self):
        # Check for errors first
        errors = self.recordform.get_errors()
        if errors:
            error_string = f'Cannot save, error in fields: {", ".join(errors.keys())}'
            error_string = error_string[:90] + '...' if len(error_string) > 90 else error_string
            self.status.set(error_string)
            message = 'Cannot save record'
            error_list = '\n  * '.join(errors.keys())
            detail = f'The following fields have errors: \n  * {error_list}'
            messagebox.showerror(title='Error', message=message, detail=detail)
            return False

        filename = self.filename.get()
        model = m.CSVModel(filename)
        data = self.recordform.get()
        model.save_record(data)
        self.records_saved += 1
        self.status.set(f'{self.records_saved} records saved this session')
        self.recordform.reset()

    def on_file_select(self):
        """Handle the file->select action from the menu"""

        filename = filedialog.asksaveasfilename(
            title='Select the target file for saving records',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
        )

        if filename:
            self.filename.set(filename)
            self.data_model = m.CSVModel(filename=self.filename.get())
