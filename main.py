# https://repl.it/talk/share/Danganronpa-simulator/6602

import os, pathlib, random, csv, re, textwrap
from guizero import App, TextBox, Box, Text, PushButton, ListBox, Picture, ButtonGroup, Slider, info, Waffle
from PIL import ImageFilter, Image, GifImagePlugin

# content_list.append()

class Chara:
    # status
    # 1 = alive, 0 = dead, 2 = currently killed
    def __init__(self, name, gender, ultimate, image):
        self.name = name
        self.gender = gender
        self.ultimate = ultimate
        self.image = image
        self.status = 1

    def __repr__(self):
        # for returning SOMETHING when called by print
        return str(self.image)

# i love to make unnecessary stuffs like this!
try:
    coolblurb_file = open("asset/coolblurb.txt", "r")
    coolblurb_lines = coolblurb_file.readlines()
    coolblurb = []
    for x in coolblurb_lines:
        coolblurb.append(x.rstrip("\n"))
finally:
    coolblurb_file.close()

app = App(title="DanganSim | " + random.choice(coolblurb), height=700, width=600)
title_box = Box(app, width="fill", align="top")
content_box = Box(app, layout="grid")
genderlist = ["Female", "Male"]
imagedefault = "player/default.png"
icon_invest = "asset/icon_invest.png"
icon_motive = "asset/icon_motive.png"
icon_event = "asset/icon_event.png"
icon_dead = "asset/icon_dead.png"
content_list = []
chara_list = []
event1_list = []
event2_list = []
event3_list = []
eventall_list = []
invest_list = []
clue_item_list = []
clue_place_list = []
clue_words_list = []
motive_list = []
punish_list = []
died_list = []
survivors = 2
wrap_width = 70
chaptercount = 0
survivecount = 0
coolcounter = 0
size_icon = (100, 100)
size_clue = (50, 50)
text1 = Text(title_box, text="DanganSim : School succ", size=14, color="red", bg="orange", font="Arial")

# check if the image has animation
def hasanimation(image):
    try:
        image.seek(1)
        return True
    except EOFError:
        return False

# reading image and return with image object from PIL(LOW)
def read_asimage(filename, emboss):
    im = Image.open(filename)
    im.load()
    filetype = im.format
    # why RGBA? some needs like alpha compositing, so i'll just make all image in RGBA mode
    im = im.convert("RGBA")
    animated_format = ["GIF", "APNG"]
    # should only seek frames instead, but i remember there's certain format that used frames as layer so just to make sure????
    if any(x in filetype for x in animated_format) and hasanimation(im):
        im.seek(0)
    # originally used for dead person, but using overlay instead so it's redundant now
    if emboss:
        im = im.filter(ImageFilter.EMBOSS)
    return im

# reading txt file and return as list of strings
def readas_list(filename):
    linelist = []
    with open(filename, "r") as file_read:
        file_lines = file_read.readlines()
        for x in file_lines:
            linelist.append(x.rstrip("\n"))
    return linelist

# here we go. in guizero, you can basically destroy their own object using destroy()
# content_list is a list of created guizero objects that i can destroy all in 1 go whenever i want (usually as first function of every screen functions)
# unfortunately i don't have enough will to check if destroy means destroy whole object or just functionality (there's active option so might be 1st one)
# and so i also clear the list to make sure there's no empty object inside
def clean_contentlist():
    if len(content_list) >= 1:
        for x in content_list:
            x.destroy()
        content_list.clear()

# wrapping text (thnx python)
def text_wrap(text):
    if len(text) > wrap_width:
        return textwrap.fill(text, wrap_width)
    else: return text

