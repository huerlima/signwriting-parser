#!/usr/bin/env python
# -*- coding: utf-8 -*-

from signWritingParserHelpers import *


##################################################################

# /**
# * @brief convert fsw to ksw
# * @param $fsw input fsw string
# * @return ksw text and x-y coordinates
# * @ingroup helpers
# */
def fsw2ksw(fsw):
    segments = fsw.split(' ')
    segsout = []
    re.IGNORECASE
    pattern = '([BLMR]|S[123][0-9a-f]{2}[0-5][0-9a-f])[0-9]{3}x[0-9]{3}'
    pattern = '(S[123][0-9a-f]{2}[0-5][0-9a-f])[0-9]{3}x[0-9]{3}'
    for fsw in segments:
        input_string = ''
        matches = []
        for outermatch in re.finditer(pattern, fsw):
            matches.append(outermatch.group(0))
        for strng in matches:
            leng = len(strng)
            pre = strng[0:leng - 7]
            coord = str2coordinates(strng[leng - 7:leng])
            coord[0] -= 500
            coord[1] -= 500
            input_string += strng
            segsout.append({"ksw": pre, "x": coord[0], "y": coord[1]})
    return segsout


#############################################################

# /**
# * @brief check if a hand subunit is a right hand
# * @param $subunit input ksw string
# * @return True/False
# * @ingroup subunitprocessing
# */
def is_right_hand(subunit):
    # print subunit, subunit[1]
    # 0-7 rechts
    # 8-f links
    subunit = subunit[5]
    return dig1smaller(subunit, 8)


#############################################################

# /**
# * @brief check if a hand subunit is a left hand
# * @param $subunit input ksw string
# * @return True/False
# * @ingroup subunitprocessing
# */
def is_left_hand(subunit):
    if right_hand(subunit):
        return False
    else:
        return True

#############################################################

# /**
# * @brief return a mirrored version of a subunit
# * @param $ksw input ksw string
# * @return mirrored ksw string
# * @ingroup subunitprocessing
# */
def mirror_subunit(ksw):
    # add 8 to the last digit, overflow normally at f, but then disregard the overflown digit
    ksw = list(ksw)
    ksw[-1] = mirror(ksw[-1])
    return "".join(ksw)


#############################################################

# /**
# * @brief finds the orientation of the extended fingers
# * @param $ksw input ksw string
# * @return string indicating the extended finger orientation of the hand
# * @ingroup subunitprocessing
# */
def get_finger_orientation(ksw):
    assert what_modality(ksw) == "hands", "current subunit is no hand, we cannot determine fingerorientation"

    right_hand_up_left_plane = ["up", "upleft", "left", "downleft", "down", "downright", "right", "upright"]
    left_hand_up_left_plane = ["upleft", "left", "downleft", "down", "downright", "right", "upright", "up"]
    left_hand_up_left_plane.reverse()
    right_hand_front_left_plane = ["front", "frontleft", "left", "backleft", "back", "backright", "right", "frontright"]
    left_hand_front_left_plane = ["frontleft", "left", "backleft", "back", "backright", "right", "frontright", "front"]
    left_hand_front_left_plane.reverse()
    if dig1smaller(int(ksw[4:6], 16), int('30', 16)):
        if is_left_hand(ksw):
            return left_hand_up_left_plane[int(ksw[-1], 16) - 8]
        else:
            return right_hand_up_left_plane[int(ksw[-1], 16)]
    else:
        if is_left_hand(ksw):
            return left_hand_front_left_plane[int(ksw[-1], 16) - 8]
        else:
            return right_hand_front_left_plane[int(ksw[-1], 16)]


#############################################################
# /**
# * @brief finds the orientation of the hand palm
# * @param $ksw input ksw string
# * @return string indicating the palm orientation of the hand
# * @ingroup subunitprocessing
# */
def get_palm_orientation(ksw):
    assert what_modality(ksw) == "hands", "current subunit is no hand, how should we determine fingerorientation"

    # the last two digits are needed to be looked at:

    # number:meaning
    # 10:left
    # 11:downleft
    # 12:down
    # 13:downright
    # 14:right
    # 15:upright
    # 16:up
    # 17:upleft

    up_left_plane = ["left", "downleft", "down", "downright", "right", "upright", "up", "upleft"]

    # 40:left
    # 41:backleft
    # 42:back
    # 43:backright
    # 44:right
    # 45:frontright
    # 46:front
    # 47:frontleft
    front_left_plane = ["left", "backleft", "back", "backright", "right", "frontright", "front", "frontleft"]

    # 0x:back
    # 2x:front
    # 3x:up
    # 5x:down
    info = "RIGHT"
    if is_left_hand(ksw):
        ksw = mirror_subunit(ksw)

        # 18:right
        # 19:downright
        # 1a:down
        # 1b:downleft
        # 1c:left
        # 1d:upleft
        # 1e:up
        # 1f:upright
        up_left_plane = ["upright", "up", "upleft", "left", "downleft", "down", "downright", "right"]

        # 48:right
        # 49:backright
        # 4a:back
        # 4b:backleft
        # 4c:left
        # 4d:frontleft
        # 4e:front
        # 4f:frontright
        front_left_plane = ["frontright", "front", "frontleft", "left", "backleft", "back", "backright", "right"]
        up_left_plane.reverse()
        front_left_plane.reverse()
        info = "LEFT"
    assert int(ksw[ -2]) < 8, \
        "bug in the code? right hands should always have a last number < 8 and we are mirroring a left hand. the actual last number is %s" % \
                             ksw[-1]

    if ksw[-2] == '0':
        return "back"
    elif ksw[-2] == '2':
        return "front"
    elif ksw[-2] == '3':
        return "up"
    elif ksw[-2] == '5':
        return "down"
    elif ksw[-2] == '1':
        info += " 1x " + ksw[-1] + " "
        return up_left_plane[int(ksw[-1])]
    elif ksw[-2] == '4':
        return front_left_plane[int(ksw[-1])]
    else:
        print "ERROR we shouldn't reach this point"
        sys.exit()


