#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

typesMap = ['others', 'head', 'hand', 'mov', 'contact']
typesDic = {'others': 0, 'head': 1, 'hand': 2, 'mov': 3, 'contact': 4}

##################################################################
# /**
# * @brief test if text is Formal SignWriting
# * @param $text character string
# * @return boolean value if text is Formal SignWriting with regular numbers
# * @ingroup fre
# */
def fsw_text(text):
    fsw_sym = 'S[123][0-9a-f]{2}[0-5][0-9a-f]'
    fsw_coord = '[0-9]{3}x[0-9]{3}'
    fsw_word = '(A(' + fsw_sym + ')+)?[BLMR](' + fsw_coord + ')(' + fsw_sym + fsw_coord + ')*'
    fsw_punc = 'S38[7-9ab][0-5][0-9a-f]' + fsw_coord
    fsw_pattern = '^(' + fsw_word + '|' + fsw_punc + ')( ' + fsw_word + '| ' + fsw_punc + ')*$'
    re.IGNORECASE
    # print fsw_pattern
    matches = re.search(fsw_pattern, text)
    if matches:
        if text == matches.group():
            return 1
    return 0

##################################################################
# /**
# * @brief irregular coordinate string to array of x,y values
# * @param $str  coordinate string centered on 0x0
# * @return an array of x,y values
# * @ingroup num
# */
def str2coordinates(str):
    str = re.sub('n', '-', str)
    parts = str.split('x')
    coord = []
    for part in parts:
        coord.append(int(part))
    return coord


##################################################################
# /**
# * @brief x,y values to irregular coordinate string
# * @param $x X value
# * @param $y Y value
# * @return a coordinate string centered on 0x0
# * @ingroup num
# */
def coordinates2str(x, y):
    strng = ''
    if (x < 0): strng += 'n'
    strng += str(abs(x))
    strng += 'x'
    if (y < 0): strng += 'n'
    strng += str(abs(y))
    return strng


##################################################################

# /**
# * @brief convert fsw to ksw
# * @param $fsw input fsw string
# * @return ksw text
# * @ingroup conv
# */
def fsw2ksw(fsw):
    segments = fsw.split(' ')
    segsout = []
    re.IGNORECASE
    pattern = '([BLMR]|S[123][0-9a-f]{2}[0-5][0-9a-f])[0-9]{3}x[0-9]{3}'
    pattern = '(S[123][0-9a-f]{2}[0-5][0-9a-f])[0-9]{3}x[0-9]{3}'
    for fsw in segments:
        input = ''
        output = ''
        matches = []
        for outermatch in re.finditer(pattern, fsw):
            matches.append(outermatch.group(0))
        # print matches
        for strng in matches:
            # print strng
            leng = len(strng)
            pre = strng[0:leng - 7]
            # print strng[leng-7:leng]
            coord = str2coordinates(strng[leng - 7:leng])
            coord[0] -= 500
            coord[1] -= 500
            input += strng
            segsout.append([pre, coord[0], coord[1]])
            output += pre + coordinates2str(coord[0], coord[1])
            # print output
            # segsout.append(re.sub(input,output,fsw))
            #  print segsout
    return segsout


##################################################################
# /**
# * @brief converts a hex number to base 10
# * @param $dig input hex char
# * @return integer value
# * @ingroup conv
# */
def hex2int(dig):
    if dig == 'a':
        return 10
    elif dig == 'b':
        return 11
    elif dig == 'c':
        return 12
    elif dig == 'd':
        return 13
    elif dig == 'e':
        return 14
    elif dig == 'f':
        return 15
    else:
        return int(dig)

##################################################################
# /**
# * @brief converts a base 10 to a hex number
# * @param $dig input integer
# * @return hex char
# * @ingroup conv
# */
def int2hex(dig):
    #    print dig
    # returns hex value without keeping track of overflows
    dig = int(dig)
    if dig == 10:
        return 'a'
    elif dig == 11:
        return 'b'
    elif dig == 12:
        return 'c'
    elif dig == 13:
        return 'd'
    elif dig == 14:
        return 'e'
    elif dig == 15:
        return 'f'
    elif dig > 15:
        return int2hex(dig - 16)
    else:
        return str(dig)


