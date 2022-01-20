import os,webbrowser
from appData import app
from appData.brocooliSecrets import appIp


def main():
    #if not os.environ.get("WERKZEUG_RUN_MAIN"):
    #    webbrowser.open_new('http://127.0.0.1:2000/')
    app.run(host=appIp, port=2000, debug=True)


if __name__ == '__main__':
    main()