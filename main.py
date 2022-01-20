import os,webbrowser
from appData import app
from appData.brocooliSecrets import appIp, appPort


def main():
    app.run(host='127.0.0.1', port=5000, ssl_context='adhoc')


if __name__ == '__main__':
    main()