# punishment screen
def play_punish(choosen):
    clean_contentlist()

    # since not needing currently death(s) anymore, gotta convert it to 0 for those recently got killed
    index = 0
    for x in chara_list:
        if x.status != 1:
            chara_list[index].status = 0
        index += 1
    # kill the culprit
    chara_list[choosen].status = 0

    gendered_1 = ["she", "he"]
    gendered_2 = ["her", "his"]
    gendered_3 = ["her", "him"]

    content_list.append(Text(content_box, text="After votes, everyone agree to choose:", grid=[0,1], size=10, color="blue"))
    content_list.append(Picture(content_box, image=read_asimage(chara_list[choosen].image, 0).resize(size_icon, Image.LANCZOS), grid=[0,2]))
    content_list.append(Text(content_box, text=chara_list[choosen].name, grid=[0,3], size=10, color="red"))
    content_list.append(Text(content_box, text="Ultimate: " + chara_list[choosen].ultimate, grid=[0,4], size=10, color="red"))
    content_list.append(Text(content_box, text="And the vote was right! The punishment for {0}:".format(chara_list[choosen].name), grid=[0,5], size=11, color="orange"))
    punish_text = random.choice(punish_list).format(chara_list[choosen].name)
    punish_text = punish_text.replace("<[1]>", gendered_1[chara_list[choosen].gender])
    punish_text = punish_text.replace("<[2]>", gendered_2[chara_list[choosen].gender])
    punish_text = punish_text.replace("<[3]>", gendered_3[chara_list[choosen].gender])
    content_list.append(Text(content_box, text=text_wrap(punish_text), grid=[0,6], size=10, color="red"))

    content_list.append(Text(content_box, font="Constantia", text="Trial : Punishment", grid=[0,0], size=12, color ="red", width="fill"))
    content_list.append(PushButton(content_box, text="Continue", grid=[0,7], command=play_chapterstart))

# voting screen
def play_vote():
    clean_contentlist()
    playerpos_x = 0
    playerpos_y = 4
    text_pos = 0
    index = 0
    content_index = 3
    choosen_bag = []
    choosen = 0
    vote_chara = []
    alive = 0
    for x in range(len(chara_list)):
        if chara_list[x].status == 1:
            vote_chara.append(0)
            alive += 1
        else:
            vote_chara.append(-1)
    # print(alive)
    # random voting time!
    for x in range(alive):
        nonminus = random.randint(0,len(chara_list)-1)
        while chara_list[nonminus].status != 1:
            nonminus = random.randint(0,len(chara_list)-1)
        vote_chara[nonminus] += 1
    # print (vote_chara)
    for x in chara_list:
        if playerpos_x == 5:
            playerpos_x = 0
            playerpos_y += 4
        if vote_chara[index] > 0:
            content_list.append(Picture(content_box, image=read_asimage(x.image, bool(not(x.status))).resize(size_icon, Image.LANCZOS), grid=[playerpos_x,1+playerpos_y]))
            content_list.append(Text(content_box, text=x.name + " | votes: " + str(vote_chara[index]), grid=[playerpos_x,2+playerpos_y], size=10, color="red"))
            content_list.append(Text(content_box, text="Ultimate " + x.ultimate, grid=[playerpos_x,3+playerpos_y], size=10, color="red"))
            content_list.append(Waffle(content_box, grid=[playerpos_x,4+playerpos_y], height=1, width=10, dim=5, pad=2))
            # print("content index: "+str(content_index))
            # print(content_list)
            vote_bar = int(vote_chara[index]/alive*10)
            for x in range(10):
                if x <= vote_bar:
                    content_list[content_index][x,0].color = "red"
            playerpos_x += 1
            content_index += 4
        index += 1
        if text_pos <= 6:
            text_pos += 1

    bignum = max(vote_chara)
    for x in range(len(vote_chara)):
        if vote_chara[x] >= bignum :
            choosen_bag.append(x)
    if len(choosen_bag) <= 1:
        choosen = choosen_bag[0]
    else:
        choosen = random.choice(choosen_bag)

    content_list.append(Text(content_box, font="Constantia", text="Trial : Voting", grid=[0,0,text_pos,1], size=12, color ="blue", width="fill"))
    content_list.append(PushButton(content_box, text="Continue", grid=[0,playerpos_y+5,text_pos,1], command=lambda: play_punish(choosen)))