##################################################################
def dig1smaller(dig1, dig2):
    if (hex2int(dig1) < hex2int(dig2)):
        return 1
    else:
        return 0


##################################################################
def dig1smaller_eq(key, val):
    is_small = 0
    # print "FirstSmaller: ",key, val
    if dig1smaller(key[0], val[0]):
        is_small = 1
        # print "first"
    elif key[0] == val[0]:
        if dig1smaller(key[1], val[1]):
            is_small = 1
            # print "sec"
        elif key[1] == val[1] and dig1smaller(key[2], val[2]):
            is_small = 1
            # print "third"
        elif key[1] == val[1] and key[2] == val[2]:
            is_small = 1
            # print "four"
    # print is_small
    return is_small


##################################################################
# /**
# * @brief estimates the subunit type of a ksw code
# * @param $symbol_key ksw input code
# * @return integer representing the type
# * @ingroup helpers
# */
def what_type(symbol_key):
    symbol_key = symbol_key[1:4]
    if dig1smaller_eq(symbol_key, '36c') and dig1smaller_eq('2ff', symbol_key):
        # HEAD &Face
        return typesDic["head"]
    elif dig1smaller_eq(symbol_key, '204') and dig1smaller_eq('100', symbol_key):
        # HAND
        return typesDic["hand"]
    elif dig1smaller_eq(symbol_key, '2f6') and dig1smaller_eq('22a', symbol_key):
        return typesDic["mov"]  # Movement
    elif dig1smaller_eq(symbol_key, '215') and dig1smaller_eq('205', symbol_key):
        return typesDic["contact"]  # contacts
    else:
        return 0

############################################################## /**
# * @brief checks if a hand ksw code represents a right hand
# * @param $subunit ksw input code
# * @return true or false
# * @ingroup helpers
# */
def right_hand(subunit):
    # print subunit, subunit[1]
    # 0-7 rechts
    # 8-f links
    subunit = subunit[5]
    return dig1smaller(subunit, 8)


#############################################################
#  /**
# * @brief checks if a hand ksw code represents a left hand
# * @param $subunit ksw input code
# * @return true or false
# * @ingroup helpers
# */
def left_hand(subunit):
    if right_hand(subunit):
        return False
    else:
        return True


#############################################################
#  /**
# * @brief checks if a movement ksw code represents a right movement
# * @param $subunit ksw input code
# * @return true or false
# * @ingroup helpers
# */
def right_movement(subunit):
    # 0,3 rechts
    # 1,4 links
    # 2,5 both sides (general arrow)
    subunit = subunit[4]
    if int(subunit) in [0, 3, 2, 5]:
        return 1  # it is a right hand movement
    else:
        return 0


#############################################################
#  /**
# * @brief rotates a movement by 45 degrees
# * @param $digit last digit of a ksw code
# * @param $direction "positive" or "negative"
# * @return last digit of rotated code
# * @ingroup helpers
# */
def rotate45(digit, direction):
    # last digit 0-7 are rotations in 45deg direction
    # last digit 8-f are rotations in 45deg direction of the mirrored
    # rotation means counting up and braking over back to the initial digit once there is an overflow
    digit = str(digit)
    if direction == "negative":
        # positive rotation
        if digit == "7":
            return "0"
        elif digit == "9":
            return "a"
        elif digit == "a":
            return "b"
        elif digit == "b":
            return "c"
        elif digit == "c":
            return "d"
        elif digit == "d":
            return "e"
        elif digit == "e":
            return "f"
        elif digit == "f":
            return "8"
        else:
            return str(int(digit) + 1)
    elif direction == "positive":
        # negative rotation
        # last digit 0-7 are rotations in 45deg direction
        # last digit 8-f are rotations in 45deg direction of the mirrored
        # rotation means counting up and braking over back to the initial digit once there is an overflow
        if digit == "0":
            return "7"
        elif digit == "a":
            return "9"
        elif digit == "b":
            return "a"
        elif digit == "c":
            return "b"
        elif digit == "d":
            return "c"
        elif digit == "e":
            return "d"
        elif digit == "f":
            return "e"
        elif digit == "8":
            return "f"
        else:
            return str(int(digit) - 1)
    else:
        print "ERROR: wrong direction"
        exit()

