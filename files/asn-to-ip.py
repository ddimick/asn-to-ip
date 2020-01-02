#!/usr/bin/env python3
#--------------------------------------#
# File name: asn-to-ip.py
# Author: Doug Dimick <doug@dimick.net>
# Last Modified: Jan 2 2020
#--------------------------------------#

import argparse

parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group(required = True)
group.add_argument('-a', '--asn', type = int, action = 'append', help = 'BGP Autonomous System Number (ASN)')
group.add_argument('-d', '--daemon', action = 'store_true', help = 'Run as a web sever')

parser.add_argument('-p', '--port', default = 5000, help = 'Port for web server (default: 5000)')
parser.add_argument('-6', '--ipv6', action = 'store_true', help = 'Also include ipv6 network blocks (default: false)')

args = parser.parse_args()

## https://tools.ietf.org/html/rfc3912
def whois_request(domain, server, port = 43):
  import socket

  _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  _sock.connect((server, port))
  _sock.send(domain.encode('utf-8'))
  _result = ""

  while True:
    _data = _sock.recv(1024).decode('iso-8859-1')

    if not _data:
      break

    _result +=  _data

  return _result

def get_asn_netblocks(AS, IPV4 = True, IPV6 = True):
  import re

  _asn = re.search("(?:AS)?(\d{1,10})", AS, re.IGNORECASE)

  if not _asn:
    return ""

  _asn = "AS{0}".format(_asn.group(1))

  is6 = ""
  if IPV6:
    is6 = "[6]?" if IPV4 else "6"

  _raw = whois_request("-i origin {0}\r\n".format(_asn),"whois.radb.net")

  if _raw:
    _ips = re.findall("^route{0}:\s+(.*?)$".format(is6),_raw,re.MULTILINE)

    return "\n".join(_ips)

  return ""

if __name__  ==  '__main__':
  if args.asn:
    for i in range(0, len(args.asn)):
      print(get_asn_netblocks(str(args.asn[i]), IPV4 = True, IPV6 = args.ipv6))

  elif args.daemon:
    from flask import Flask, request, url_for, redirect
  
    app = Flask(__name__)
  
    @app.route('/')
    def usage():
      return('usage: {0}asn/X or {0}ipv6/asn/X, where X is a BGP Autonomous System Number.'.format(request.url_root))
  
    ## Catch requests with no ASN included.
    @app.route('/asn/')
    def empty_asn():
      return redirect(url_for('usage'))

    @app.route('/ipv6/')
    def empty_ipv6():
      return redirect(url_for('usage'))

    @app.route('/ipv6/asn/')
    def empty_ipv6_asn():
      return redirect(url_for('usage'))

    ## Catch requests where the ASN is not an integer.
    @app.route('/asn/<_invalid>')
    def invalid(_invalid):
      return redirect(url_for('usage'))
  
    @app.route('/ipv6/asn/<_invalid>')
    def invalid_ipv6(_invalid):
      return redirect(url_for('usage'))
  
    ## Route handlers for a properly formatted request.
    @app.route('/asn/<int:_asn>')
    def asn(_asn):
      return(get_asn_netblocks('{0}'.format(_asn), True, False))
  
    @app.route('/ipv6/asn/<int:_asn>')
    def asn_ipv6(_asn):
      return(get_asn_netblocks('{0}'.format(_asn), True, True))
  
    app.run(debug = False, port = args.port)
