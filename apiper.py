
# Author: Pierce Brooks

import os
import sys
import json
import inspect
import xml.etree.ElementTree as xml_tree

def get_parent(parents, tag):
  length = len(parents)
  if (length == 0):
    return None
  for i in range(length):
    temp = (length-1)-i
    if not (parents[temp] == None):
      if not (tag == None):
        if (parents[temp].tag == tag):
          return parents[temp]
      else:
        return parents[temp]
  return None
  
def get_child(node, tag):
  for child in node:
    if (child.tag == tag):
      return child
    temp = get_child(child, tag)
    if not (temp == None):
      return temp
  return None
  

def wd():
  filename = inspect.getframeinfo(inspect.currentframe()).filename
  path = os.path.dirname(os.path.abspath(filename))
  return path

def flatten(output, prefix = "", suffix = ""):
  final = ""
  for i in range(len(output)):
    temp = output[i]
    final += prefix
    for j in range(len(temp)):
      final += temp[j]
    final += suffix
  return final

def ensure(string):
  if (string == None):
    return ""
  if not (type(string) == str):
    return ""
  return string
  
class Object(object):
  def __init__(self):
    self.node = None
    
  def getContent(self):
    return ""
    
  def toString(self, *arguments):
    if (len(arguments) == 0):
      return "("+self.__class__.__name__+")"+str(self)
    other = arguments[0]
    if (other == None):
      return "/NULL/"
    if ((str(type(other)) == "str") or (str(type(other)) == "list")):
      return str(other)
    if not (isinstance(other, Object)):
      return "/INVALID/"
    return other.toString()
    
class Element(Object):
  def __init__(self):
    super(Element, self).__init__()
    self.parent = None
    
  def build(self, owner):
    return True
    
  def getParent(self):
    return self.parent
    
  def getContent(self):
    return ""

class String(Object):
  def __init__(self, content = None):
    super(String, self).__init__()
    self.content = ""
    if (type(content) == str):
      self.content = content
      
  def getContent(self):
    return self.content
      
  def __str__(self):
    return "<\""+self.content+"\">"
    
class List(Element):
  def __init__(self, content = None):
    super(List, self).__init__()
    self.content = []
    if (type(content) == list):
      self.content = content
    else:
      if (type(content) == dict):
        for key in content:
          self.content.append(content[key])
      
  def build(self, owner):
    if not (self.content == None):
      if (type(self.content) == list):
        length = len(self.content)
        for i in range(length):
          if (isinstance(self.content[i], Element)):
            if not (self.content[i].build(owner)):
              return False
    return True
    
  def add(self, content):
    if not (content == None):
      if (type(content) == list):
        length = len(content)
        for i in range(length):
          if not (self.add(content[i])):
            return False
        return True
      elif (isinstance(content, Object)):
        self.content.append(content)
        return True
      else:
        return False
    return False
    
  def getContent(self):
    content = []
    length = len(self.content)
    for i in range(length):
      if (isinstance(self.content[i], Object)):
        content.append(self.content[i])
    return content
    
  def __len__(self):
    return len(self.content)
      
  def __str__(self):
    to = "<["
    length = len(self.content)
    for i in range(length):
      to += self.content[i].toString()
      if not (i == length-1):
        to += ", "
    to += "]>"
    return to
    
class Content(Object):
  def __init__(self, string = String("")):
    super(Content, self).__init__()
    self.string = string
    
  def __str__(self):
    return "<"+self.toString(self.string)+">"
    
class ParentList(List):
  def __init__(self, content = None):
    super(ParentList, self).__init__(content)
    
class Parent(Element):
  def __init__(self):
    super(Parent, self).__init__()
    self.string = String("")
    
  def build(self, owner):
    return True
    
  def __str__(self):
    return "<"+self.toString(self.string)+">"
    
class NamespaceList(List):
  def __init__(self, content = None):
    super(NamespaceList, self).__init__(content)
    
class ModelList(List):
  def __init__(self, content = None):
    super(ModelList, self).__init__(content)
    
class ParameterList(List):
  def __init__(self, content = None):
    super(ParameterList, self).__init__(content)
    
