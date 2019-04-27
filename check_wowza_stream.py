#!/usr/bin/env python

import nagiosplugin
import requests
import argparse
from requests.auth import HTTPDigestAuth
from urlparse import urlunparse

class Stream(nagiosplugin.Resource):

    """Wowza v4 stream status Nagios check
       Requests Wowza4 API URL '/v2/servers/{servername}/vhosts/{vhostname}/applications/livecam/instances/{instancename}/incomingstreams/{streamname}'
       Checks for returned 'isConnected' value
    """
    def __init__(self,host,port,user,password,timeout,serverName,vhostName,instanceName,appName,streamName):
        self.scheme = 'http'
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.serverName = serverName
        self.vhostName = vhostName
        self.instanceName = instanceName
        self.appName = appName
        self.streamName = streamName
        self.status = False

    def probe(self):
        path = "/v2/servers/{}/vhosts/{}/applications/{}/instances/{}/incomingstreams/{}".format(
                self.serverName, self.vhostName, self.appName, self.instanceName, self.streamName)
        netloc = "{}:{}".format(self.host, self.port)
        url = urlunparse((self.scheme, netloc, path, None, None, None))

        headers = {
                'user-agent': 'nagiosplugin-check-wowza-stream/0.0.1',
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json; charset=utf-8',
                }

        try:
            r = requests.get(url, headers=headers, auth=HTTPDigestAuth(self.user, self.password), timeout=self.timeout)
            # Raise for all responses which are not 200
            r.raise_for_status()
            if r.json()['isConnected']: self.status = True
        except (requests.ConnectionError, requests.HTTPError) as err:
            print("Check Error: %s" % err) 

        return [nagiosplugin.Metric('status', self.status, context='status')]


#@nagiosplugin.guarded(verbose=0)
def main():
    argp = argparse.ArgumentParser(description=__doc__)
    
    argp.add_argument('-H', '--host',
            default='localhost', help='Server host. Default = localhost')
    argp.add_argument('-P', '--port',
            default='8087', help='Server port. Default = 8087')
    argp.add_argument('-u', '--user',
            default='nagios', help='Username for Wowza API. Default = nagios')
    argp.add_argument('-p', '--password',
            default='nagios', help='Password for Wowza API. Default = nagios')
    argp.add_argument('-t', '--timeout',
            default=3, help='Server connection timeout. Default = 5')
    argp.add_argument('--serverName',
            default='_defaultServer_', help='Wowza server name. Default = _defaultServer_')
    argp.add_argument('--vhostName',
            default='_defaultVHost_', help='Wowza vhost name. Default = _defaultVHost_')
    argp.add_argument('--instanceName',
            default='_definst_', help='Wowza instance name. Default = _definst_')
    argp.add_argument('-a', '--app',
            default='live', help='Wowza application name. Default = live')
    argp.add_argument('-s', '--stream',
            default='live.stream', help='Wowza stream name. Default = live.stream')
    args = argp.parse_args()
    
    check = nagiosplugin.Check(
            Stream(
                host=args.host,
                port=args.port,
                user=args.user,
                password=args.password,
                timeout=args.timeout,
                serverName=args.serverName,
                vhostName=args.vhostName,
                instanceName=args.instanceName,
                appName=args.app,
                streamName=args.stream),
            nagiosplugin.ScalarContext('status', None, '1:', fmt_metric=args.stream)
            )

    check.main()

if __name__ == '__main__':
    main()

