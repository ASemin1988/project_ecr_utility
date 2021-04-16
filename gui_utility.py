import PySimpleGUI as sg




def gui_app(name):
    layout = [
            [sg.Text('Вывести информацию о ККТ', size=(30, 1)),
             sg.Button('Информация о ККТ', size=(25, 1), border_width=3)],
            [sg.Text('Печать информации о ККТ', size=(30, 1)),
             sg.Button('Печать информации', size=(25, 1), border_width=3)],
            [sg.Text('Технологическое обнуление', size=(30, 1)),
             sg.Button('Тех.обнуление', size=(25, 1), border_width=3)],
            [sg.Text('Перезагрузка кассы', size=(30, 1)),
             sg.Button('Перезагрузить', size=(25, 1), border_width=3)],
            [sg.Text('Инициализация ФНа', size=(30, 1)),
             sg.Button('Очистить ФН', size=(25, 1), border_width=3)],
            [sg.Text('Инициализация ККТ', size=(30, 1)),
             sg.Button('Инициализация ККТ', size=(25, 1), border_width=3)],
            [sg.Text('Записать лицензии/коды защиты в ККТ', size=(30, 1)),
             sg.Button('Записать лицензии', size=(25, 1), border_width=3)],
            [sg.Text('Запись ключей и uin', size=(30, 1)),
             sg.Button('Записать ключи', size=(25, 1), border_width=3)],
            [sg.Output(size=(80, 20))],
            [sg.Cancel()]
        ]
    window = sg.Window('Утилита для работы с кассой', layout)
    while True:
        event, values = window.read()
        if event in 'Информация о ККТ':
            name.get_information_kkt()
        if event in 'Печать информации':
            name.print_info_kkt()
        if event in 'Тех.обнуление':
            name.technical_reset_kkt()
        if event in 'Перезагрузить':
            name.reboot_kkt()
        if event in 'Очистить ФН':
            name.clear_fn_kkt()
        if event in 'Инициализация ККТ':
            name.check_initialisation_kkt()
        if event in 'Записать лицензии':
            name.write_licenses()
        if event in 'Записать ключи':
            name.enter_uin_from_file()
        if event in (None, 'Exit', 'Cancel') or event == sg.WINDOW_CLOSED:
            exit()