# clue findings screen
def play_clue():
    clean_contentlist()
    content_list.append(Text(content_box, font="Constantia", text="Trial : Clue findings", grid=[0,0,3,1], size=12, color ="blue", width="fill"))
    # constructing clues
    chara_event = []
    chara_image = []
    playerpos_y = 2
    for x in range(random.randint(4,7)):
        for x in range(2):
            pick = random.randrange(0,len(chara_list))
            while chara_list[pick].status != 1 or chara_list[pick].name in chara_event:
                pick = random.randrange(0,len(chara_list))
            chara_event.append(chara_list[pick].name)
            chara_image.append(chara_list[pick].image)

        mode = random.randint(0,1) == 0
        if mode == 0:
            message_clue = random.choice(clue_item_list) + " found in " + random.choice(clue_place_list)
        elif mode == 1:
            message_clue = random.choice(clue_words_list)
        # check if there's people attached into it
        if "{0}" in message_clue and "{1}" in message_clue:
            message_clue =  message_clue.format(chara_event[0], chara_event[1])
            pic1 = chara_image[0]
            pic2 = chara_image[1]
        elif "{1}" in message_clue:
            message_clue = message_clue.replace("{1}", "{0}")
            message_clue = message_clue.format(random.choice(chara_event))
            pic1 = chara_image[0]
            pic2 = icon_invest
        elif "{0}" in message_clue:
            message_clue = message_clue.format(random.choice(chara_event))
            pic1 = chara_image[0]
            pic2 = icon_invest
        
        content_list.append(Picture(content_box, image=read_asimage(pic1, 0).resize(size_clue, Image.LANCZOS), grid=[0,playerpos_y]))
        content_list.append(Text(content_box, text=text_wrap(message_clue), grid=[1,playerpos_y], size=10, color="black"))
        content_list.append(Picture(content_box, image=read_asimage(pic2, 0).resize(size_clue, Image.LANCZOS), grid=[2,playerpos_y]))

        playerpos_y += 1
        chara_event.clear()
        chara_image.clear()

    # content_list.append(Text(content_box, text="\n".join(result_clue), grid=[0,2], size=10, color="black"))
    content_list.append(Text(content_box, text="After some discussions, here's the list of possible clues:", grid=[0,1,3,1], size=10, color="blue"))
    content_list.append(PushButton(content_box, text="Continue", grid=[0,playerpos_y+1,3,1], command=play_vote))

# investigate screen
def play_investigate():
    global coolcounter
    clean_contentlist()
    pick = random.randrange(0,len(chara_list))
    while chara_list[pick].status != 1:
        pick = random.randrange(0,len(chara_list))
    chara_invest = chara_list[pick].name
    chara_index = pick

    message_invest = random.choice(invest_list)
    if "{0}" in message_invest:
        # print(message_invest)
        content_list.append(Picture(content_box, image=read_asimage(chara_list[chara_index].image, 0).resize(size_icon, Image.LANCZOS), grid=[0,1]))
        content_list.append(Picture(content_box, image=read_asimage(icon_invest, 0).resize(size_icon, Image.LANCZOS), grid=[1,1]))
        message_invest = message_invest.format(chara_invest)
        place_x = 2
    else:
        content_list.append(Picture(content_box, image=read_asimage(icon_invest, 0).resize(size_icon, Image.LANCZOS), grid=[0,1]))
        place_x = 1
    content_list.append(Text(content_box, text=text_wrap(message_invest), grid=[0,2,place_x,1], size=10, color="blue"))

    coolcounter -= 1
    if coolcounter == 0:
        content_list.append(PushButton(content_box, text="Continue", grid=[0,3,place_x,1], command=play_clue))
    else:
        content_list.append(PushButton(content_box, text="Continue", grid=[0,3,place_x,1], command=play_investigate))

    content_list.append(Text(content_box, font="Constantia", text="Investigating", grid=[0,0,place_x,1], size=12, color ="blue", width="fill"))

# recently killed screen
def play_killed():
    global coolcounter
    clean_contentlist()
    playerpos_x = 0
    index = 0
    for x in chara_list:
        # shows only recently killed
        if x.status == 2:
            # print(x.image)
            imageded = read_asimage(x.image, 0).resize(size_icon, Image.LANCZOS)
            content_list.append(Picture(content_box, image=Image.alpha_composite(imageded, read_asimage(icon_dead, 0)), grid=[playerpos_x,1]))
            content_list.append(Text(content_box, text=x.name, grid=[playerpos_x,2], size=10, color="red"))
            content_list.append(Text(content_box, text="Ultimate " + x.ultimate, grid=[playerpos_x,3], size=10, color="red"))
            # print(x.name + "'s status: " + str(x.status))
            playerpos_x += 1
        index += 1
    coolcounter = random.randint(4,6)
    content_list.append(Text(content_box, text="Found " + random.choice(died_list), grid=[0,4,playerpos_x,1], size=10, color="red"))
    content_list.append(PushButton(content_box, text="Continue", grid=[0,5,playerpos_x,1], command=play_investigate))

    content_list.append(Text(content_box, font="Chiller", text="Killed!", grid=[0,0,playerpos_x,1], size=18, color ="red", width="fill"))

