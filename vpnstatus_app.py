#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#################################################
# Webapp zum Auslesen des VPN-Server-Status     #
# --------------------------------------------- #
# Erstellt von Johannes Paul, 01.04.2015        #
# Bearbeitet am 17.11.2018                      #
# --------------------------------------------- #
#################################################

import os


def html_output(status, status_line, clients):
    htmltext = """<!DOCTYPE html>
<html>
    <head>
        <title>VPN-Server-Status</title>
        <link rel="stylesheet" type="text/css" href="vpnstatus.css" media="screen, projection" title="Standarddesign"/>
        <meta http-equiv="refresh" content="10">
    </head>
    <body>
        <h1>VPN-Server-Status</h1>
        <p>Serverstatus:<br/>
            <span class="active" {status_style}>{status_line}</span><br/>
        </p>
        <table>
            <thead>
                <tr><th>Nutzername</th><th>VPN-Addresse</th><th>Reale Addresse</th><th>Gesendet</th><th>Empfangen</th><th>Verbunden seit</th></tr>
            </thead>
            <tbody>{client_list}
            </tbody>
        </table>
    </body>
</html>
    """

    if status == 'aktiv':
        status_style = 'style="color:#00FF00"'
    elif status == 'inaktiv':
        status_style = 'style="color:#FF0000"'
    else:
        status_style = 'class="fehler"'

    client_templ = '<tr><td>{cn}</td><td>{virt}</td><td>{real}</td><td>{recv}</td><td>{sent}</td><td>{since}</td></tr>'
    client_list = '\n                '.join([client_templ.format(**client) for client in clients])

    return htmltext.format(
        status_style=status_style,
        status_line=status_line,
        client_list=client_list,
    )


def vpnstatus(environ, start_response):
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import vpnstatus_parser

    status, status_line = vpnstatus_parser.get_service_info()

    clients = []
    if status == 'aktiv':
        clients = vpnstatus_parser.get_status_info(tel=True)

    # For Debugging
    #    print(clients, file=environ['wsgi.errors'])

    htmltext = html_output(status, status_line, clients)
    output = str.encode(htmltext)
    status = '200 OK'
    headers = [('Content-type', 'text/html'),
               ('Content-Length', str(len(output)))]
    start_response(status, headers)
    yield output


# mod_wsgi need the *application* variable to serve our small app
application = vpnstatus
