#!/usr/bin/env python
#
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, util
from string import Template

dto_template = Template("""
package $base_package.$dto_package;

/**
 * $docs
 */
public final class $cls_name implements $base_package.$dto_package.$base_type {

$fields
$methods
}
""")

field_template = Template("""    public $type $name;\n""")

send_template = Template("""    @Override
    public int send(final $base_package.JVpp jvpp) {
        return jvpp.$method_name($args);
    }\n""")


def generate_dtos(func_list, base_package, dto_package):
    """ Generates dto objects in a dedicated package """
    print "Generating DTOs"

    if not os.path.exists(dto_package):
        raise Exception("%s folder is missing" % dto_package)

    for func in func_list:
        camel_case_dto_name = util.underscore_to_camelcase_upper(func['name'])
        camel_case_method_name = util.underscore_to_camelcase(func['name'])
        dto_path = os.path.join(dto_package, camel_case_dto_name + ".java")

        if util.is_notification(func['name']) or util.is_ignored(func['name']):
            # TODO handle notifications
            continue

        fields = ""
        for t in zip(func['types'], func['args']):
            fields += field_template.substitute(type=util.jni_2_java_type_mapping[t[0]],
                                                name=util.underscore_to_camelcase(t[1]))
        methods = ""
        base_type = ""
        if util.is_reply(camel_case_dto_name):
            request_dto_name = get_request_name(camel_case_dto_name, func['name'])
            if util.is_details(camel_case_dto_name):
                # FIXME assumption that dump calls end with "Dump" suffix. Not enforced in vpe.api
                base_type += "JVppReply<%s.%s.%s>" % (base_package, dto_package, request_dto_name + "Dump")
                generate_dump_reply_dto(request_dto_name, base_package, dto_package, camel_case_dto_name,
                                        camel_case_method_name, func)
            else:
                base_type += "JVppReply<%s.%s.%s>" % (base_package, dto_package, request_dto_name)
        else:
            args = "" if fields is "" else "this"
            methods = send_template.substitute(method_name=camel_case_method_name,
                                               base_package=base_package,
                                               args=args)
            if util.is_dump(camel_case_dto_name):
                base_type += "JVppDump"
            else:
                base_type += "JVppRequest"

        dto_file = open(dto_path, 'w')
        dto_file.write(dto_template.substitute(docs='Generated from ' + str(func),
                                               cls_name=camel_case_dto_name,
                                               fields=fields,
                                               methods=methods,
                                               base_package=base_package,
                                               base_type=base_type,
                                               dto_package=dto_package))
        dto_file.flush()
        dto_file.close()

    flush_dump_reply_dtos()


dump_dto_suffix = "ReplyDump"
dump_reply_artificial_dtos = {}


# Returns request name or special one from unconventional_naming_rep_req map
def get_request_name(camel_case_dto_name, func_name):
    return util.underscore_to_camelcase_upper(
        util.unconventional_naming_rep_req[func_name]) if func_name in util.unconventional_naming_rep_req \
        else util.remove_reply_suffix(camel_case_dto_name)


def flush_dump_reply_dtos():
    for dump_reply_artificial_dto in dump_reply_artificial_dtos.values():
        dto_path = os.path.join(dump_reply_artificial_dto['dto_package'],
                                dump_reply_artificial_dto['cls_name'] + ".java")
        dto_file = open(dto_path, 'w')
        dto_file.write(dto_template.substitute(docs=dump_reply_artificial_dto['docs'],
                                               cls_name=dump_reply_artificial_dto['cls_name'],
                                               fields=dump_reply_artificial_dto['fields'],
                                               methods=dump_reply_artificial_dto['methods'],
                                               base_package=dump_reply_artificial_dto['base_package'],
                                               base_type=dump_reply_artificial_dto['base_type'],
                                               dto_package=dump_reply_artificial_dto['dto_package']))
        dto_file.flush()
        dto_file.close()


def generate_dump_reply_dto(request_dto_name, base_package, dto_package, camel_case_dto_name, camel_case_method_name,
                            func):
    base_type = "JVppReplyDump<%s.%s.%s, %s.%s.%s>" % (
        base_package, dto_package, util.remove_reply_suffix(camel_case_dto_name) + "Dump",
        base_package, dto_package, camel_case_dto_name)
    fields = "    public java.util.List<%s> %s = new java.util.ArrayList<>();" % (camel_case_dto_name, camel_case_method_name)
    cls_name = camel_case_dto_name + dump_dto_suffix

    # In case of already existing artificial reply dump DTO, just update it
    # Used for sub-dump dtos
    if request_dto_name in dump_reply_artificial_dtos.keys():
        dump_reply_artificial_dtos[request_dto_name]['fields'] = \
            dump_reply_artificial_dtos[request_dto_name]['fields'] + '\n' + fields
    else:
        dump_reply_artificial_dtos[request_dto_name] = ({'docs': 'Dump reply wrapper generated from ' + str(func),
                                                         'cls_name': cls_name,
                                                         'fields': fields,
                                                         'methods': "",
                                                         'base_package': base_package,
                                                         'base_type': base_type,
                                                         'dto_package': dto_package,
                                                         })