# randomize within range
def kill_roulette():
    x1, x2 = 50, 85
    roulette = random.randint(1,100)
    if roulette >= 1 and roulette <= x1:
        kill = 1
    elif roulette >= x1 and roulette <= x2:
        kill = 2
    elif roulette >= x2 and roulette <= 100:
        kill = 3
    return kill

# calculation on who to die
def play_decidekill():
    remain_to_kill = survivecount - survivors - 1
    # print("remainings to kill -> " + str(remain_to_kill))
    # check if it's possible to kill up to 3 people 
    if remain_to_kill > 3:
        kill = kill_roulette()
        # cool, now imagine 4 target survivors and there's 7 remaining atm
        # so it should have 3 remainings to kill
        # with that, now imagine the system decided to kill 1 person
        # that means 2 people left. after kill the culprit after, it'll turn into 1 person left
        # see the problem? next time it'll be 5 survivors remaining, which is bad
        # with this, shouldn't purely randomized so no error!
        while (remain_to_kill - kill == 1):
            kill = kill_roulette()
        # print("final kill"+str(kill))
    else:
        kill = random.randint(1,remain_to_kill)
        while (remain_to_kill - kill == 1):
            kill = random.randint(1,remain_to_kill)
        # print("final kill"+str(kill))
    for x in range(kill):
        # avoid killing already killed person
        kill_index = random.randrange(0, len(chara_list))
        while chara_list[kill_index].status == 2 or chara_list[kill_index].status == 0:
            kill_index = random.randrange(0, len(chara_list))
        chara_list[kill_index].status = 2
    play_killed()

# event (and motivation showin) screen
def play_event():
    global coolcounter
    clean_contentlist()
    eventselect = random.randint(1,4)
    chara_event = []
    chara_index = []
    place_x = 0
    for x in range(3):
        pick = random.randrange(0,len(chara_list))
        while chara_list[pick].status != 1 or chara_list[pick].name in chara_event:
            pick = random.randrange(0,len(chara_list))
        chara_event.append(chara_list[pick].name)
        chara_index.append(pick)
    if coolcounter == 3:
        content_list.append(Picture(content_box, image=read_asimage(icon_motive, 0).resize(size_icon, Image.LANCZOS), grid=[0,2]))
        motive_text = "Motive shown for students : " + random.choice(motive_list)
        content_list.append(Text(content_box, text=text_wrap(motive_text), grid=[0,3], size=10, color="blue"))
        place_x = 1
    else:
        message_event = ""
        if eventselect == 4:
            message_event = random.choice(eventall_list)
            content_list.append(Picture(content_box, image=read_asimage(icon_event, 0).resize(size_icon, Image.LANCZOS), grid=[0,2]))
            place_x = 1
        else:
            if eventselect == 1:
                message_event = random.choice(event1_list).format(chara_event[0])
            elif eventselect == 2:
                message_event = random.choice(event2_list).format(chara_event[0], chara_event[1])
            elif eventselect == 3:
                message_event = random.choice(event3_list).format(chara_event[0], chara_event[1], chara_event[2])
            for x in range(eventselect):
                place_x += 1
                i = chara_list[chara_index[x]].image
                content_list.append(Picture(content_box, image=read_asimage(i, 0).resize(size_icon, Image.LANCZOS), grid=[x,2]))
            content_list.append(Picture(content_box, image=read_asimage(icon_event, 0).resize(size_icon, Image.LANCZOS), grid=[place_x,2]))
            place_x += 1
        content_list.append(Text(content_box, text=text_wrap(message_event), grid=[0,3,place_x,1], size=10, color="blue"))
    coolcounter -= 1
    if coolcounter == 0:
        content_list.append(PushButton(content_box, text="Continue", grid=[0,4,place_x,1], command=play_decidekill))
    else:
        content_list.append(PushButton(content_box, text="Continue", grid=[0,4,place_x,1], command=play_event))

    content_list.append(Text(content_box, font="Constantia", text="Events", grid=[0,0,place_x,1], size=12, color ="blue", width="fill"))