#############################################################

# /**
# * @brief extracts the hand shape
# * @param $ksw input ksw string
# * @return string indicating the shape of the hand
# * @ingroup subunitprocessing
# */
def get_handshape(ksw):
    assert what_modality(ksw) == "hands", "current subunit is no hand, how should we determine hand shape"
    hsmapping = {"S100": "index", "S101": "d", "S102": "d/index", "S103": "d", "S104": "d", "S105": "d",
                 "S106": "index_hook", "S107": "index_hook", "S108": "index_hook", "S109": "index_hook",
                 "S10a": "index_hook", "S10b": "index_flex", "S10c": "index_flex", "S10d": "index_flex", "S10e": "v",
                 "S10f": "v", "S110": "v_hook", "S111": "s", "S112": "v_flex", "S113": "k/v/v_flex",
                 "S114": "k/v/v_flex", "S115": "h", "S116": "h/h_hook", "S117": "h/h_hook", "S118": "h_hook",
                 "S119": "h/n", "S11a": "r", "S11b": "r", "S11c": "r", "S11d": "r", "S11e": "3", "S11f": "3",
                 "S120": "3", "S121": "3_hook", "S122": "3_hook", "S123": "v_flex", "S124": "k", "S125": "k",
                 "S126": "3", "S127": "k/3", "S128": "3_hook", "S129": "obaby_double", "S12a": "obaby_double",
                 "S12b": "h/n", "S12c": "k", "S12d": "h_thumb", "S12e": "h", "S12f": "h", "S130": "index",
                 "S131": "middle", "S132": "n", "S133": "r", "S134": "h_thumb", "S135": "cbaby", "S136": "index",
                 "S137": "cbaby/middle", "S138": "d", "S139": "d", "S13a": "index", "S13b": "middle", "S13c": "middle",
                 "S13d": "h/n", "S13e": "n", "S13f": "n", "S140": "k", "S141": "middle", "S142": "k", "S143": "middle",
                 "S144": "4", "S145": "ae/4/m/spoon", "S146": "m/spoon", "S147": "b_nothumb", "S148": "b_nothumb",
                 "S149": "m", "S14a": "e", "S14b": "ital_nothumb", "S14c": "5", "S14d": "5", "S14e": "ae/ae_thumb",
                 "S14f": "ae/ae_thumb", "S150": "ae", "S151": "ae", "S152": "5/4", "S153": "ae/c", "S154": "ae/c",
                 "S155": "ae/c", "S156": "ae/c/cbaby", "S157": "ital_open", "S158": "ital_thumb",
                 "S159": "ital_nothumb", "S15a": "b", "S15b": "b", "S15c": "b", "S15d": "b_thumb", "S15e": "b_thumb",
                 "S15f": "b_thumb", "S160": "ital_open", "S161": "b_thumb/2", "S162": "b", "S166": "by/ae",
                 "S167": "by", "S16a": "s", "S16b": "e", "S16c": "c", "S16d": "c", "S16e": "spoon", "S16f": "spoon",
                 "S170": "spoon", "S171": "spoon", "S172": "c", "S173": "c", "S174": "s/e/a", "S175": "s/a",
                 "S176": "o", "S177": "o", "S178": "ital_thumb", "S179": "ital_nothumb", "S17a": "c",
                 "S17b": "ital_open", "S17c": "ital_open", "S17d": "ital_open", "S17e": "ital", "S17f": "ital_thumb",
                 "S180": "ital_thumb", "S181": "spoon", "S182": "ital_nothumb", "S183": "ital_nothumb", "S185": "ital",
                 "S186": "w", "S187": "6", "S188": "w", "S189": "6", "S18a": "si", "S18b": "w", "S18c": "si",
                 "S18d": "m", "S18f": "ae_thumb", "S190": "ae_thumb", "S192": "i", "S193": "i", "S194": "o/i",
                 "S195": "o/i", "S198": "i", "S19a": "y", "S19b": "y", "S19c": "fly", "S19d": "fly",
                 "S1a0": "fly_nothumb", "S1a1": "fly_nothumb", "S1a2": "fly_nothumb/fly", "S1a3": "fly_nothumb",
                 "S1a4": "7", "S1a5": "7", "S1a6": "7", "S1a8": "7", "S1b0": "si", "S1ba": "8", "S1bb": "8",
                 "S1bc": "8", "S1c0": "jesus_thumb", "S1c1": "jesus_thumb", "S1c2": "8", "S1c3": "8", "S1c5": "jesus",
                 "S1c6": "middle", "S1c7": "middle", "S1c9": "middle", "S1cd": "f", "S1ce": "f", "S1cf": "f",
                 "S1d0": "f_open", "S1d1": "f_open", "S1d2": "f", "S1d3": "f", "S1d4": "f", "S1d5": "f/obaby",
                 "S1da": "f", "S1dc": "2", "S1de": "2", "S1df": "index", "S1e1": "l_hook", "S1e2": "l_hook/cbaby",
                 "S1e3": "2", "S1e4": "2", "S1e5": "l_hook", "S1e6": "write", "S1e7": "write/a/s", "S1e8": "t",
                 "S1ea": "write", "S1eb": "obaby", "S1ec": "cbaby", "S1ed": "cbaby", "S1ee": "cbaby/g/2", "S1ef": "g",
                 "S1f0": "g", "S1f1": "g", "S1f2": "t", "S1f3": "t", "S1f4": "pincet", "S1f5": "1", "S1f6": "1",
                 "S1f7": "a", "S1f8": "a", "S1f9": "a", "S1fa": "s/a", "S1fb": "a/t", "S1fe": "n", "S1ff": "s",
                 "S200": "m/a", "S202": "e", "S203": "s", "S204": "s"}

    if ksw[0:4] in hsmapping:
        return hsmapping[ksw[0:4]]
    else:
        return None