#############################################################
#  /**
# * @brief mirrors a ksw digit
# * @param $digit last digit of a ksw code
# * @return last digit of mirrored code
# * @ingroup helpers
# */
def mirror(digit):
    # add 8 to the digit, overflow normally at f
    return int2hex(hex2int(digit) + 8)

#############################################################
#  /**
# * @brief mirrors a ksw digit backwards
# * @param $digit last digit of a ksw code
# * @return last digit of mirrored code
# * @ingroup helpers
# */
def mirror_countback(digit):
    # add 8 to the digit, overflow normally at f
    num_of_rotations = hex2int(digit) % 8
    digit = int2hex(hex2int(digit) - num_of_rotations + 8)  # +8 mirrors
    for i in range(0, num_of_rotations):
        digit = rotate45(digit, "positive")
    return str(digit)

#############################################################
#  /**
# * @brief when a mirrored subunit gets built by a non-mirrored subunit, then we need to fix the replacement
# * we do this by seeing how much the subunit has been rotated, and rotate the non-mirrored replacement in the other direction
# * @param $digit last digit of a ksw code
# * @return last digit of mirrored code
# * @ingroup helpers
# */
def fix_mirrored2notmirrored(digit):
    #
    num_of_rotations = hex2int(digit) - 8
    digit = 0  # set it to the non-rotated subunit
    for i in range(0, num_of_rotations):
        digit = rotate45(digit, "positive")
    return str(digit)