# clean all the list.... idk why i have to do this tbh i prob only need things like character list
# and resetting chapter count to 0 (since it's always incrementing after chapter)
def play_cleanfinish():
    global chaptercount
    chara_list.clear()
    event1_list.clear()
    event2_list.clear()
    event3_list.clear()
    eventall_list.clear()
    died_list.clear()
    invest_list.clear()
    clue_item_list.clear()
    clue_place_list.clear()
    clue_words_list.clear()
    motive_list.clear()
    punish_list.clear()
    chaptercount = 0
    menu_main()

# final survivors screen
def play_finish():
    clean_contentlist()
    index = 0
    playerpos_x = 0
    playerpos_y = 0
    text_pos = 0
    for x in chara_list:
        if chara_list[index].status == 1:
            if playerpos_x == 4:
                playerpos_x = 0
                playerpos_y += 2
            content_list.append(Picture(content_box, image=read_asimage(x.image, bool(not(x.status))).resize(size_icon, Image.LANCZOS), grid=[playerpos_x,2+playerpos_y]))
            content_list.append(Text(content_box, text=x.name, grid=[playerpos_x,3+playerpos_y], size=10, color="blue"))
            playerpos_x += 1
            if text_pos <= 5:
                text_pos += 1
        index += 1
    content_list.append(Text(content_box, text="Chapter" + str(chaptercount), grid=[0,0,text_pos,1], size=10, color ="blue", width="fill"))
    content_list.append(Text(content_box, text="Here are survivors", grid=[0,1,text_pos,1], size=10, color ="orange", width="fill"))
    content_list.append(PushButton(content_box, text="Finish", grid=[0,playerpos_y+4,5,1], command=play_cleanfinish))

# chapter start screen
def play_chapterstart():
    global chaptercount, survivecount, coolcounter
    clean_contentlist()
    chaptercount += 1
    survivecount = 0
    for x in chara_list:
        if x.status != 0:
            survivecount += 1
    playerpos_x = 0
    playerpos_y = 0
    text_pos = 0
    colortext = ["red", "blue"]
    for x in chara_list:
        if playerpos_x == 5:
            playerpos_x = 0
            playerpos_y += 2
        if x.status == 0:
            imageded = read_asimage(x.image, 0).resize(size_icon, Image.LANCZOS)
            content_list.append(Picture(content_box, image=Image.alpha_composite(imageded, read_asimage(icon_dead, 0)), grid=[playerpos_x,1+playerpos_y]))
        else:
            content_list.append(Picture(content_box, image=read_asimage(x.image, 0).resize(size_icon, Image.LANCZOS), grid=[playerpos_x,1+playerpos_y]))
        content_list.append(Text(content_box, text=x.name, grid=[playerpos_x,2+playerpos_y], size=10, color=colortext[x.status]))
        playerpos_x += 1
        if text_pos <= 6:
            text_pos += 1
    # random initialize event counter
    content_list.append(Text(content_box, text="Chapter " + str(chaptercount), grid=[0,0,text_pos,1], size=12, color ="blue", width="fill"))
    coolcounter = random.randint(4,6)
    if survivecount <= survivors + 1 :
        content_list.append(PushButton(content_box, text="Continue", grid=[0,playerpos_y+3,5,1], command=play_finish))
    else:
        content_list.append(PushButton(content_box, text="Continue", grid=[0,playerpos_y+3,5,1], command=play_event))

# saving function for editor screen
def edit_save(index, n, g, u, i):
    regex = re.compile("[^\w\d\s@#]")
    if n == "" or u == "":
        app.warn("Empty Form(s)!", "All of forms must be filled")
        return
    elif regex.search(n) or regex.search(u):
        app.warn("Symbols Detected!", "Only alphanumeric and underscore (_) allowed")
        return
    if i == None:
        i = imagedefault
    chara_list[index].image = i
    chara_list[index].name = n
    chara_list[index].gender = g 
    chara_list[index].ultimate = u 
    play_charalist()

