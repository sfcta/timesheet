"""  

  http://github.com/sfcta/timesheet

  Timesheet, Copyright 2013 San Francisco County Transportation Authority
                            San Francisco, CA, USA
                            http://www.sfcta.org/
                            info@sfcta.org

  This file is part of Timesheet.

  Timesheet is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  Timesheet is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with Timesheet.  If not, see <http://www.gnu.org/licenses/>.
  
"""

import unittest
import turbogears
from turbogears import testutil
from timesheet.controllers import Root
import cherrypy

cherrypy.root = Root()

class TestPages(unittest.TestCase):

    def setUp(self):
        turbogears.startup.startTurboGears()

    def tearDown(self):
        """Tests for apps using identity need to stop CP/TG after each test to
        stop the VisitManager thread.
        See http://trac.turbogears.org/turbogears/ticket/1217 for details.
        """
        turbogears.startup.stopTurboGears()

    def test_method(self):
        "the index method should return a string called now"
        import types
        result = testutil.call(cherrypy.root.index)
        assert type(result["now"]) == types.StringType

    def test_indextitle(self):
        "The indexpage should have the right title"
        testutil.create_request("/")
        response = cherrypy.response.body[0].lower()
        assert "<title>welcome to turbogears</title>" in response

    def test_logintitle(self):
        "login page should have the right title"
        testutil.create_request("/login")
        response = cherrypy.response.body[0].lower()
        assert "<title>login</title>" in response
