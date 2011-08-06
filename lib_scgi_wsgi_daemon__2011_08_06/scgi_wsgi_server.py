# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2011 Andrej A Antonov <polymorphm@qmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
assert unicode is not str

class ScgiWsgiServer(object):
    def __init__(self, loop_idle, app, socket,
            inactive_guard=None,
            inactive_quit_time=None,
            loop_quit=None):
        assert inactive_guard is not None or \
                inactive_quit_time is None or \
                inactive_quit_time is not None and loop_quit is not None
        
        from .daemon import start_daemon
        
        if inactive_guard is None and inactive_quit_time is not None:
            from .inactive_guard import InactiveGuard
            
            inactive_guard = InactiveGuard(loop_idle, loop_quit, inactive_quit_time)
            
        self._loop_idle = loop_idle
        self._app = app
        self._socket = socket
        self._inactive_guard = inactive_guard
        self._is_started = False
    
    def _conn_daemon(self, conn, address):
        pass # TODO: ...
    
    def _socket_accept_daemon(self):
        from socket import timeout
        
        self._socket.settimeout(10.0)
        try:
            conn, address = self._socket.accept()
        except timeout:
            self._loop_idle(self._socket_accept, None)
        else:
            self._loop_idle(self._socket_accept, (conn, address))
    
    def _socket_accept(self, accept_result):
        if self._is_started:
            from .daemon import start_daemon
            
            if accept_result is not None:
                conn, address = accept_result
                start_daemon(self.loop_idle, self._conn_daemon, conn, address)
            
            start_daemon(self.loop_idle, self._socket_accept_daemon)
    
    def start(self):
        if not self._is_started:
            from .daemon import start_daemon
            
            self._is_started = True
            self._inactive_guard.start()
            
            start_daemon(self.loop_idle, self._socket_accept_daemon)
    
    def stop(self):
        self._is_started = False
        self._inactive_guard.stop()