#############################################################

# /**
# * @brief finds the broad modality of a ksw string
# * @param $ksw input ksw string
# * @return string indicating the modality [head&faces|hands|movement|fingermovement|body|dynamics]
# * @ingroup subunitprocessing
# */
def what_modality(ksw):
    symbol_key = ksw[1:4]
    if (dig1smaller_eq(symbol_key, '36c') and dig1smaller_eq('2ff', symbol_key)):
        return "head&faces"
    elif (dig1smaller_eq(symbol_key, '204') and dig1smaller_eq('100', symbol_key)):
        return "hands"
    elif (dig1smaller_eq(symbol_key, '2f6') and dig1smaller_eq('22a', symbol_key)):
        return "movement"
    elif (dig1smaller_eq(symbol_key, '215') and dig1smaller_eq('205', symbol_key)):
        return "contacts"
    elif (dig1smaller_eq(symbol_key, '229') and dig1smaller_eq('216', symbol_key)):
        return "fingermovement"
    elif (dig1smaller_eq(symbol_key, '37e') and dig1smaller_eq('36d', symbol_key)):
        return "body"
    elif (dig1smaller_eq(symbol_key, '2fe') and dig1smaller_eq('2f7', symbol_key)):
        return "dynamics"
    else:
        return None


#################################################################
# /**
# * @brief get subunits
# * @param $spml dictionary contains all entries
# * @param $modalities list containing the modalities to be extracted
# * @ingroup mainfunction
# */
def get_subunits(spml, verbose):
    for id in spml:
        assert len(spml[id]) >= 3, "not a valid entry"
        if verbose:
            print id, spml[id]
            print "%10s %10s %10s %15s %15s %10s %10s %10s %10s" %("ksw", "modality", "side", "fingerorient", "palmorient", "shape", "xcoord", "ycoord", "entry")

        fsw = spml[id]["fswcode"]
        transcription = spml[id]["transcription"]
        fswclusters = fsw2ksw(fsw)
        for part in fswclusters:
            ksw = part["ksw"]
            xcoord = part["x"]
            ycoord = part["y"]
            modality = what_modality(ksw)
            side = ""
            finger_orientation = ""
            palm_orientation = ""
            shape = ""
            # currently only hands will be output
            # todo: add other modalities
            if modality == "hands":
                shape = get_handshape(ksw)
                finger_orientation = get_finger_orientation(ksw)
                palm_orientation = get_palm_orientation(ksw)
                if is_right_hand(ksw):
                    side = "right"
                else:
                    side = "left"

                spml[id]["subunits"]["hands"][side]["shape"].append(shape)
                spml[id]["subunits"]["hands"][side]["fingerorientation"].append(finger_orientation)
                spml[id]["subunits"]["hands"][side]["palmorientation"].append(palm_orientation)

            if verbose:
                for word in transcription:
                    #print "%10s %10s %10s %10s %10s %10s %10s %10s %10s" %(unicode(word).encode('utf8'), modality, side, finger_orientation, palm_orientation, shape, ksw, xcoord, ycoord)
                    print "%10s %10s %10s %15s %15s %10s %10s %10s %10s" % (unicode(ksw).encode('utf8'), modality, side, finger_orientation, palm_orientation, shape, xcoord, ycoord, unicode(word).encode('utf8'))



    return spml

##################################################################
