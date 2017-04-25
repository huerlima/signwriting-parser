#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime
import sys
import urllib2
import xml.sax
import copy
from optparse import OptionParser
from xml.sax import make_parser

from signWritingParserClasses import *

defaultEncoding = "UTF-8"
options = None


def check_args(args, option_parser):
    if len(args) != 0:
        option_parser.error("incorrect number of arguments %d, detected arguments being %s" % (len(args), args))
        sys.exit()


def add_options_to_option_parser(option_parser):
    option_parser.add_option("-E", "--encoding", default=defaultEncoding, dest="encoding",
                             help="encoding [" + defaultEncoding + "]")
    option_parser.add_option("-f", "--spmlFile", dest="spml", help="pass a spml File")
    option_parser.add_option("--downloadSource",
                             default="http://www.signbank.org/SignPuddle1.5/export.php?ui=8&sgn=53&ex_source=All&action=Download",
                             dest="downloadSource",
                             help="If no SPML file is provided, we download it from here  [http://www.signbank.org/SignPuddle1.5/export.php?ui=8&sgn=53&ex_source=All&action=Download]")
    option_parser.add_option("--modality", dest="modality",
                             help="provide a comma-separated list of modalities that will be extracted. ex: fingerorientation,palmorientation,handshape")

    option_parser.add_option("--vocabFile", dest="vocab", help="pass a vocab File")
    option_parser.add_option("--modality2", dest="modality2",
                             help="choose a second specific modality [headface|hand|mov]")
    option_parser.add_option("--modality3", dest="modality3",
                             help="choose a third specific modality [headface|hand|mov]")
    option_parser.add_option("--minFrequency", dest="minFrequency", help="give a minimum Frequency. implies combination")
    option_parser.add_option("-r", "--rotInvariant", action="store_true", dest="rotInvariant",
                             help="perform calculation rotation invariant (consider only first 4 letters of id)")
    option_parser.add_option("--combKeys", action="store_true", dest="combinationKeys",
                             help="return combination keys. Needs --combination.")
    option_parser.add_option("--rotHand", action="store_true", dest="rotHand",
                             help="perform handshape calculation rotation invariant (consider only first 4 letters of id)")
    option_parser.add_option("-c", "--combination", action="store_true", dest="combination",
                             help="output combination statistics")
    option_parser.add_option("--movMappingImages", action="store_true", dest="generateImagesToCheckMovementMapping",
                             help="Generates controll images to check the movmement mapping functionality.")
    option_parser.add_option("--searchInText", action="store_true", dest="searchInText",
                             help="Searches the vocabulary entries also in the text tag of the sgml file.")
    option_parser.add_option("--useEmptySubunitModel", action="store_true", dest="emptySubunit",
                             help="When an annotation doesn't contain the specific modality required emptySubunits are returned (ie. no-movements).")
    option_parser.add_option("--convertGlossSpace2Minus", action="store_true", dest="glossSpace",
                             help="gloss 'fuer uns' will be returned as 'fuer-uns'.")
    option_parser.add_option("--backgroundModel", action="store_true", dest="backgroundModel",
                             help="Will return a background model for each vocabulary entry.")
    option_parser.add_option("--restrictSubunitsFile", dest="restrictSubunits",
                             help="Give a File, which lists all the allowed subunits. everything else is deleted from output.")
    option_parser.add_option("--addInnerCoarticulation", action="store_true", dest="addInnerCoarticulation",
                             help="When there are two movements annotated in the same direction, an inner coarticulation in the opposite direction will get inserted, ex: down down -> down up down.")
    option_parser.add_option("--mapMovementSize", action="store_true", dest="mapMovementSize",
                             help="Different sizes are mapped to a uniform size.")
    option_parser.add_option("--buildFromBasic", action="store_true", dest="buildFromBasic",
                             help="Complex movements are split up in basic building movements.")
    option_parser.add_option("--mapArrows", action="store_true", dest="mapArrows",
                             help="Visually equal movements, having a different transcription, are mapped together.")
    option_parser.add_option("--bothHands", action="store_true", dest="bothHands",
                             help="Consider both hands for generating transcriptions.")
    option_parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Verbose output.")