#############################################################
#  /**
# * @brief builds a given movement from basic movements (building blocks),
# * eg. a corner movement by two perpendicular straight movements.
# * @param $orig ksw movement code
# * @param $do_coart if it is 1, insert coarticulation tags in between two building blocks
# * @return simplified code
# * @ingroup helpers
# */
def build_movement_from_basic_movement(orig, do_coart=0):
    # to_basic_mapping stores the composition of building units for movements
    to_basic_mapping = {"S22f": [["doublePlusCoarticulation", "S22a"]],
                        "S230": [["doublePlusCoarticulation", "S22e"]],
                        "S231": [["rot180", "S22a"], ["_", "S22a"]],
                        "S232": [["rot180", "S22e"], ["_", "S22e"]],
                        "S233": [["_", "S22a"], ["rot-90", "S22a"]],
                        "S234": [["triplePlusCoarticulation", "S22a"]],
                        "S235": [["triplePlusCoarticulation", "S22e"]],
                        "S236": [["_", "S22a"], ["rot180", "S22a"], ["_", "S22a"]],
                        "S237": [["_", "S22e"], ["rot180", "S22e"], ["_", "S22e"]],
                        "S238": [["rot-45", "S22a"], ["_", "S22a"]],
                        "S23b": [["rot-90", "S22a"], ["_", "S22a"]],
                        "S23f": [["rot-135", "S22a"], ["_", "S22a"]],
                        "S242": [["rot180", "S22a"], ["rot-90", "S22a"], ["_", "S22a"]],
                        "S245": [["_", "S22a"], ["rot-135", "S22a"], ["_", "S22a"]],
                        "S248": [["rot45", "S22a"], ["rot-45", "S22a"], ["rot45", "S22a"], ["rot-45", "S22a"]],
                        "S253": [["double", "S252"]],
                        "S254": [["triple", "S252"]],
                        "S26a": [["double", "S265"]],
                        "S26b": [["double", "S269"]],
                        "S26c": [["rot180", "S265"], ["_", "S265"]],
                        "S26d": [["rot180", "S269"], ["_", "S269"]],
                        "S26e": [["_", "S265"], ["rot-90", "S265"]],
                        "S26f": [["triplePlusCoarticulation", "S265"]],
                        "S270": [["triplePlusCoarticulation", "S269"]],
                        "S271": [["_", "S265"], ["rot180", "S265"], ["_", "S265"]],
                        "S272": [["_", "S269"], ["rot180", "S269"], ["_", "S269"]],
                        "S273": [["rot-45", "S265"], ["_", "S265"]],
                        "S274": [["rot-90", "S265"], ["_", "S265"]],
                        "S277": [["rot-135", "S265"], ["_", "S265"]],
                        "S278": [["rot180", "S265"], ["rot-90", "S265"], ["_", "S265"]],
                        "S27b": [["_", "S265"], ["rot135", "S265"], ["_", "S265"]],
                        "S27e": [["rot135", "S265"], ["_", "S265"], ["rot135", "S265"], ["_", "S265"]],
                        "S28c": [["rot45", "S288"], ["rot-45", "S288"]],
                        "S290": [["rot135", "S288"], ["rot45", "S288"], ["rot-45", "S288"]],
                        "S292": [["double", "S288"]],
                        "S298": [["double", "S295"]],
                        "S299": [["mirror", "S288"], ["_", "S288"]],
                        "S29c": [["rot45", "S288"], ["rot-45", "S288"], ["mirror_rot45", "S288"],
                                 ["mirror_rot-45", "S288"], ["rot45", "S288"], ["rot-45", "S288"]],
                        "S2a7": [["double", "S2a6"]],
                        "S2b9": [["double", "S2b7"]],
                        "S2bb": [["triple", "S2b7"]],
                        "S2c8": [["double", "S2c6"]],
                        "S2ca": [["triple", "S2c6"]],
                        "S2da": [["double", "S2d5"]],
                        "S2e5": [["double", "S2e3"]],
                        "S2ea": [["double", "S2e7"]],
                        "S2ee": [["double", "S2ed"]],
                        "S2f0": [["double", "S2ef"]],
                        "S2f2": [["double", "S2f1"]],
                        "S2f4": [["double", "S2f3"]],
                        "S24c": [["doublePlusCoarticulation", "S24b"]],
                        # Travel Rotation, Double Wall Plane gets 2 single
                        "S24d": [["_", "S24b"], ["mirror", "S24b"]],
                        # Travel Rotation, Alternating Wall Plane gets 2 single
                        "S24f": [["doublePlusCoarticulation", "S24e"]],
                        # Travel Rotation, Double Floor Plane gets 2 single
                        "S250": [["_", "S24e"], ["mirror", "S24e"]],
                        # Travel Rotation, Alternating Floor Plane gets 2 single
                        "S282": [["doublePlusCoarticulation", "S281"]],
                        # Travel Rotation, Double Floor Plane gets 2 single
                        "S283": [["_", "S281"], ["mirror", "S281"]],
                        # Travel Rotation, Alternating Floor Plane gets 2 single
                        "S285": [["doublePlusCoarticulation", "S284"]],
                        # Travel Rotation, Double Wall Plane gets 2 single
                        "S286": [["_", "S284"], ["mirror", "S284"]],
                        # Travel Rotation, Alternating Wall Plane gets 2 single
                        "S2a3": [["doublePlusCoarticulation", "S2a2"]],  # Rotation, Double Wall Plane gets 2 single
                        "S2a4": [["_", "S2a2"], ["mirror", "S2a2"]],  # Rotation, Alternating Wall Plane gets 2 single
                        "S2ab": [["doublePlusCoarticulation", "S2aa"]],
                        # Rotation, Double hits front wall gets 2 single
                        "S2ac": [["_", "S2aa"], ["mirror", "S2aa"]],
                        # Rotation, Alternating hits front wall gets 2 single
                        "S2b2": [["doublePlusCoarticulation", "S2b1"]],  # Rotation, Double hits chest gets 2 single
                        "S2b3": [["_", "S2b1"], ["mirror", "S2b1"]],  # Rotation, Alternating hits chest gets 2 single
                        "S2c4": [["doublePlusCoarticulation", "S2c3"]],  # Rotation, Double hits ceiling gets 2 single
                        "S2c5": [["_", "S2c3"], ["mirror", "S2c3"]],  # Rotation, Alternating hits ceiling gets 2 single
                        "S2d3": [["doublePlusCoarticulation", "S2d2"]],  # Rotation, Double hits floor gets 2 single
                        "S2d4": [["_", "S2d2"], ["mirror", "S2d2"]],  # Rotation, Alternating hits floor gets 2 single
                        "S2e0": [["doublePlusCoarticulation", "S2df"]],  # Rotation Double Floor Plane gets 2 single
                        "S2e1": [["_", "S2df"], ["mirror", "S2df"]],  # Rotation, Alternating  floor plane gets 2 single
                        "S25d": [["_", "S255"]],  # Diagonal Between Away to Diagonal Away Movement
                        "S261": [["_", "S259"]],  # Diagonal Between Away to Diagonal Away Movement
                        }

    # saves, whether a mirrored version of the movement exists
    mirror_exists = ["S231", "S232", "S233", "S238", "S239", "S23a", "S23b", "S23c", "S23d", "S23e", "S23f", "S240",
                     "S241", "S242", "S243", "S244", "S245", "S246", "S247", "S248", "S249", "S24a", "S24b", "S24c",
                     "S24d", "S24e", "S24f", "S250", "S252", "S253", "S254", "S26c", "S26d", "S26e", "S271", "S273",
                     "S274", "S275", "S276", "S277", "S278", "S279", "S27a", "S27b", "S27c", "S27d", "S27e", "S27f",
                     "S280", "S281", "S282", "S283", "S284", "S285", "S286", "S288", "S289", "S28a", "S28b", "S28c",
                     "S28d", "S28e", "S28f", "S290", "S291", "S292", "S293", "S294", "S295", "S296", "S297", "S298",
                     "S299", "S29a", "S29b", "S29c", "S29d", "S29e", "S29f", "S2a0", "S2a1", "S2a2", "S2a3", "S2a4",
                     "S2a5", "S2a6", "S2a7", "S2a8", "S2a9", "S2aa", "S2ab", "S2ac", "S2ad", "S2ae", "S2af", "S2b0",
                     "S2b1", "S2b2", "S2b3", "S2b4", "S2b5", "S2b6", "S2b7", "S2b8", "S2b9", "S2ba", "S2bb", "S2bc",
                     "S2bd", "S2be", "S2bf", "S2c0", "S2c1", "S2c2", "S2c3", "S2c4", "S2c5", "S2c6", "S2c7", "S2c8",
                     "S2c9", "S2ca", "S2cb", "S2cc", "S2cd", "S2ce", "S2cf", "S2d0", "S2d1", "S2d2", "S2d3", "S2d4",
                     "S2d5", "S2d6", "S2d7", "S2d8", "S2d9", "S2da", "S2db", "S2dc", "S2dd", "S2de", "S2df", "S2e0",
                     "S2e1", "S2e2", "S2e3", "S2e4", "S2e5", "S2e6", "S2e7", "S2e8", "S2e9", "S2ea", "S2eb", "S2ec",
                     "S2ed", "S2ee", "S2ef", "S2f0", "S2f1", "S2f2", "S2f3", "S2f4"]

    if orig[0] != "S":
        return orig.strip(' ')
    else:
        if len(orig) != 6:
            print "ERROR, subunit is not long enough: " + len(orig) + " " + orig
            exit()
        start = orig[0:4]
        end = orig[4:6]
        result = ""
        if start in to_basic_mapping:
            for rule in to_basic_mapping[start]:
                start = orig[0:4]
                end = orig[4:6]
                procedure = rule[0]
                target = rule[1]
                rotation_direction = "positive"
                needs_fixing = 0
                if (start in mirror_exists) and (target not in mirror_exists):
                    #               print "...target may be mirrored", end
                    if dig1smaller("7", orig[5]):  # orig is mirrored?
                        needs_fixing = 1
                        #                    print "...it is mirrored, fixing"

                if procedure == "_":
                    if needs_fixing == 1:
                        # print "yeas"
                        end = end[0] + fix_mirrored2notmirrored(end[1])
                    result += target + end + " "

                # insert movement epenthesis between to following movments in one direction, ex: "down down"
                elif procedure == "doublePlusCoarticulation" and do_coart == 1:
                    if needs_fixing == 1:
                        end = end[0] + fix_mirrored2notmirrored(end[1])

                    result += target + end + " " + target + end[0] + rotate45(
                        rotate45(rotate45(rotate45(end[1], rotation_direction), rotation_direction), rotation_direction),
                        rotation_direction) + " " + target + end + " "

                elif procedure == "doublePlusCoarticulation" or procedure == "double":
                    if needs_fixing == 1:
                        end = end[0] + fix_mirrored2notmirrored(end[1])
                    result += target + end + " " + target + end + " "

                elif procedure == "triplePlusCoarticulation" and do_coart == 1:
                    if needs_fixing == 1:
                        end = end[0] + fix_mirrored2notmirrored(end[1])
                    result += target + end + " " + target + end[0] + rotate45(
                        rotate45(rotate45(rotate45(end[1], rotation_direction), rotation_direction), rotation_direction),
                        rotation_direction) + " " + target + end + " " + target + end[0] + rotate45(
                        rotate45(rotate45(rotate45(end[1], rotation_direction), rotation_direction), rotation_direction),
                        rotation_direction) + " " + target + end + " "

                elif procedure == "triplePlusCoarticulation" or procedure == "triple":
                    if needs_fixing == 1:
                        end = end[0] + fix_mirrored2notmirrored(end[1])
                    result += target + end + " " + target + end + " " + target + end + " "

                elif procedure == "rot45":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        end = end[0] + mirror(end[1])  # mirror back
                    result += target + end[0] + rotate45(end[1], rotation_direction) + " "

                elif procedure == "rot90":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        end = end[0] + mirror(end[1])  # mirror back
                    result += target + end[0] + rotate45(rotate45(end[1], rotation_direction), rotation_direction) + " "

                elif procedure == "rot135":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        end = end[0] + mirror(end[1])  # mirror back
                    result += target + end[0] + rotate45(
                        rotate45(rotate45(end[1], rotation_direction), rotation_direction), rotation_direction) + " "

                elif procedure == "rot180" or procedure == "rot-180":
                    if needs_fixing == 1:
                        end = end[0] + fix_mirrored2notmirrored(end[1])
                    result += target + end[0] + rotate45(
                        rotate45(rotate45(rotate45(end[1], rotation_direction), rotation_direction), rotation_direction),
                        rotation_direction) + " "

                elif procedure == "rot-45":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        # end=end[0]+mirror(end[1]) # mirror back
                        end = end[0] + fix_mirrored2notmirrored(end[1])
                    # inverse rotation Direction
                    if rotation_direction == "positive":
                        rotation_direction = "negative"
                    else:
                        rotation_direction = "positive"
                    result += target + end[0] + rotate45(end[1], rotation_direction) + " "

                elif procedure == "rot-90":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        end = end[0] + mirror(end[1])  # mirror back
                        # inverse rotation Direction
                    if rotation_direction == "positive":
                        rotation_direction = "negative"
                    else:
                        rotation_direction = "positive"
                    result += target + end[0] + rotate45(rotate45(end[1], rotation_direction), rotation_direction) + " "

                elif procedure == "rot-135":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        # end=end[0]+mirror(end[1]) # mirror back
                        end = end[0] + fix_mirrored2notmirrored(end[1])

                        # inverse rotation Direction
                    if rotation_direction == "positive":
                        rotation_direction = "negative"
                    else:
                        rotation_direction = "positive"
                    result += target + end[0] + rotate45(
                        rotate45(rotate45(end[1], rotation_direction), rotation_direction), rotation_direction) + " "

                elif procedure == "mirror":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        end = end[0] + mirror(end[1])  # mirror back
                        # end=end[0]+fixMirrored2NotMirrored(end[1])
                    result += target + end[0] + mirror_countback(end[1]) + " "

                elif procedure == "mirror_rot45":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        end = end[0] + mirror(end[1])  # mirror back
                    result += target + end[0] + mirror(rotate45(end[1], rotation_direction)) + " "

                elif procedure == "mirror_rot-45":
                    if needs_fixing == 1:
                        rotation_direction = "negative"  # inverse rotation directions
                        end = end[0] + mirror(end[1])  # mirror back
                        # inverse rotation Direction
                    if rotation_direction == "positive":
                        rotation_direction = "negative"
                    else:
                        rotation_direction = "positive"

                    result += target + end[0] + mirror(rotate45(end[1], rotation_direction)) + " "
                else:
                    print "WARNING procedure " + procedure + " not implemented. Subunit stays as it is: " + orig
                    result += start + end + " "

        else:
            # no rule applicable
            result = orig
        return result.strip(' ')


