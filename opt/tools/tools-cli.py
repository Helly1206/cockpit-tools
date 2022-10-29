#!/usr/bin/python3

# -*- coding: utf-8 -*-
#########################################################
# SERVICE : tools-cli.py                                #
#           Commandline interface for cockpit tools     #
#           Adding other web UIs to cockpit             #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
import sys
import os
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import json
import requests
from io import BytesIO
from PIL import Image
from base64 import b64encode

#########################################################

####################### GLOBALS #########################
VERSION       = "0.80"
XML_FILENAME  = "cockpit-tools.xml"
ENCODING      = 'utf-8'
FALLBACK_ICON = '/opt/tools/fallback.png'
#########################################################

###################### FUNCTIONS ########################



#########################################################
# Class : database                                      #
#########################################################
class database(object):
    def __init__(self):
        self.db = {}
        if not self.getXMLpath(False):
            # only create xml if super user, otherwise keep empty
            self.createXML()
            self.getXML()
        else:
            self.getXML()

    def __del__(self):
        del self.db
        self.db = {}

    def __call__(self):
        return self.db

    def update(self):
        self.updateXML()

    def reload(self):
        del self.db
        self.db = {}
        self.getXML()

    def bl(self, val):
        retval = False
        try:
            f = float(val)
            if f > 0:
                retval = True
        except:
            if val.lower() == "true" or val.lower() == "yes" or val.lower() == "1":
                retval = True
        return retval

