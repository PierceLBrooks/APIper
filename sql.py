
# Author: Pierce Brooks

import os
import sys
import json
import uuid
from passlib.context import CryptContext

def refer(references, first, second):
    result = {}
    if (first in references):
        for third in references[first]:
            for fourth in references[first][third]:
                for i in range(len(references[first][third][fourth])):
                    if (references[first][third][fourth][i] == second):
                        if not (third in result):
                            result[third] = []
                        if not (fourth in result[third]):
                            result[third].append(fourth)
    return result
    
def defer(references, first, second):
    result = {}
    for third in references:
        for fourth in references[third]:
            if (first == fourth):
                for fifth in references[third][fourth]:
                    if (fifth == second):
                        if not (third in result):
                            result[third] = []
                        for i in range(len(references[third][fourth][fifth])):
                            if not (references[third][fourth][fifth][i] in result[third]):
                                result[third].append(references[third][fourth][fifth][i])
    return result

def run(target):
    uuids = {}
    secret = "SECRET"
    context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    handle = open(target, "r")
    lines = handle.readlines()
    handle.close()
    content = ""
    for line in lines:
        content += line.strip()+"\n"
    data = json.loads(content.strip())
    tab = "\t"
    tables = data["tables"]
    references = data["references"]
    content = ""
    for first in tables:
        table = tables[first]
        output = ""
        for second in table:
            type = table[second]
            if (type == "str"):
                type = "character varying"
            elif (type == "int"):
                type = "integer"
            elif (type == "bool"):
                type = "boolean"
            elif (type == "uuid"):
                reference = defer(references, first, second)
                print(str(reference))
                if not (len(reference.keys()) == 0):
                    if not (first in uuids):
                        uuids[first] = {}
                    if not (second in uuids[first]):
                        uuids[first][second] = {}
            else:
                type = ""
            if (len(type) == 0):
                continue
            output += tab+second+" "+type
            if not (table[second] == "str"):
                output += " NOT"
            output += " NULL"
            output += ",\n"
        if (len(output) == 0):
            continue
        output = "\nCREATE TABLE public.\""+first+"\" (\n"+output
        output += tab+"CONSTRAINT "+first+"_pk PRIMARY KEY (id)\n"
        output += ");\n"
        content += output
    content += "\n"
    inserts = data["inserts"]
    populations = {}
    nulls = {}
    for first in inserts:
        if not (first in tables):
            continue
        table = tables[first]
        if not (first in populations):
            populations[first] = 0
        for i in range(len(inserts[first])):
            insert = inserts[first][i]
            output = ""
            values = ""
            for second in insert:
                if not (second in table):
                    continue
                type = table[second]
                value = insert[second]
                if ("password" in second):
                    password = context.hash(value)
                    print(value+" -> "+password)
                    value = password
                if (type == "str"):
                    if ("'" in value):
                        value = "E'"+value.replace("'", "\\'")+"'"
                    else:
                        value = "'"+value+"'"
                elif (type == "int"):
                    pass
                elif (type == "bool"):
                    pass
                elif (type == "uuid"):
                    check = True
                    if (first in uuids):
                        if (second in uuids[first]):
                            check = False
                            if (str(i) in uuids[first][second]):
                                value = uuids[first][second][str(i)]
                            else:
                                value = str(uuid.uuid4())
                                print(str(i)+" -> "+value)
                                uuids[first][second][str(i)] = value
                    else:
                        reference = refer(references, first, second)
                        print(str(reference))
                        for key in reference:
                            if (key in uuids):
                                for j in range(len(reference[key])):
                                    if (reference[key][j] in uuids[key]):
                                        if (value in uuids[key][reference[key][j]]):
                                            check = False
                                            value = uuids[key][reference[key][j]][value]
                                            break
                                if not (check):
                                    break
                    if (check):
                        continue
                    value = "'"+value+"'"
                else:
                    continue
                output += second+", "
                values += value+", "
                if (second == "id"):
                    if not (first in nulls):
                        nulls[first] = value
            if (len(output) == 0):
                continue
            populations[first] += 1
            output = "INSERT INTO public.\""+first+"\" ("+output[:(len(output)-2)]+") VALUES ("+values[:(len(values)-2)]+");\n"
            content += output
        content += "\n"
    content += "\n"
    output = "\nCREATE TABLE public.\"nulls\" (\n"
    output += tab+"tablename character varying NOT NULL,\n"
    output += tab+"id character varying NOT NULL,\n"
    output += tab+"CONSTRAINT nulls_pk PRIMARY KEY (tablename)\n"
    output += ");\n"
    content += output
    for first in nulls:
        output = "INSERT INTO public.\"nulls\" (tablename, id) VALUES ('"+first+"', '"+nulls[first].replace("'", "")+"');\n"
        content += output
    content += "\n"
    output = "\nCREATE TABLE public.\"populations\" (\n"
    output += tab+"tablename character varying NOT NULL,\n"
    output += tab+"population integer NOT NULL,\n"
    output += tab+"CONSTRAINT populations_pk PRIMARY KEY (tablename)\n"
    output += ");\n"
    content += output
    for first in populations:
        output = "INSERT INTO public.\"populations\" (tablename, population) VALUES ('"+first+"', "+str(populations[first])+");\n"
        content += output
    content += "\n"
    for first in references:
        if not (first in tables):
            continue
        for second in references[first]:
            if not (second in tables):
                continue
            if (first == second):
                continue
            for third in references[first][second]:
                if not (third in tables[second]):
                    continue
                for i in range(len(references[first][second][third])):
                    fourth = references[first][second][third][i]
                    if not (fourth in tables[first]):
                        continue
                    print(fourth+" @ "+first+" -> "+third+" @ "+second)
                    output = "ALTER TABLE public.\""+first+"\" ADD CONSTRAINT "+first+"_"+second+"_"+str(i)+"\n"
                    output += tab+"FOREIGN KEY ("+fourth+")\n"
                    output += tab+"REFERENCES public.\""+second+"\" ("+third+");\n"
                    content += output
                content += "\n"
    content += "\n"
    handle = open(target+".sql", "w")
    handle.write(content)
    handle.close()
    return 0

def launch(arguments):
    if (len(arguments) < 2):
        return False
    target = arguments[1]
    result = run(target)
    print(str(result))
    if not (result == 0):
        return False
    return True

if (__name__ == "__main__"):
    print(str(launch(sys.argv)))