class Parameter(Element):
  def __init__(self):
    super(Parameter, self).__init__()
    self.id = None
    self.type = None
    self.model = None
    self.assignment = None
    
  def build(self, owner):
    return True
    
  def __str__(self):
    return "<"+self.toString(self.id)+","+self.toString(self.type)+","+self.toString(self.model)+">"
    
class RequestList(List):
  def __init__(self, content = None):
    super(RequestList, self).__init__(content)
    
class Request(Element):
  def __init__(self):
    super(Request, self).__init__()
    self.uri = None
    self.id = None
    self.namespace = None
    self.response = None
    self.method = None
    self.parameters = None
    
  def build(self, owner):
    if (owner == None):
      return False
    if ((self.response == None) or (self.namespace == None)):
      return False
    if not (self.namespace.getContent() in owner.context.namespaces):
      return False
    if not (self.namespace.getContent() in owner.namespaces):
      owner.namespaces[self.namespace.getContent()] = {}
    values = {}
    model = {}
    if not (self.response.values == None):
      values = self.response.values.content.string.getContent().strip()
      if not (len(values) == 0):
        if ((values[:1] == "{") or (values[:1] == "[")):
          values = json.loads(values)
    if not (self.response.model == None):
      model = self.response.model.content.string.getContent().strip()
      if not (len(model) == 0):
        if ((model[:1] == "{") or (model[:1] == "[")):
          model = json.loads(model)
    models = []
    models.append("class "+self.id.getContent()+"Model(BaseModel):")
    if (type(model) == dict):
      for key in model:
        models.append(owner.context.root.tab.getContent()+str(key)+": "+str(model[key]))
    elif (type(model) == list):
      for i in range(len(model)):
        models.append(owner.context.root.tab.getContent()+str(model[i]))
    else:
      models.append(owner.context.root.tab.getContent()+str(model))
    if not (self.parameters == None):
      parameters = self.parameters.getContent()
      for i in range(len(parameters)):
        if (parameters[i].model == None):
          continue
        parameter = "class "+parameters[i].type.getContent()+"(BaseModel):"
        if (parameter in models):
          continue
        models.append(parameter)
        model = parameters[i].model.content.string.getContent().strip()
        if not (len(model) == 0):
          if ((model[:1] == "{") or (model[:1] == "[")):
            model = json.loads(model)
        if (type(model) == dict):
          for key in model:
            models.append(owner.context.root.tab.getContent()+str(key)+": "+str(model[key]))
        elif (type(model) == list):
          for i in range(len(model)):
            models.append(owner.context.root.tab.getContent()+str(model[i]))
        else:
          models.append(owner.context.root.tab.getContent()+str(model))
    routers = []
    routers.append("@router."+self.method.getContent()+"(\""+self.uri.getContent()+"\", response_model="+self.response.model.prefix.getContent()+self.namespace.getContent()+"."+self.id.getContent()+"Model"+self.response.model.suffix.getContent()+")")
    parameter = ""
    if not (self.parameters == None):
      parameters = self.parameters.getContent()
      for i in range(len(parameters)):
        if ("." in parameters[i].type.getContent()):
          parameter += " "+parameters[i].id.getContent()+": "+parameters[i].type.getContent()
        else:
          parameter += " "+parameters[i].id.getContent()+": "+self.namespace.getContent()+"."+parameters[i].type.getContent()
        if not (parameters[i].assignment == None):
          parameter += " = "+parameters[i].assignment.getContent()
        parameter += ","
      if (parameter[(len(parameter)-1):] == ","):
        parameter = parameter[:(len(parameter)-1)]
    routers.append("async def "+self.id.getContent()+"Router("+parameter.strip()+"):")
    router = ""
    if (type(values) == dict):
      for value in values:
        router += "\""+str(value)+"\":"+str(values[value])+","
    elif (type(values) == list):
      for i in range(len(values)):
        router += str(values[i])+","
    else:
      router += str(values)
    if (len(router) == 0):
      return False
    if (router[(len(router)-1):] == ","):
      router = router[:(len(router)-1)]
    if not (self.response.preamble == None):
      preambles = self.response.preamble.string.getContent().split("\n")
      for preamble in preambles:
        routers.append(owner.context.root.tab.getContent()+preamble)
    if (type(values) == dict):
      routers.append(owner.context.root.tab.getContent()+"return {"+router+"}")
    elif (type(values) == list):
      routers.append(owner.context.root.tab.getContent()+"return ["+router+"]")
    else:
      routers.append(owner.context.root.tab.getContent()+"return "+router)
    namespace = {}
    namespace["models"] = models
    namespace["routers"] = routers
    for key in namespace:
      if not (key in owner.namespaces[self.namespace.getContent()]):
        owner.namespaces[self.namespace.getContent()][key] = []
      owner.namespaces[self.namespace.getContent()][key] = owner.namespaces[self.namespace.getContent()][key]+namespace[key]
    return True
    
  def __str__(self):
    return "<"+self.toString(self.response)+","+self.toString(self.uri)+","+self.toString(self.id)+","+self.toString(self.namespace)+", "+self.toString(self.method)+", "+self.toString(self.parameters)+">"
    
