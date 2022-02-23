

pip3 install -U pip virtualenv
virtualenv --system-site-packages -p python ./venv
.\venv\Scripts\activate


## для запуска venv в консоли
терминал от администратора:
    Set-ExecutionPolicy RemoteSigned
ввод:
    A

## venv
python -m venv venv
.\venv\Scripts\activate

## UI to python
pyuic5 qt_templates/LoginUI.ui -o ui/LoginUI.py
Не забываем подключить наши таблицы MyTableWidget.py