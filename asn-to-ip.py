#!/usr/bin/env python3

import argparse
import ipaddress
import re
import telnetlib

## Get command-line options.
_parser = argparse.ArgumentParser()
_parser_group = _parser.add_mutually_exclusive_group(required = True)
_parser_group.add_argument('-a', '--asn', action = 'append', help = 'BGP Autonomous System Number (ASN), may use this parameter multiple times')
_parser_group.add_argument('-d', '--daemon', action = 'store_true', help = 'Run as a web sever (requires Flask)')
_parser.add_argument('-i', '--ip', default = '127.0.0.1', help = 'Host IP to attach the web server (default 127.0.0.1, use 0.0.0.0 for all interfaces)')
_parser.add_argument('-p', '--port', default = '5000', help = 'Port for web server (default: 5000)')
_parser.add_argument('-6', '--ipv6', action = 'store_true', help = 'Also include ipv6 network blocks (default: false)')
_parser.add_argument('--debug', action = 'store_true', help = 'Enable debug mode for Flask server')
_parser_args = _parser.parse_args()


## Controls telnet session.
def telnet(_asn_list, _server = 'whois.radb.net', _port = '43', _timeout = 10):

  # Build query string.
  _query = '!!\n' # Tells RADB to expect multiple queries in this session.
  for _asn in _asn_list:
    _query += '!g' + _asn + '\n' # Query for IPv4 routes.
    if _parser_args.ipv6:
      _query += '!6' + _asn + '\n' # Query for IPv6 routes.
  _query += 'exit\n' # Ends session.

  # Execute telnet session.
  with telnetlib.Telnet(_server, _port, _timeout) as _telnet:
    _telnet.write(_query.encode('ascii'))
    return(_telnet.read_all().decode('ascii'))

  return(None)


## Gets a list of networks from the list of ASNs. Returns a sorted and deduplicated multi-line string.
def get_network_list(_asn_list = list(), _result = list()):

  # Build list of ASNs.
  for _asn in _parser_args.asn:
    _valid_asn = re.search('(?:AS)?(\d{1,10})', _asn, re.IGNORECASE) # Check that we have a valid-looking ASN.
    if _valid_asn:
      _asn_list.append('AS{0}'.format(_valid_asn.group(1)))
    else:
      return('Invalid ASN "{0}". Example valid format is "AS54321" or simply "54321".'.format(_asn))

  # Builds list of valid networks, removing duplicates.
  for _network in set(telnet(_asn_list).split()):
    try:
      _result.append(ipaddress.ip_network(_network, strict = False))
    except ValueError:
      continue # Ignore anything that isn't a valid network.

  return('\n'.join(map(str, sorted(_result, key=ipaddress.get_mixed_type_key))))


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
        _parser_args.asn = request.args.get('asn').split(',')
        _parser_args.ipv6 = True if request.args.get('ipv6') is not None else False
        return(get_network_list())

      return('usage: {0}?asn=X, where X is one or more BGP Autonomous System Numbers separated by commas.\nReturns IPv4 results by default. Add &ipv6 to also include IPv6 results, like {0}?asn=X&ipv6.'.format(request.url_root))

    app.run(debug = _parser_args.debug, host = _parser_args.ip, port = _parser_args.port)