class Model(Element):
  def __init__(self):
    super(Model, self).__init__()
    self.content = Content(String(""))
    self.prefix = String("")
    self.suffix = String("")
    self.type = None
    self.parents = None
    
  def build(self, owner):
    return True
    
  def __str__(self):
    return "<"+self.toString(self.content)+", "+self.toString(self.prefix)+", "+self.toString(self.suffix)+", "+self.toString(self.type)+", "+self.toString(self.parents)+">"
    
class Values(Element):
  def __init__(self):
    super(Values, self).__init__()
    self.content = Content(String(""))
    
  def build(self, owner):
    return True
    
  def __str__(self):
    return "<"+self.toString(self.content)+">"
    
class Preamble(Object):
  def __init__(self):
    super(Preamble, self).__init__()
    self.string = None
    
  def __str__(self):
    return "<"+self.toString(self.string)+">"
    
class Header(Object):
  def __init__(self):
    super(Header, self).__init__()
    self.string = None
    
  def __str__(self):
    return "<"+self.toString(self.string)+">"
    
class Namespace(Element):
  def __init__(self):
    super(Namespace, self).__init__()
    self.name = String("")
    self.header = None
    self.models = None
    
  def build(self, owner):
    return True
    
  def __str__(self):
    return "<"+self.toString(self.name)+", "+self.toString(self.header)+", "+self.toString(self.models)+">"
    
class Response(Object):
  def __init__(self):
    super(Response, self).__init__()
    self.model = None
    self.values = None
    self.preamble = None
    
  def __str__(self):
    return "<"+self.toString(self.model)+","+self.toString(self.values)+", "+self.toString(self.preamble)+">"

