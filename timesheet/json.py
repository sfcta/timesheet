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

# A JSON-based API(view) for your app.
# Most rules would look like:
# @jsonify.when("isinstance(obj, YourClass)")
# def jsonify_yourclass(obj):
#     return [obj.val1, obj.val2]
# @jsonify can convert your objects to following types:
# lists, dicts, numbers and strings

from turbojson.jsonify import jsonify

from turbojson.jsonify import jsonify_sqlobject
from timesheet.model import User, Group, Permission

@jsonify.when('isinstance(obj, Group)')
def jsonify_group(obj):
    result = jsonify_sqlobject( obj )
    result["users"] = [u.user_name for u in obj.users]
    result["permissions"] = [p.permission_name for p in obj.permissions]
    return result

@jsonify.when('isinstance(obj, User)')
def jsonify_user(obj):
    result = jsonify_sqlobject( obj )
    del result['password']
    result["groups"] = [g.group_name for g in obj.groups]
    result["permissions"] = [p.permission_name for p in obj.permissions]
    return result

@jsonify.when('isinstance(obj, Permission)')
def jsonify_permission(obj):
    result = jsonify_sqlobject( obj )
    result["groups"] = [g.group_name for g in obj.groups]
    return result
