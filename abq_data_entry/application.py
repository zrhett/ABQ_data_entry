import tkinter as tk
from tkinter import ttk
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

        self.recordform = v.DataRecordForm(self, m.CSVModel.fields)
        self.recordform.grid(row=1, padx=10)

        self.savebutton = ttk.Button(self, text='Save', command=self.on_save)
        self.savebutton.grid(sticky=tk.E, row=2, padx=10)

        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(sticky=(tk.W + tk.E), row=3, padx=10)

        self.records_saved = 0

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

        datestring = datetime.today().strftime('%Y-%m-%d')
        filename = f'abq_data_record_{datestring}.csv'
        model = m.CSVModel(filename)
        data = self.recordform.get()
        model.save_record(data)
        self.records_saved += 1
        self.status.set(f'{self.records_saved} records saved this session')
        self.recordform.reset()
