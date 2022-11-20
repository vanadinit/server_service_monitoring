import curses
import subprocess
import telnetlib

# Path to logfile (format -> status-version 3)
STATUSFILE = "/tmp/ramdisk/openvpn-status.log"


def curses_header(screen, tel):
    screen.addstr("\n\n")
    if tel:
        screen.addstr("%+66s" % 'VPN-Server (Telnet-Abfrage)', curses.color_pair(5) | curses.A_BOLD)
    else:
        screen.addstr("%+63s" % 'VPN-Server (Logdatei)', curses.color_pair(5) | curses.A_BOLD)
    screen.addstr(
        "\n----------------------------------------------------------------------------------------------------------\n")


def curses_status(screen, status, statusline):
    if status == 'aktiv':
        screen.addstr(statusline + '\n', curses.color_pair(3))
    elif status == 'inaktiv':
        screen.addstr(statusline + '\n', curses.color_pair(2))
    else:
        screen.addstr(statusline + '\n', curses.color_pair(4))


def curses_clients(screen, clients):
    # Define headers
    headers = {
        'cn': 'Nutzername',
        'virt': 'VPN-Addresse',
        'real': 'Reale Addresse',
        'sent': 'Gesendet',
        'recv': 'Empfangen',
        'since': 'Verbunden seit'
    }

    fmt = "%(cn)-14s %(virt)-19s %(real)-16s %(sent)11s %(recv)13s %(since)28s"
    screen.addstr(fmt % headers + '\n')
    screen.addstr(
        "----------------------------------------------------------------------------------------------------------\n")
    screen.addstr("\n".join([fmt % h for h in clients]), curses.color_pair(4) | curses.A_BOLD)


def get_service_info():
    process = subprocess.Popen(
        'systemctl status openvpn@server.service',
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )

    status = 'inaktiv'
    status_line = 'Fehler in der Statusüberprüfung!!!\n'
    for line in process.stdout.read().split('\n'):
        if line.find('Active') > -1:
            if line.find('inactive') == -1:
                status = 'aktiv'
            status_line = line
            break

    return status, status_line


def get_status_info(tel: bool):
    clients = []

    if tel:
        # Connect via Telnet to Openvpn Management Interface
        # Query status
        vpn = telnetlib.Telnet("127.0.0.1", 5555)
        vpn.write(b"status 3 \r\n")
        data = bytes.decode(vpn.read_until(b"END", 2))
        vpn.write(b"exit \r\n")
        vpn.close()
        stats = data.split("\r\n")
    else:
        # Open logfile and read
        status_file = open(STATUSFILE, 'r')
        stats = status_file.readlines()
        status_file.flush()

    # Search for the right data
    for line in stats:
        cols = line.split('\t')
        if len(cols) == 12 and line.startswith('CLIENT_LIST'):
            clients.append({
                'cn': cols[1],
                'real': cols[2].split(':')[0],
                'virt': cols[3],
                'recv': byte2str(int(cols[5])),
                'sent': byte2str(int(cols[6])),
                'since': cols[7].strip(),
            })
    return clients


def byte2str(size):
    # Nice byte formatting
    for border, suffix in [
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'KB'),
        (1, 'B')
    ]:
        if size >= border:
            return f'{size / float(border):.2f} {suffix}'