################## INTERNAL FUNCTIONS ###################

    def gettype(self, text, txtype = True):
        try:
            retval = int(text)
        except:
            try:
                retval = float(text)
            except:
                if text:
                    if text.lower() == "false":
                        retval = False
                    elif text.lower() == "true":
                        retval = True
                    elif txtype:
                        retval = text
                    else:
                        retval = ""
                else:
                    retval = ""

        return retval

    def settype(self, element):
        retval = ""
        if type(element) == bool:
            if element:
                retval = "true"
            else:
                retval = "false"
        elif element != None:
            retval = str(element)

        return retval

    def getXML(self):
        XMLpath = self.getXMLpath()
        try:
            tree = ET.parse(XMLpath)
            root = tree.getroot()
            self.db = self.parseKids(root, True)
        except Exception as e:
            print("Error parsing xml file")
            print("Check XML file syntax for errors")
            print(e)
            exit(1)

    def parseKids(self, item, isRoot = False):
        db = {}
        if self.hasKids(item):
            for kid in item:
                if self.hasKids(kid):
                    db[kid.tag] = self.parseKids(kid)
                else:
                    db.update(self.parseKids(kid))
        elif not isRoot:
            db[item.tag] = self.gettype(item.text)
        return db

    def hasKids(self, item):
        retval = False
        for kid in item:
            retval = True
            break
        return retval

    def updateXML(self):
        db = ET.Element('tools')
        pcomment = self.getXMLcomment("")
        if pcomment:
            comment = ET.Comment(pcomment)
            db.append(comment)
        self.buildXML(db, self.db)

        XMLpath = self.getXMLpath(dowrite = True)

        with open(XMLpath, "w") as xml_file:
            xml_file.write(self.prettify(db))

    def buildXML(self, xmltree, item):
        if isinstance(item, dict):
            for key, value in item.items():
                kid = ET.SubElement(xmltree, key)
                self.buildXML(kid, value)
        else:
            xmltree.text = self.settype(item)

    def createXML(self):
        print("Creating new XML file")
        db = ET.Element('tools')
        comment = ET.Comment("This XML file describes the tools at be displayed in cockpit.\n"
        "            Add a tool to have it displayed on the tools tab.")
        db.append(comment)

        XMLpath = self.getNewXMLpath()

        with open(XMLpath, "w") as xml_file:
            xml_file.write(self.prettify(db))

    def getXMLcomment(self, tag):
        comment = ""
        XMLpath = self.getXMLpath()
        with open(XMLpath, 'r') as xml_file:
            content = xml_file.read()
            if tag:
                xmltag = "<{}>".format(tag)
                xmlend = "</{}>".format(tag)
                begin = content.find(xmltag)
                end = content.find(xmlend)
                content = content[begin:end]
            cmttag = "<!--"
            cmtend = "-->"
            begin = content.find(cmttag)
            end = content.find(cmtend)
            if (begin > -1) and (end > -1):
                comment = content[begin+len(cmttag):end]
        return comment

    def prettify(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ET.tostring(elem, ENCODING)
        reparsed = parseString(rough_string)
        return reparsed.toprettyxml(indent="\t").replace('<?xml version="1.0" ?>','<?xml version="1.0" encoding="%s"?>' % ENCODING)

    def getXMLpath(self, doexit = True, dowrite = False):
        etcpath = "/etc/"
        XMLpath = ""
        # first look in etc
        if os.path.isfile(os.path.join(etcpath,XML_FILENAME)):
            XMLpath = os.path.join(etcpath,XML_FILENAME)
            if dowrite and not os.access(XMLpath, os.W_OK):
                print("No valid writable XML file location found")
                print("XML file cannot be written, please run as super user")
                if doexit:
                    exit(1)
        else: # Only allow etc location
            print("No XML file found")
            if doexit:
                exit(1)
        return XMLpath

    def getNewXMLpath(self):
        etcpath = "/etc/"
        XMLpath = ""
        # first look in etc
        if os.path.exists(etcpath):
            if os.access(etcpath, os.W_OK):
                XMLpath = os.path.join(etcpath,XML_FILENAME)
        if (not XMLpath):
            print("No valid writable XML file location found")
            print("XML file cannot be created, please run as super user")
            exit(1)
        return XMLpath


#########################################################

#########################################################
# Class : toolscli                                      #
#########################################################
class toolscli(object):
    def __init__(self):
        self.name = ""

    def __del__(self):
        pass

    def __str__(self):
        return "{}: commandline interface for syncwatch".format(self.name)

    def __repr__(self):
        return self.__str__()

    def run(self, argv):
        if len(os.path.split(argv[0])) > 1:
            self.name = os.path.split(argv[0])[1]
        else:
            self.name = argv[0]

        self.db = database()

        for arg in argv:
            if arg[0] == "-":
                if arg == "-h" or arg == "--help":
                    self.printHelp()
                    exit()
                elif arg == "-v" or arg == "--version":
                    print(self)
                    print("Version: {}".format(VERSION))
                    exit()
                else:
                    self.parseError(arg)
        if len(argv) < 2:
            self.lstExt()
        elif argv[1] == "add":
            icon = ""
            ref = ""
            opt = argv[1]
            if len(argv) < 3:
                opt += " <name>"
                self.parseError(opt)
            elif len(argv) < 4:
                opt += " <name> <options>"
                self.parseError(opt)
            elif len(argv) > 4:
                icon = argv[3]
                ref = argv[4]
            else:
                try:
                    opts = json.loads(argv[3])
                    if 'icon' in opts:
                        icon = opts['icon']
                    if 'ref' in opts:
                        ref = opts['ref']
                except:
                    self.parseError("Invalid JSON format")
            self.tadd(argv[2], icon, ref)
        elif argv[1] == "del":
            opt = argv[1]
            if len(argv) < 3:
                opt += " <name>"
                self.parseError(opt)
            self.tdel(argv[2])
        elif argv[1] == "shw":
            opt = argv[1]
            if len(argv) < 3:
                opt += " <name>"
                self.parseError(opt)
            self.shw(argv[2])
        elif argv[1] == "lst":
            self.lst()
        else:
            self.parseError(argv[1])

    def printHelp(self):
        print(self)
        print("Usage:")
        print("    {} {}".format(self.name, "<argument> <name> <options>"))
        print("    <arguments>")
        print("        add           : adds/ edits tool <name> with <options>")
        print("        del           : deletes tool <name>")
        print("        shw           : shows options for tool <name>")
        print("        lst           : list tools and options")
        print("        <no arguments>: lists all tools in json")
        print("")
        print("<options> may be entered in JSON or as <name> <icon> <ref> as arguments")
        print("JSON options may be entered as single JSON string using full name, e.g.")
        print("{}".format(self.name), end="")
        print(" add tool1 \"{'ref': 'http://www.example.com'}\"")
        print("Mind the double quotes to bind the JSON string.")
        print("JSON options:")
        print("icon: icon ad file location or URL")
        print("ref: link to webpage of tool")

    def parseError(self, opt = ""):
        print(self)
        print("Invalid option entered")
        if opt:
            print(opt)
        print("Enter '{} -h' for help".format(self.name))
        exit(1)

    def lst(self):
        for item, value in self.db().items():
            print("Tool name: " + item)
            print("    icon : " + value['icon'])
            print("    ref  : " + value['ref'])

    def lstExt(self):
        tools = {}
        for item, value in self.db().items():
            tool = {}
            origIcon = self.openImage(value['icon'])
            icon = self.htmlImage(self.convertImage(origIcon))
            tool['icon'] = icon
            tool['ref'] = value['ref']
            tools[item] = tool

        print(json.dumps(tools))

    def tadd(self, name, icon, ref):
        item = self.getItem(name)
        if not item:
            item = {}
            item['icon'] = icon
            item['ref'] = ref
            self.db()[name] = item
        else:
            if icon:
                item['icon'] = icon
            if ref:
                item['ref'] = ref
        self.db.update()

    def tdel(self, name):
        item = self.getItem(name)
        if not item:
            self.parseError("<name> doesn't exist")
        del self.db()[name]
        self.db.update()

    def shw(self, name):
        item = self.getItem(name)
        if not item:
            self.parseError("<name> doesn't exist")
        print(json.dumps(item))

    def getItem(self, name):
        itemvals = {}

        for item, value in self.db().items():
            if name.strip() == item.strip():
                itemvals = value
                break

        return itemvals

    def openImage(self, icon):
        img = None

        if icon.startswith("http://") or icon.startswith("https://"):
            #download image
            try:
                response = requests.get(icon)
                img = Image.open(BytesIO(response.content))
            except:
                pass
        else:
            try:
                img = Image.open(icon)
            except:
                pass
        if not img:
            img = Image.open(FALLBACK_ICON)
        return img

    def convertImage(self, img):
        img2 = None
        if img:
            basesize = 128
            if img.size[0] > img.size[1]:
                wsize = basesize
                wpercent = (basesize/float(img.size[0]))
                hsize = int((float(img.size[1])*float(wpercent)))
            else:
                hsize = basesize
                hpercent = (basesize/float(img.size[1]))
                wsize = int((float(img.size[0])*float(hpercent)))
            img2 = img.resize((wsize, hsize), Image.Resampling.LANCZOS)
            img3 = Image.new('RGBA', (basesize, basesize), (0, 0, 0, 0))
            upper = (128 - img2.size[1]) // 2
            left = (128 - img2.size[0]) // 2
            img3.paste(img2, (left, upper))
        return img3

    def htmlImage(self, img):
        imgCode = None

        output = BytesIO()
        img.save(output, 'PNG')
        imgCode = output.getvalue()
        output.close()
        encoded = b64encode(imgCode) # Creates a bytes object
        return 'data:image/png;base64,{}'.format(encoded.decode())

######################### MAIN ##########################
if __name__ == "__main__":
    toolscli().run(sys.argv)