# canceling function
def edit_cancel(index, mode):
    if mode == 0:
        # since i made instance first for create mode, i need to pop it off
        chara_list.pop(-1)
    play_charalist()

# updating image preview
def update_imageprev(value):
    content_list[1].image = read_asimage(value, 0).resize(size_icon, Image.LANCZOS)

# chara editor screen
def play_charaeditor(index, mode):
    clean_contentlist()
    imagelist = []
    filefind = pathlib.Path("player/").glob("*")
    for file in filefind:
        if ".png" in str(file) or ".gif" in str(file) or ".jpg" in str(file) or ".jpeg" in str(file):
            imagelist.append(file)

    content_list.append(Text(content_box, text="Character Editor", grid=[0,0,2,1], size=10, color ="blue", width="fill"))
    content_list.append(Picture(content_box, image=read_asimage(chara_list[index].image, 0).resize(size_icon, Image.LANCZOS), grid=[1,1]))
    content_list.append(ListBox(content_box, scrollbar=True, items=imagelist, selected=chara_list[index].image, command=update_imageprev, grid=[0,1], width="fill"))

    content_list.append(Text(content_box, text="Name: ", grid=[0,2], size=10, color ="blue", align="right"))
    content_list.append(TextBox(content_box, text=chara_list[index].name, grid=[1,2], width="fill"))

    content_list.append(Text(content_box, text="Gender: ", grid=[0,3], size=10, color ="blue", align="right"))
    content_list.append(ButtonGroup(content_box, options=genderlist, selected=genderlist[chara_list[index].gender], grid=[1,3], horizontal=True, width="fill"))

    content_list.append(Text(content_box, text="Ultimate: ", grid=[0,4], size=10, color ="blue", align="right"))
    content_list.append(TextBox(content_box, text=chara_list[index].ultimate, grid=[1,4], width="fill"))

    content_list.append(PushButton(content_box, text="Save", grid=[0,5], command=lambda: edit_save(index,content_list[4].value,genderlist.index(content_list[6].value),content_list[8].value,content_list[2].value)))
    content_list.append(PushButton(content_box, text="Cancel", grid=[1,5], command=lambda: edit_cancel(index,mode)))

    content_list.append(Text(content_box, text="NOTE: Only alphanumeric and underscore (_) allowed for input!", grid=[0,6,2,1], size=10, color ="red", width="fill"))

# make new instance of the character
def player_create():
    chara_list.append(Chara("",0,"",imagedefault))
    play_charaeditor(chara_list.index(chara_list[-1]), 0)

# just throw in to her house since locked
def player_edit(index):
    play_charaeditor(index, 1)

# removal of character tru menu. apparently works
def player_remove(index):
    chara_list.pop(index)
    play_charalist()

# updating preview charalist
def update_charalist(value):
    regex = re.compile("\d+;")
    index = int(regex.search(value).group().strip(";"))
    content_list[2].image = read_asimage(chara_list[index].image, 0).resize(size_icon, Image.LANCZOS)
    content_list[3].value = chara_list[index].name
    content_list[4].value = genderlist[chara_list[index].gender]
    content_list[5].value = "Ultimate " + chara_list[index].ultimate
    content_list[1].value = str(index)
    # print(chara_list)

# updating survivor's number
def update_survivor(value):
    global survivors
    survivors = int(value)

# checking how many charas
def check_enoughchara():
    global chaptercount
    if len(chara_list) < 8:
        app.warn("Not Enough People!", "Minimum students for the sim are 8")
        return
    elif len(chara_list) > 20:
        app.warn("Too Much People!", "Minimum students for the sim are 20")
        return
    else:
        chaptercount = 0
        play_chapterstart()

# abandon
def play_abandon():
    global chaptercount
    if app.yesno("Confirmation", "Are you sure you want to abandon the sim?\n(Character list will be wiped out clean)"):
        chara_list.clear()
        event1_list.clear()
        event2_list.clear()
        event3_list.clear()
        eventall_list.clear()
        died_list.clear()
        invest_list.clear()
        clue_item_list.clear()
        clue_place_list.clear()
        clue_words_list.clear()
        motive_list.clear()
        punish_list.clear()
        chaptercount = 0
        menu_main()
    else:
        return

