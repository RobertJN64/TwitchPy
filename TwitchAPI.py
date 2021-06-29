import warnings
import socket

def sendMessage(s, channel, message):
    m = "PRIVMSG " + channel + " :" + message + "\r\n"
    s.send(bytes(m, 'utf-8'))

def loadTokens():
    with open("token.txt") as f:
        lines = f.readlines()

    if len(lines) != 3:
        warnings.warn("Error parsing token file.")

    clientID = lines[0].strip('\n')
    clientSecret = lines[1].strip('\n')
    oauth = lines[2].strip('\n')

    return clientID, clientSecret, oauth

def parseCommand(message):
    i = str(message).index(':', 1)
    return message[i + 1:].strip('\n').strip('\r')

def connect():
    """Connect to the server and return a working socket"""
    server = 'irc.twitch.tv'
    port = 6667
    nickname = 'robertjn_dev'
    channel = '#robertjn_dev'

    clientID, clientSecret, oauth = loadTokens()

    s = socket.socket()
    s.connect((server, port))
    s.send(f"PASS {oauth}\n".encode('utf-8'))
    s.send(f"NICK {nickname}\n".encode('utf-8'))
    s.send(f"JOIN {channel}\n".encode('utf-8'))

    return s

def checkChat(s, l):
    """Check for chat updates on the server"""
    resp = s.recv(2048).decode('utf-8')

    if resp.startswith('PING'):
        s.send("PONG\n".encode('utf-8'))

    elif len(resp) > 0 and 'PRIVMSG' in resp:
        l.append(parseCommand(resp))