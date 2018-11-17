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
    htmltext = "<!DOCTYPE html>\n"
    htmltext += '<html><head>\n'
    htmltext += '<title>VPN-Server-Status</title>\n'
    htmltext += '<link rel="stylesheet" type="text/css" href="vpnstatus.css" media="screen, projection" title="Standarddesign"/>\n'
    htmltext += '<meta http-equiv="refresh" content="10">\n'
    htmltext += '</head>\n'
    htmltext += '<body>\n<h1>VPN-Server-Status</h1>\n'
    htmltext += "<p>Serverstatus:<br/>"

    if status == 'aktiv':
        htmltext += '<span class="active" style="color:#00FF00">' + statusline + '</span><br/>\n'
    elif status == 'inaktiv':
        htmltext += '<span class="active" style="color:#FF0000;">' + statusline + '</span><br/>\n'
    else:
        htmltext += '<span class="active" class="fehler">' + statusline + '</span><br/>\n'

    htmltext += '</p>'

    htmltext += '<table>\n'
    htmltext += '<thead>\n'
    htmltext += '<tr><th>Nutzername</th><th>VPN-Addresse</th><th>Reale Addresse</th><th>Gesendet</th><th>Empfangen</th><th>Verbunden seit</th></tr>\n'
    htmltext += '</thead>\n'
    htmltext += '<tbody>\n'
    for client in clients:
        htmltext += '<tr><td>' + client['cn'] + '</td><td>' + client['virt'] + '</td><td>' + client[
            'real'] + '</td><td>' + client['recv'] + '</td><td>' + client['sent'] + '</td><td>' + client[
                        'since'] + '</td></tr>\n'
    htmltext += '</tbody>\n'
    htmltext += '</table>\n'

    htmltext += "</body></html>"
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
