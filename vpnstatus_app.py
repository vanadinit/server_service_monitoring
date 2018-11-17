#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#################################################
# Webapp zum Auslesen des VPN-Server-Status     #
# --------------------------------------------- #
# Erstellt von Johannes Paul, 01.04.2015        #
# Bearbeitet am 17.11.2018                      #
# --------------------------------------------- #
#################################################


def html_output(status, statusline, clients):
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
            <span class="active" {statusstyle}>{statusline}</span><br/>
        </p>
        <table>
            <thead>
                <tr><th>Nutzername</th><th>VPN-Addresse</th><th>Reale Addresse</th><th>Gesendet</th><th>Empfangen</th><th>Verbunden seit</th></tr>
            </thead>
            <tbody>{clientlist}
            </tbody>
        </table>
    </body>
</html>
    """

    if status == 'aktiv':
        statusstyle = 'style="color:#00FF00"'
    elif status == 'inaktiv':
        statusstyle = 'style="color:#FF0000"'
    else:
        statusstyle = 'class="fehler"'

    clientlist = ''
    clienttempl =  '\n                <tr><td>{cn}</td><td>{virt}</td><td>{real}</td><td>{recv}</td><td>{sent}</td><td>{since}</td></tr>'
    for client in clients:
        clientlist += clienttempl.format(
            cn=client['cn'],
            virt=client['virt'],
            real=client['real'],
            recv=client['recv'],
            sent=client['sent'],
            since=client['since'],
        )

    htmltext = htmltext.format(
        statusstyle=statusstyle,
        statusline=statusline,
        clientlist=clientlist,
    )
    return htmltext


def vpnstatus(environ, start_response):
    import sys
    sys.path.append('/root/scripts')
    import vpnstatus_parser

    status, statusline = vpnstatus_parser.get_service_info()

    clients = []
    if status == 'aktiv':
        clients = vpnstatus_parser.get_status_info(True)

    # For Debugging
    #    print(clients, file=environ['wsgi.errors'])

    htmltext = html_output(status, statusline, clients)
    output = str.encode(htmltext)
    status = '200 OK'
    headers = [('Content-type', 'text/html'),
               ('Content-Length', str(len(output)))]
    start_response(status, headers)
    yield output


# mod_wsgi need the *application* variable to serve our small app
application = vpnstatus