class APIper(Element):
  def __init__(self):
    super(APIper, self).__init__()
    self.root = None
    self.context = None
    self.requests = None
    self.namespaces = {}
    self.tab = String("")
    
  def build(self, owner):
    if not (self.requests == None):
      if not (self.requests.build(owner)):
        return False
      reorganize = {}
      for key in self.namespaces:
        namespace = self.namespaces[key]
        for k in namespace:
          if not (k in reorganize):
            reorganize[k] = {}
            reorganize[k][key] = []
          for i in range(len(namespace[k])):
            if not (key in reorganize[k]):
              reorganize[k][key] = []
            reorganize[k][key].append(namespace[k][i])
      for key in reorganize:
        for k in reorganize[key]:
          path = os.path.join("app", key)
          if not (os.path.isdir(path)):
            os.makedirs(path)
          path = os.path.join(path, k+".py")
          descriptor = open(path, "w")
          if (key == "models"):
            reorganize[key][k] = ["from pydantic import BaseModel"]+reorganize[key][k]
          elif (key == "routers"):
            reorganize[key][k] = ["router = APIRouter()"]+reorganize[key][k]
            reorganize[key][k] = ["current_user = fastapi_users.current_user()"]+reorganize[key][k]
            reorganize[key][k] = ["from app import util"]+reorganize[key][k]
            reorganize[key][k] = ["from ..models import "+k]+reorganize[key][k]
            reorganize[key][k] = ["from ..main import fastapi_users"]+reorganize[key][k]
            reorganize[key][k] = ["from fastapi import APIRouter, Depends"]+reorganize[key][k]
          if (k in self.context.namespaces):
            if not (self.context.namespaces[k].header == None):
              headers = self.context.namespaces[k].header.string.getContent().split("\n")
              for header in headers:
                descriptor.write(header+"\n")
          for i in range(len(reorganize[key][k])):
            descriptor.write(reorganize[key][k][i]+"\n")
          if (key == "models"):
            if (k in self.context.namespaces):
              if not (self.context.namespaces[k].models == None):
                models = self.context.namespaces[k].models.getContent()
                for i in range(len(models)):
                  model = models[i]
                  if (model.type == None):
                    continue
                  parent = ""
                  if not (model.parents == None):
                    parents = model.parents.getContent()
                    for j in range(len(parents)):
                      parent += " "+parents[j].string.getContent()+","
                    if not (len(parent) == 0):
                      if (parent[(len(parent)-1):] == ","):
                        parent = parent[:(len(parent)-1)]
                  descriptor.write("class "+model.type.getContent()+"("+parent.strip()+"):\n")
                  model = model.content.string.getContent().strip()
                  if not (len(model) == 0):
                    if ((model[:1] == "{") or (model[:1] == "[")):
                      model = json.loads(model)
                  if (type(model) == dict):
                    for key in model:
                      descriptor.write(owner.context.root.tab.getContent()+str(key)+": "+str(model[key])+"\n")
                  elif (type(model) == list):
                    for i in range(len(model)):
                      descriptor.write(owner.context.root.tab.getContent()+str(model[i])+"\n")
                  else:
                    descriptor.write(owner.context.root.tab.getContent()+str(model)+"\n")
          descriptor.close()
      return True
    return False
    
  def __str__(self):
    return "<"+self.toString(self.requests)+", "+self.toString(NamespaceList(self.context.namespaces))+">"
  
class Context(Object):
  def __init__(self, data):
    super(Context, self).__init__()
    self.namespaces = {}
    self.data = data
    self.root = None
    self.nodes = {}
    self.tier = 0
    self.any = "any"
    nodeTags = []
    nodeParents = {}
    nodeAttributes = {}
    nodeTags.append("apiper")
    nodeTags.append("namespace")
    nodeTags.append("header")
    nodeTags.append("requests")
    nodeTags.append("request")
    nodeTags.append("response")
    nodeTags.append("models")
    nodeTags.append("model")
    nodeTags.append("values")
    nodeTags.append("content")
    nodeTags.append("preamble")
    nodeTags.append("parameter")
    nodeTags.append("parameters")
    nodeTags.append("parent")
    nodeTags.append("parents")
    nodeTags.append("content")
    nodeParents["content"] = []
    nodeParents["content"].append("model")
    nodeParents["content"].append("values")
    nodeParents["namespace"] = []
    nodeParents["namespace"].append("apiper")
    nodeParents["header"] = []
    nodeParents["header"].append("namespace")
    nodeParents["models"] = []
    nodeParents["models"].append("namespace")
    nodeParents["requests"] = []
    nodeParents["requests"].append("apiper")
    nodeParents["request"] = []
    nodeParents["request"].append("requests")
    nodeParents["response"] = []
    nodeParents["response"].append("request")
    nodeParents["model"] = []
    nodeParents["model"].append("response")
    nodeParents["model"].append("parameter")
    nodeParents["model"].append("models")
    nodeParents["values"] = []
    nodeParents["values"].append("response")
    nodeParents["preamble"] = []
    nodeParents["preamble"].append("response")
    nodeParents["parameters"] = []
    nodeParents["parameters"].append("request")
    nodeParents["parameter"] = []
    nodeParents["parameter"].append("parameters")
    nodeParents["parent"] = []
    nodeParents["parent"].append("parents")
    nodeParents["parents"] = []
    nodeParents["parents"].append("model")
    nodeAttributes["apiper"] = []
    nodeAttributes["apiper"].append(["tab", False])
    nodeAttributes["namespace"] = []
    nodeAttributes["namespace"].append(["name", False])
    nodeAttributes["request"] = []
    nodeAttributes["request"].append(["uri", False])
    nodeAttributes["request"].append(["id", False])
    nodeAttributes["request"].append(["namespace", False])
    nodeAttributes["request"].append(["method", False])
    nodeAttributes["model"] = []
    nodeAttributes["model"].append(["prefix", True])
    nodeAttributes["model"].append(["suffix", True])
    nodeAttributes["model"].append(["type", True])
    nodeAttributes["parameter"] = []
    nodeAttributes["parameter"].append(["id", False])
    nodeAttributes["parameter"].append(["type", False])
    nodeAttributes["parameter"].append(["assignment", True])
    self.nodeTags = nodeTags
    self.nodeParents = nodeParents
    self.nodeAttributes = nodeAttributes
    
  def record(self, node, message):
    print(("  "*self.tier)+node.tag+": "+message)
    
  def log(self, node, message):
    self.record(node, message)
    
  def check(self, node, parent):
    tag = node.tag
    if not (tag in self.nodeTags):
      self.record(node, "Node Tag Error...")
      return False
    if (parent == None):
      if (tag in self.nodeParents):
        self.record(node, "Node Parent Error 1...")
        return False
    else:
      if not (tag in self.nodeParents):
        self.record(node, "Node Parent Error 2...")
        return False
      if not (self.any in self.nodeParents[tag]):
        if not (parent.tag in self.nodeParents[tag]):
          self.record(node, "Node Parent Error 3...")
          return False
    if (tag in self.nodeAttributes):
      attributes = self.nodeAttributes[tag]
      for attribute in attributes:
        optional = attribute[1]
        attribute = attribute[0]
        if not (attribute in node.attrib):
          if not (optional):
            self.record(node, "Node Attribute Error...")
            return False
    return True
    
