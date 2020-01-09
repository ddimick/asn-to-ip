#!/usr/bin/env python3

import re
import socket
import argparse
import ipaddress

_parser = argparse.ArgumentParser()
_parser_group = _parser.add_mutually_exclusive_group(required = True)
_parser_group.add_argument('-a', '--asn', action = 'append', help = 'BGP Autonomous System Number (ASN), may use this parameter multiple times')
_parser_group.add_argument('-d', '--daemon', action = 'store_true', help = 'Run as a web sever (requires Flask)')
_parser.add_argument('-i', '--ip', default = '127.0.0.1', help = 'Host IP to attach the web server (default 127.0.0.1, use 0.0.0.0 for all interfaces)')
_parser.add_argument('-p', '--port', default = '5000', help = 'Port for web server (default: 5000)')
_parser.add_argument('-6', '--ipv6', action = 'store_true', help = 'Also include ipv6 network blocks (default: false)')
_parser.add_argument('--debug', action = 'store_true', help = 'Enable debug mode for Flask server')
_parser_args = _parser.parse_args()


## Controls socket communication to whois server.
def whois(_domain, _server = 'whois.radb.net', _port = 43):
  _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  _sock.connect((_server, _port))
  _sock.send(_domain.encode('utf-8'))
  _result = str()

  while True:
    _data = _sock.recv(1024).decode('iso-8859-1')

    if not _data:
      break

    _result += _data

  return(_result)


## Performs the whois query and returns a multiline string of the resulting IPv4 and/or IPv6 networks.
def get_asn_networks(_asn, _ipv4 = True, _ipv6 = False):
  _route_type = str()
  if _ipv6:
    _route_type = '[6]?' if _ipv4 else '6'

  _result = whois('-i origin {0}\r\n'.format(_asn))

  if _result:
    _networks = re.findall('^route{0}:\s+(.*?)$'.format(_route_type), _result, re.MULTILINE)

    if _networks:
      return(_networks)

  return(None)


## Deduplicates and sorts a list of networks from the list of ASNs. Returns a multi-line string.
def get_network_list():
  _networks = list()

  for _asn in range(0, len(_parser_args.asn)):
    _valid_asn = re.search('(?:AS)?(\d{1,10})', _parser_args.asn[_asn], re.IGNORECASE)
    if not _valid_asn:
      return('Invalid ASN "{0}". Example valid format is "AS54321" or simply "54321".'.format(_parser_args.asn[_asn]))
    _valid_asn = 'AS{0}'.format(_valid_asn.group(1))

    # Builds an object containing networks, removing duplicates.
    for _network in list(set(get_asn_networks(_valid_asn, True, _parser_args.ipv6))):
      _networks.append(ipaddress.ip_network(_network, strict = False))

  return('\n'.join(map(str, sorted(_networks, key=ipaddress.get_mixed_type_key))))


if __name__  ==  '__main__':
  ## Command-line mode
  if _parser_args.asn:
    print(get_network_list())

  ## Web daemon mode
  elif _parser_args.daemon:
    from flask import Flask, request
  
    app = Flask(__name__)
  
    @app.route('/')
    def index():
      if request.args.get('asn') is not None:
        # We aren't really using argparse here but, since the variable already exists, it's simple to reuse.
        _parser_args.asn = request.args.get('asn').split(',')
        _parser_args.ipv6 = True if request.args.get('ipv6') is not None else False
        return(get_network_list())

      return('usage: {0}?asn=X, where X is one or more BGP Autonomous System Numbers separated by commas.\nReturns IPv4 results by default. Add &ipv6 to also include IPv6 results, like {0}?asn=X&ipv6.'.format(request.url_root))

    app.run(debug = _parser_args.debug, host = _parser_args.ip, port = _parser_args.port)
