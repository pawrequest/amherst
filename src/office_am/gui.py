import PySimpleGUI as sg


def invoice_gui():
    layout = [
        [sg.Checkbox('Save', default=True, key='-SAVE-')],
        [sg.Checkbox('Open', default=True, key='-OPEN-')],
        [sg.Checkbox('Print', default=False, key='-PRINT-')],
        [sg.Checkbox('Email', default=False, key='-EMAIL-')],
        [sg.Checkbox('Log cmc', default=False, key='-CMC-')],
        [sg.Button('Submit')]
    ]
    window = sg.Window('Actions', layout)
    return window