def handle(context, node, tier, parents):
  parent = parents[len(parents)-1]
  quit = False
  result = True
  tag = node.tag
  element = None
  elements = {}
  output = []
  if (context.check(node, parent)):
    if (tag == "quit"):
      quit = True
      result = False
    elif (tag == "apiper"):
      element = APIper()
      element.context = context
      context.root = element
    elif (tag == "requests"):
      element = RequestList()
    elif (tag == "request"):
      element = Request()
    elif (tag == "response"):
      element = Response()
    elif (tag == "model"):
      element = Model()
    elif (tag == "values"):
      element = Values()
    elif (tag == "preamble"):
      element = Preamble()
    elif (tag == "header"):
      element = Header()
    elif (tag == "namespace"):
      element = Namespace()
    elif (tag == "parameters"):
      element = ParameterList()
    elif (tag == "parameter"):
      element = Parameter()
    elif (tag == "parents"):
      element = ParentList()
    elif (tag == "parent"):
      element = Parent()
    elif (tag == "content"):
      element = Content()
    elif (tag == "models"):
      element = ModelList()
    children = False
    for child in node:
      children = True
      context.tier = tier
      call = handle(context, child, tier+1, parents+[node])
      if not (call[0]):
        result = False
        break
      output.append([ensure(call[1]).strip(), ensure(child.tail).strip()])
      for key in call[2]:
        value = call[2][key]
        if not (value == None):
          for i in range(len(value)):
            if not (value[i] == None):
              if not (child.tag in elements):
                elements[child.tag] = []
              elements[child.tag].append(value[i])
    context.tier = tier
    success = True
    if (tag in context.nodeAttributes):
      if (tag == "request"):
        element.uri = String(node.attrib["uri"])
        element.id = String(node.attrib["id"])
        element.namespace = String(node.attrib["namespace"])
        element.method = String(node.attrib["method"])
        if ("response" in elements):
          for response in elements["response"]:
            element.response = response
            break
          elements["response"] = None
        if ("parameters" in elements):
          for parameters in elements["parameters"]:
            element.parameters = parameters
            break
          elements["parameters"] = None
      elif (tag == "parameter"):
        element.id = String(node.attrib["id"])
        element.type = String(node.attrib["type"])
        if ("assignment" in node.attrib):
          element.assignment = String(node.attrib["assignment"])
        if ("model" in elements):
          for model in elements["model"]:
            element.model = model
            break
          elements["model"] = None
      elif (tag == "model"):
        if ("content" in elements):
          for content in elements["content"]:
            element.content = content
            break
          elements["content"] = None
        if ("parents" in elements):
          for parent in elements["parents"]:
            element.parents = parent
            break
          elements["parents"] = None
        if ("prefix" in node.attrib):
          element.prefix = String(node.attrib["prefix"])
        if ("suffix" in node.attrib):
          element.suffix = String(node.attrib["suffix"])
        if ("type" in node.attrib):
          element.type = String(node.attrib["type"])
      elif (tag == "apiper"):
        element.tab = String(node.attrib["tab"])
        if ("requests" in elements):
          for requests in elements["requests"]:
            element.requests = requests
            break
          elements["requests"] = None
      elif (tag == "namespace"):
        element.name = String(node.attrib["name"])
        if ("models" in elements):
          for models in elements["models"]:
            element.models = models
            break
          elements["models"] = None
        if ("header" in elements):
          for header in elements["header"]:
            element.header = header
            break
          elements["header"] = None
        context.namespaces[element.name.getContent()] = element
      else:
        success = False
    else:
      if (tag == "requests"):
        if ("request" in elements):
          for request in elements["request"]:
            element.add(request)
          elements["request"] = None
      elif (tag == "parameters"):
        if ("parameter" in elements):
          for parameter in elements["parameter"]:
            element.add(parameter)
          elements["parameter"] = None
      elif (tag == "parents"):
        if ("parent" in elements):
          for parent in elements["parent"]:
            element.add(parent)
          elements["parent"] = None
      elif (tag == "models"):
        if ("model" in elements):
          for model in elements["model"]:
            element.add(model)
          elements["model"] = None
      elif (tag == "response"):
        if ("model" in elements):
          for model in elements["model"]:
            element.model = model
            break
          elements["model"] = None
        if ("values" in elements):
          for values in elements["values"]:
            element.values = values
            break
          elements["values"] = None
        if ("preamble" in elements):
          for preamble in elements["preamble"]:
            element.preamble = preamble
            break
          elements["preamble"] = None
      elif (tag == "values"):
        if ("content" in elements):
          for content in elements["content"]:
            element.content = content
            break
          elements["content"] = None
      elif (tag == "preamble"):
        output = ensure(node.text)+flatten(output).strip()
        output = output.strip()
        element.string = String(output)
      elif (tag == "header"):
        output = ensure(node.text)+flatten(output).strip()
        output = output.strip()
        element.string = String(output)
      elif (tag == "content"):
        output = ensure(node.text)+flatten(output).strip()
        output = output.strip()
        element.string = String(output)
      elif (tag == "parent"):
        output = ensure(node.text)+flatten(output).strip()
        output = output.strip()
        element.string = String(output)
      else:
        success = False
    if (success):
      if not (element == None):
        element.node = node
        if not (tag in elements):
          elements[tag] = []
        elements[tag].append(element)
      else:
        if not (children):
          output = ensure(node.text)+flatten(output).strip()
          output = output.strip()
          context.log(node, output+"\n")
    else:
      if not (children):
        output = ensure(node.text)+flatten(output).strip()
        output = output.strip()
        context.log(node, output+"\n")
  else:
    result = False
  if not (result):
    context.log(node, "Error!")
  else:
    context.nodes[node] = element
    if not (element == None):
      parent = get_parent(parents, None)
      if (parent in context.nodes):
        element.parent = context.nodes[parent]
  return [result, output, elements]
  
def run(target, data):
  dictionary = {}
  for i in range(len(data)):
    element = data[i]
    elements = element.split("=")
    if (len(elements) == 2):
      left = elements[0].strip()
      right = elements[1].strip()
      dictionary[left] = right
  tree = xml_tree.parse(target)
  base = tree.getroot()
  if not (base.tag == "apiper"):
    return False
  context = Context(dictionary)
  result = handle(context, base, 0, [None])
  context.log(base, context.toString(context.root))
  if not (context.root == None):
    context.root.context = context
    context.root.build(context.root)
  else:
    return False
  return result[0]
  
if (__name__ == "__main__"):
  result = 0
  arguments = sys.argv
  length = len(arguments)
  if (length > 1):
    data = []
    if (length > 2):
      data = arguments[2:]
    code = run(arguments[1].strip(), data)
    if not (code):
      print("Error!")
      result = -1
  sys.exit(result)