#############################################################
#  /**
# * @brief maps different movement sizes to a single size.
# * eg. a long straight movement and a short will result in the same movements.
# * @param $subunit ksw movement code
# * @return mapped ksw code
# * @ingroup helpers
# */
def map_movement_size(subunit):
    # differences in length (ie small, medium large) are contained in each list
    map_lengths = [
        ["S22a", "S22b", "S22c", "S22d"],
        ["S238", "S239", "S23a"],
        ["S23b", "S23c", "S23d"],
        ["S23f", "S240", "S241"],
        ["S242", "S243", "S244"],
        ["S245", "S246", "S247"],
        ["S248", "S249", "S24a"],
        ["S255", "S256", "S257", "S258"],
        ["S259", "S25a", "S25b", "S25c"],
        ["S25d", "S25e", "S25f", "S260"],
        ["S261", "S262", "S263", "S264"],
        ["S265", "S266", "S267", "S268"],
        ["S274", "S275", "S276"],
        ["S278", "S279", "S27a"],
        ["S27b", "S27c", "S27d"],
        ["S27e", "S27f", "S280"],
        ["S288", "S289", "S28a", "S28b"],
        ["S28c", "S28d", "S28e", "S28f"],
        ["S290", "S291"],
        ["S292", "S293", "S294"],
        ["S295", "S296", "S297"],
        ["S299", "S29a", "S29b"],
        ["S29c", "S29d", "S29e"],
        ["S2a0", "S2a1"],
        ["S2b4", "S2b5", "S2b6"],
        ["S2b7", "S2b8"],
        ["S2b9", "S2ba"],
        ["S2bb", "S2bc"],
        ["S2bd", "S2be"],
        ["S2bf", "S2c0"],
        ["S2c1", "S2c2"],
        ["S2c6", "S2c7"],
        ["S2c8", "S2c9"],
        ["S2ca", "S2cb"],
        ["S2cc", "S2cd"],
        ["S2ce", "S2cf"],
        ["S2d0", "S2d1"],
        ["S2d5", "S2d6", "S2d7", "S2d8"],
        ["S2dd", "S2de"],
        ["S2e3", "S2e4"],
        ["S2e5", "S2e6"],
        ["S2e7", "S2e8", "S2e9"],
        ["S2ea", "S2eb", "S2ec"],
        ["S2f5", "S2f6"],
    ]
    length_mapping = {}
    for array2join in map_lengths:
        target = array2join[0]
        for i in range(1, len(array2join)):
            length_mapping.setdefault(array2join[i], target)

    start = subunit[0:4]
    end = subunit[4:len(subunit)]
    if start in length_mapping:
        return length_mapping[start] + end
    else:
        return subunit

def map_general_arrow2right_arrow(subunit):
    # open arrow heads (like S22a20) are a general arrow: both hands move together
    start = subunit[0:4]
    if subunit[4] == "2":
        return subunit[0:4] + "0" + subunit[5:len(subunit)]
    elif subunit[4] == "5":
        return subunit[0:4] + "3" + subunit[5:len(subunit)]
    else:
        return subunit


def map_floor_plane2wall_plane_arrow(subunit):
    # some movements in the floor plane correspond to others in the wall plane
    # we use the wall plane movements as standard
    mapping = {"S26502": "S22a02",
               "S26506": "S22a06"}
    # print subunit, mapping[subunit]
    if subunit in mapping:
        return mapping[subunit]
    else:
        return subunit
