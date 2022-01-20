from distutils.log import debug
import os,webbrowser
from appData import app


def main():
    app.run(host='127.0.0.1', port=443, ssl_context='adhoc', debug=True)


if __name__ == '__main__':
    main()