# checking formats inside
def assert_format(file_name):
    regex = re.compile("[^\w\d\s@#]")
    format_list = [".gif", ".png", ".jpg", ".jpeg", ".bmp"]
    path_list = ["player/"]
    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) != 4:
                app.warn("Rows not as intended", "Should have 4 rows (name, gender, ultimate, image)")
                return False
            index = 0
            for cell in row:
                if index == 1 and (not cell.isdigit() or not (int(cell) >= 0 and int(cell) <= 1)):
                    app.warn("Gender misinput", "Should only 0 or 1 (female or male)")
                    return False
                elif (index == 0 or index == 2) and (cell == '' or cell == None or regex.search(cell)):
                    app.warn("Form misinput", "Input for name and ultimate should not be empty,\nand only contains alphanumeric and underscore")
                    return False
                elif index == 3 and (not (any(x in cell for x in format_list)) or not (any(x in cell[0:7] for x in path_list))):
                    # print(cell[0:6])
                    app.warn("Image misinput", "Input for file should be in either of these formats;\nGIF, PNG, JP(E)G, and Bitmap\nand has 'player' path behind")
                    return False
                index += 1
            index = 0
    return True

# importing list of charas
def chara_import():
    file_name = app.select_file(filetypes=[["CSV documents", "*.csv"]])
    if file_name == "" or file_name == None:
        play_charalist()
        return
    else: chara_list.clear()
    if assert_format(file_name):
        with open(file_name, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                chara_list.append(Chara(row[0], int(row[1]), row[2], row[3]))
            app.info("Success", "successfully imported the list!")
    else:
        app.info("Failed", "failed to import the file...")
    play_charalist()

# exporting list of charas
def chara_export():
    if len(chara_list) <= 0:
        app.warn("Empty list?", "No. Why you want to save empty list?")
        return
    filename = app.select_file(save=True, filetypes=[["CSV documents", "*.csv"]])
    if not (filename == None or filename == ""):
        regex = re.compile(".csv$")
        # check if it needs to add .csv on filename
        if not regex.search(filename):
            filename += ".csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x in chara_list:
                writer.writerow([x.name, x.gender, x.ultimate, x.image[0:6] + "/" + x.image[7:-1] + x.image[-1]])
            app.info("Saved", "successfully saved the list!")
    play_charalist()

# character screen out of me
def play_charalist():
    global survivors
    clean_contentlist()
    characount = len(chara_list)
    charalistin = []
    if characount > 0:
        for x in range(len(chara_list)):
            charalistin.append(str(x) + "; " + str(chara_list[x].name))

    content_list.append(Text(content_box, text="Preparation Menu", grid=[0,0,3,1], size=10, color ="blue", width="fill"))
    content_list.append(Text(content_box, text="0", grid=[0,7], size=10, color ="blue", visible=False))
    content_list.append(Picture(content_box, image=read_asimage(imagedefault, 0).resize(size_icon, Image.LANCZOS), grid=[2,1]))
    content_list.append(Text(content_box, text="-", grid=[2,2], size=10, color ="blue"))
    content_list.append(Text(content_box, text="-", grid=[2,3], size=10, color ="blue"))
    content_list.append(Text(content_box, text="-", grid=[2,4], size=10, color ="blue"))
    content_list.append(ListBox(content_box, scrollbar=True, items=charalistin, command=update_charalist, grid=[0,2,2,3], width="fill", height="fill"))

    content_list.append(Text(content_box, text="Last Survivors: ", grid=[0,6], size=10, color ="blue", align="right"))
    content_list.append(Slider(content_box, start=2, end=4, grid=[1,6,2,1], command=update_survivor, width="fill"))
    content_list[8].value = str(survivors)

    content_list.append(PushButton(content_box, text="Create", grid=[0,5], command=player_create, width="fill"))
    if characount > 0:
        content_list.append(PushButton(content_box, text="Edit", grid=[1,5], command=lambda: player_edit(int(content_list[1].value)), width="fill"))
        content_list.append(PushButton(content_box, text="Remove", grid=[2,5], command=lambda: player_remove(int(content_list[1].value)), width="fill"))
    content_list.append(PushButton(content_box, text="Begin", command=check_enoughchara, grid=[0,8], width="fill"))
    go_mainmenu([2,8], True)

    content_list.append(PushButton(content_box, text="Export", command=chara_export, grid=[0,7], width="fill"))
    content_list.append(PushButton(content_box, text="Import", command=chara_import, grid=[2,7], width="fill"))

    content_list.append(Text(content_box, text="Character List", grid=[0,1], size=10, color ="blue", align="bottom"))
    content_list.append(Text(content_box, text="Note : Minimum for charas are 8 and maximum are 20!", grid=[0,9,3,1], size=10, color ="red", align="bottom"))

# inserting texts into list
def play_initialize():
    event1_list.extend(readas_list("asset/event1.txt"))
    event2_list.extend(readas_list("asset/event2.txt"))
    event3_list.extend(readas_list("asset/event3.txt"))
    eventall_list.extend(readas_list("asset/eventall.txt"))
    died_list.extend(readas_list("asset/died.txt"))
    invest_list.extend(readas_list("asset/invest.txt"))
    clue_item_list.extend(readas_list("asset/clue_item.txt"))
    clue_place_list.extend(readas_list("asset/clue_place.txt"))
    clue_words_list.extend(readas_list("asset/clue_words.txt"))
    motive_list.extend(readas_list("asset/motive.txt"))
    punish_list.extend(readas_list("asset/punishment.txt"))
    play_charalist()

# to the menu screen
def go_mainmenu(listpos, mode):
    if not mode:
        content_list.append(PushButton(content_box, text="Menu", grid=listpos, command=menu_main))
    else:
        content_list.append(PushButton(content_box, text="Menu", grid=listpos, command=play_abandon))

# main menu screen
def menu_main():
    clean_contentlist()
    content_list.append(PushButton(content_box, text="Prepare Simulation", grid=[0,0,2,1], command=play_initialize, width="fill"))
    content_list.append(PushButton(content_box, text="Punishment", grid=[0,1], command=prev_punishment, width="fill"))
    content_list.append(PushButton(content_box, text="Motive", grid=[1,1], command=prev_motive, width="fill"))
    content_list.append(Picture(content_box, image=read_asimage(imagedefault, True), grid=[0,2,2,1]))

# update text values
def update_preview(value):
    if "{0}" in value:
        replacement = value
        replacement = replacement.replace("<[1]>", "he")
        replacement = replacement.replace("<[2]>", "his")
        replacement = replacement.replace("<[3]>", "him")
        content_list[1].value = replacement.format("Student A")
    else:
        content_list[1].value = value

# preview punishment
def prev_punishment():
    clean_contentlist()
    punish = readas_list("asset/punishment.txt")
    content_list.append(Text(content_box, text="Punishments Preview", grid=[0,0,2,1], size=10, color ="blue", width="fill"))

    content_list.append(Text(content_box, text="none", grid=[1,2], size=10, color ="red", align="left"))
    content_list.append(Text(content_box, text="Preview: ", grid=[0,2], size=10, color ="blue", align="left"))
    content_list.append(ListBox(content_box, scrollbar=True, items=punish, command=update_preview, grid=[0,1,2,1], width="fill"))
    go_mainmenu([0,3,2,1], False)

# preview motive
def prev_motive():
    clean_contentlist()
    motive = readas_list("asset/motive.txt")
    content_list.append(Text(content_box, text="Motives Preview", grid=[0,0,2,1], size=10, color ="blue", width="fill"))

    content_list.append(Text(content_box, text="none", grid=[1,2], size=10, color ="red", align="left"))
    content_list.append(Text(content_box, text="Preview: ", grid=[0,2], size=10, color ="blue", align="left"))
    content_list.append(ListBox(content_box, scrollbar=True, items=motive, command=update_preview, grid=[0,1,2,1], width="fill"))
    go_mainmenu([0,3,2,1], False)

def main():
    menu_main()
    app.display()

if __name__ == "__main__":
    main()