class XmlResultHandler(xml.sax.ContentHandler):
    search = ""
    found = 0
    buf = []
    currTranscription = []
    currCode = ""
    currText = []
    content = {}
    currID = ""
    # this describes fsw: formal sign writing
    code = re.compile(
        r'^(A(S[123][0-9a-f]{2}[0-5][0-9a-f])+)?[BLMR]([0-9]{3}x[0-9]{3})(S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*$')

    def __init__(self):
        self.currTranscription = []
        self.currText = []
        self.content = {}
        self.content.clear()
        self.currID = ""
        pass

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attributes):
        if name == "entry":
            self.currID = attributes.get('id', "")
            self.currCode = ""
            self.currText = []
            self.currTranscription = []
        if name == "term":
            self.buf = []
        if name == "text":
            self.buf = []
        if self.currID not in self.content and self.currID != "":
            self.content.setdefault(self.currID, {})

    def endElement(self, name):
        if name == "term":
            # two cases: either it is a description in the form M
            if self.code.search(" ".join(self.buf)) is not None:
                assert len(self.buf) == 1, "Error This is not a valid Code."

                self.currCode = self.buf[0]
            else:
                self.currTranscription.extend(self.buf)
            self.buf = []
        if name == "text":
            self.currText.append(self.buf)
            self.buf = []
        if name == "entry":
            self.content[self.currID] = {
                "fswcode": copy.deepcopy(self.currCode),
                "transcription": self.currTranscription,
                "text": self.currText,
                "subunits": {
                    "hands": {
                        "right": {
                            "shape": [], "fingerorientation": [], "palmorientation": []
                        }, "left": {
                            "shape": [], "fingerorientation": [], "palmorientation": []
                        }
                    }
                }
            }

        pass

    def print_frames(self):
        for i in self.frames:
            print ""
            for key in i:
                print key, i[key],

    def characters(self, data):
        pass
        self.buf.append(data)


def parse_spml(path):
    xml_resultparser = make_parser()
    res = XmlResultHandler()
    xml_resultparser.setContentHandler(res)
    infile = open(path)
    content = infile.read()
    infile.close()
    xml_resultparser.feed(content)
    xml_resultparser.close()
    return res


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                     (bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(response, chunk_size=8192, report_hook=None):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0
    data = []

    while 1:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        data += chunk
        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)

    return "".join(data)


def main(argv):
    usage = "usage: %prog [options]"
    option_parser = OptionParser(usage=usage)
    add_options_to_option_parser(option_parser)
    global options
    (options, args) = option_parser.parse_args()
    check_args(args, option_parser)
    if options.spml is None:
        if options.verbose:
            print "downloading lexicon from", options.downloadSource
        response = urllib2.urlopen(options.downloadSource)
        now = datetime.datetime.now()
        options.spml = "SignPuddle-" + now.strftime("%Y-%m-%d") + ".spml"
        spml = open("SignPuddle-" + now.strftime("%Y-%m-%d") + ".spml", "w")
        html = chunk_read(response, report_hook=chunk_report)
        spml.write(html)
        spml.close()

    if options.verbose:
        print "parsing spml file."
    spmldict = parse_spml(options.spml).content

    if options.verbose:
        print "extracting subunits"

    spmldict = get_subunits(spmldict, options.verbose)

    for id in spmldict:
        if (spmldict[id]["subunits"]["hands"] != []):
            for orth in spmldict[id]["transcription"]:
                if orth[0:4] == "rwth":
                    orth = " ".join(spmldict[id]["text"][0])
                print  orth.encode('utf8'), "#",
                for (index, shape) in enumerate(spmldict[id]["subunits"]["hands"]["right"]["shape"]):
                    print  "%s-F%s-P%s" % (
                        shape, spmldict[id]["subunits"]["hands"]["right"]["fingerorientation"][index],
                        spmldict[id]["subunits"]["hands"]["right"]["palmorientation"][index]),
                print ""


### MAIN ###
if (__name__ == "__main__"):
    main(sys.argv)

