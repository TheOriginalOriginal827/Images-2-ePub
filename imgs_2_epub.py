import os
import time
import shutil
import sys
import itertools
from PIL import Image
from datetime import datetime
import uuid
import zipfile
import threading
        
### PREP

debug = False

settings={}

def roman(int):
    m = ["", "m", "mm", "mmm"]
    c = ["", "c", "cc", "ccc", "cd", "d", "dc", "dcc", "dccc", "cm"]
    x = ["", "x", "xx", "xxx", "xl", "l", "lx", "lxx", "lxxx", "xc"]
    i = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"]
    
    thous = m[int // 1000]
    hunds = c[(int%1000)//100]
    tens = x[(int%100)//10]
    ones = i[int%10]
    
    return (thous+hunds+tens+ones)

processDone = False
loadmsg=""
donemsg=""

def loadPrint():
    for frame in itertools.cycle(["...", "   ", ".  ", ".. "]):
        if processDone:
            sys.stdout.write(("\r"+loadmsg+"..."))
            sys.stdout.flush()
            break
        sys.stdout.write(("\r"+loadmsg+frame))
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\n"+donemsg+"\n")
        
def startLoadPrint(msg):
    global processDone
    global loadmsg
    processDone = False
    loadmsg = msg
    anim = threading.Thread(target=loadPrint)
    anim.start()
    
def endLoadPrint(msg):
    global processDone
    global donemsg
    donemsg = msg
    processDone = True
    time.sleep(0.2)

## DEFINE PATHS

while True:
    print(f"\nCurrent Path - {os.path.dirname(os.path.realpath(__file__))}")
    
    #GET EPUB PATH
    while True:
        settings.update({"epub_path": input("\nWhere do you want the file to be created? (Leave blank for current path): ")})
        if debug == True: print("EPUB PATH IN: "+settings["epub_path"])
        if(settings["epub_path"] == ""):
            settings.update({"epub_path": os.path.dirname(os.path.realpath(__file__))})
            break
        elif (os.path.exists(settings["epub_path"]) == False):
            print("\nPath is invalid!")
        else: break
        
    if debug == True: print("EPUB PATH: "+settings["epub_path"])
    
    ## GET IMAGE PATH
    while True:
        while True:
            settings.update({"img_path": input("\nWhere are your images stored? (Leave blank for current path): ")})
            if debug == True: print("IMAGE PATH IN: "+settings["img_path"])
            if(settings["img_path"] == ""):
                settings.update({"img_path": os.path.dirname(os.path.realpath(__file__))})
                break
            elif (os.path.exists(settings["img_path"]) == False):
                print("\nPath is invalid!")
            else:break

        if debug == True: print("IMAGE PATH SAVE: "+settings["img_path"])

        ## CHECK FOR IMAGES
        
        print("\nStarting search\n")
        
        startLoadPrint("Searching for images")
        
        if debug == True: print("FILES IN PATH: "+str(os.listdir(settings["img_path"])))
        
        imgs = [f for f in os.listdir(settings["img_path"]) if (f[:-4].replace(".", "").replace("img_", "")).isdigit()]

        if len(imgs) == 0:
            endLoadPrint("\nCould not find any images! Make sure your images are in the image path.")
            
        else:
            endLoadPrint(f"\n{str(len(imgs))} images found!")
            if debug == True: print("UNSORTED IMAGES: "+str(imgs))
            imgs.sort(key=lambda f: int(f[:-4].replace(".", "").replace("img_", "")))
            if debug == True: print("SORTED IMAGES: "+str(imgs))
            print(f"\nPaths set to:\nFile Path - {settings['epub_path']}!\nImage Path - {settings['img_path']}!")
            break
    break

## METADATA

def promptMeta(tochange, question, good, bad, invalidMsg):
    while True:
        response = input(question)
        if debug == True: print(f"META {tochange} RESPONSE {response}")
        if (bad != False) and (response in bad or response == bad):print(invalidMsg)
        elif (good != False) and (response not in good):print(invalidMsg)
        else: 
            settings.update({tochange:response})
            if debug == True: print(f"META {tochange} SET VALID {response}")
            break


promptMeta("filename", "\nEPUB File Name (Ex: 'My_Book', 'scott_pilgrim_1.epub'): ", False, ("", "/", "<", ">", ":", "\\", "|", "?", "*"), "\nFile name is blank or contains invalid characters. Please provide a file name.")

promptMeta("title", "\nWhat's the title of your book (Ex: Scott Pilgrim, Vol. 1: Precious Little Life): ", False, "", "\nTitle cannot be blank. Please provide a title.")

promptMeta("lang", "\nWhat language is your book in? MUST be well-formed language tag. (Look here for tags: https://r12a.github.io/app-subtags/)\n(Leave blank for default, 'en-US'): ", False, False, "\nInvalid language tag!")
if settings["lang"] == "": settings.update({"lang":"en-US"})

promptMeta("dateMod", "\nWhen is the 'last modified' date? (Time must be in UTC format!) (Leave blank for current time): ", False, False, "\nInvalid date modified!")
if settings["dateMod"] == "": settings.update({"dateMod": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")})

promptMeta("identifier", "\nPlease provide a unique identifier for your EPUB (Ex: UUID, DOI, ISBN)\nFor custom identifiers, include the type at the beginning of the identifier (EX: isbn:#####)\n(Leave blank for random UUID): ", False, False, "\nInvalid Identifier!")
if settings["identifier"] == "": settings.update({"identifier": "uuid:"+ str(uuid.uuid4())})

while True:
    promptMeta("pageStart", "\nWhat does your book consider 'Page 1'? (0 = Cover, 1 = 'Page 1', etc.): ", False, False, "\nInvalid page!")
    if settings["pageStart"].isdigit() == True: break
    else: print("\nInvalid Page!")
settings.update({"pageStart": int(settings["pageStart"])-1})

promptMeta("legacy", "\nWould you like to enable legacy compatability? (May be needed for old ePub readers) (y/n): ", ("y", "n"), False, "\nInvalid choice! Please type 'y' or 'n'.")


promptMeta("toc", "\nWould you like a table of contents? (y/n): ", ("y", "n"), False, "\nInvalid choice! Please type 'y' or 'n'.")

settings.update({"chapters": []})
if settings["toc"] == "y":
    while True:
        while True:
            chapter = input("\nWhat page does Chapter "+str(len(settings["chapters"])+1)+" start? (Leave blank to end): ")
            if debug == True: print("CHAPTER: "+chapter)
            if chapter != "":
                if chapter.isdigit():
                    settings["chapters"].append(chapter)
                else: 
                    print("\nNot a page!")
            else: break
        break
    if debug == True: print("CHAPTERS: "+str(settings["chapters"]))

    if len(settings["chapters"]) > 0: promptMeta("chapName", "\nWould you like to give your chapter custom names? (y/n): ", ("y", "n"), False, "\nInvalid choice! Please type 'y' or 'n'.")

    settings.update({"chapterNames": []})
    if settings["chapName"] == "y":
        for i in range(len(settings["chapters"])):
            name = input("\nPlease give a custom name to Chapter "+str(i+1)+" (Leave blank to skip): ")
            if name != "":
                settings["chapterNames"].append(name)
            else:
                settings["chapterNames"].append("Chapter "+str(i+1))
    else:
        for i in range(len(settings["chapters"])):
            settings["chapterNames"].append("Chapter "+str(i+1))

promptMeta("dir", "\nWhich way should your ePub be read? (Left-to-right for english and similar languages) (ltr/rtl): ", ("ltr", "rtl"), False, "Not a direction! Please type 'ltr' or 'rtl'")

promptMeta("optionalMeta", "\nWould you like to include additional metadata, such as authors?\n(It is heavily reccommended to add this metadata in in a seperate app like Calibre or Sigil instead)\n(y/n): ", ("y", "n"), False, "Please put 'y' or 'n'.")

settings.update({"titleSort": ""})
settings.update({"authors":[]})
settings.update({"authorSort":[]})
settings.update({"authorAltScript":[]})
settings.update({"contributors":[]})
settings.update({"contributorSort":[]})
settings.update({"contributorAltScript":[]})
settings.update({"pubdate":""})
settings.update({"publisher":""})
settings.update({"desc":""})

if settings["optionalMeta"] == "y":
    settings.update({"titleSort": input("\nHow should your title be sorted? (Ex: The Lord of the Rings -> Lord of the Rings, The)\n(Leave blank to skip): ")})
    if debug == True: print("TITLE SORT: "+settings["titleSort"])
    while True:
        auth = input("\nWho is an author of the book? (Person/Company that played a primary role in the creation of the book)\n(Leave blank to skip/end): ")
        if debug == True: print("AUTH: "+auth)
        if auth == "": break
        else: settings["authors"].append(auth)
    if debug == True: print("AUTHOR LIST: "+settings["authors"])
    if len(settings["authors"]) > 0:
        for i in range(len(settings["authors"])):
            while True:
                settings["authorSort"].append(input(f"\nFor each author, provide a sort name\n(Ex: Brian Lee O'Malley -> O'Malley, Bryan Lee)\nCurrent Author is {str(settings['authors'][i])}: "))
                if debug == True: print("AUTHOR SORT: "+settings["authorSort"])
                if settings["authorSort"] == "": print("\nPlease provide an author sort.")
                else: break
    if len(settings["authors"]) > 0:
        for i in range(len(settings["authors"])):
            while True:
                altScript = input("\nFor each author, you may provide an alt script (Ex: Hirohiko Araki, en -> 荒木 飛呂彦, jp)\n(Leave blank to skip author): ").replace(" ", "")
                if debug == True: print("ALT SCRIPT: "+altScript)
                if "," not in altScript: print("\nInvalid Alt-Script!")
                else:
                    settings["authorAltScript"].append(altScript)
                    break
            if debug == True: print("ALT SCRIPTS: "+settings["authorAltScripts"])
    while True:
        contributor = input("\nIs there a contributor of the book? (Person/Company that played a secondary role in book creation)\n(Leave blank to skip/end): ")
        if debug == True: print("CONTRIBUTOR: "+settings["contributor"])
        if contributor == "": break
        else: settings["contributors"].append(contributor)
    if debug == True: print("CONTRIBUTORS: "+settings["contributors"])
    if len(settings["contributors"]) > 0:
        for i in range(len(settings["contributors"])):
            while True:
                settings["contributorSort"].append(input(f"\nFor each contributor, provide a sort name\n(Ex: Brian Lee O'Malley -> O'Malley, Bryan Lee)\nCurrent Contributor is {settings['contributors'][i]}: "))
                if debug == True: print("CONTRIBUTOR SORT: "+settings["contributorSort"])
                if settings["contributorSort"] == "": print("\nPlease provide an contributor sort.")
                else: break
    if len(settings["contributors"]) > 0:
        for i in range(len(settings["contributors"])):
            while True:
                altScript = input("\nFor each contributor, you may provide an alt script (Ex: Hirohiko Araki, en -> 荒木 飛呂彦, jp)\n(Leave blank to skip contributor): ").replace(" ", "")
                if debug == True: print("CONTRIBUTOR ALT: "+altScript)
                if "," in altScript != True: print("\nInvalid Alt-Script!")
                else:
                    settings["contributorAltScript"].append(altScript)
                    break
            if debug == True: print("CONTR. ALT SCTIPTS: "+settings["contributorAltScripts"])
            
    settings.update({"publisher": input("\nDoes your book have a publisher? (Leave blank to skip): ")})
    if debug == True: print("PUBLISHER: "+settings["publisher"])
            
    settings.update({"pubdate": input("\nWhen was the publication date of your book? (Please write in UTC format)\n(Leave blank to skip): ")})
    if debug == True: print("PUBLICATION DATE: "+settings["pubdate"])
    
    settings.update({"desc": input("\nIf you would like to add a description, write it here (Leave blank to skip): ")})
    if debug == True: print("DESCRIPTION: "+settings["desc"])
    
### CREATE DIRECTORIES
print("\nMetadata gathered, starting filemaking proccess\n")
startLoadPrint("Creating directories")

## MAIN DIRECTORY

def create_directory(path):
    global donemsg
    global processDone
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            if debug == True: print(f"DIR {path}")
        except Exception as error:
            endLoadPrint(f"\nDirectory {path} can't be created. Reason: {error}")
            quit()
    else:
        if debug == True: print(f"{path} PRESENT")

def create_file(path, write):
    global donemsg
    global processDone
    try:
        with open((path), "a") as file:
            file.write(write)
        if debug == True: print (f"FILE {path}")
    except Exception as error:
        endLoadPrint(f"\File {path} can't be created. Reason: {error}")
        quit()

create_directory(os.path.join(settings["epub_path"], settings["filename"]))

create_file(os.path.join(settings["epub_path"], settings["filename"],"mimetype"), "application/epub+zip")

create_directory(os.path.join(settings["epub_path"], settings["filename"], "META-INF"))
create_directory(os.path.join(settings["epub_path"], settings["filename"], "OEBPS"))
create_directory(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", "images"))

endLoadPrint("\nDirectories Created!\n")

### COPY IMAGES

startLoadPrint("Copying images")

for i in range(len(imgs)):
    shutil.copy(os.path.join(settings["img_path"],imgs[i]), os.path.join(settings["epub_path"], settings["filename"],"OEBPS","images"))
    if debug==True:print(f"COPY {imgs[i]} ")

endLoadPrint("\nImages Copied!\n")

### FILES

## XHTML FILES + DYNAMIC CODE FOR OTHERS

stylesheet = "body {background-color: #fff;}\n\n"
navigation = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\">\n<head>\n    <title>{settings['title']}</title>\n    <link rel=\"stylesheet\" href=\"stylesheet.css\" type=\"text/css\"/>\n    <meta charset=\"utf-8\"/>\n</head>\n<body>\n    <nav xmlns:epub=\"http://www.idpf.org/2007/ops\" role=\"doc-toc\" epub:type=\"toc\" id=\"toc\">\n        <ol>"
pagelist = []
manifestXHTML = ""
spine = ""
startLoadPrint("Creating files")

for i in range(len(imgs)):
    pageImg = Image.open(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","images",imgs[i]))
    if pageImg.format == "JPEG": mediatype = "jpeg"
    elif pageImg.format == "PNG": mediatype = "png"
    elif pageImg.format == "GIF": mediatype = "gif"
    elif pageImg.format == "WebP": mediatype = "webp"
    page_num = i
    width, height = pageImg.size
    page_num -= int(settings["pageStart"])
    if i == 0:
        title = "Cover"
        file_name = "cover.xhtml"
        xhtml_code = f"<body class=\"body_cover\">\n    <div class=\"image_cover\">\n        <img src=\"images/{imgs[i]}\" alt=\"Cover)\"/>\n    </div>\n</body>"
        stylesheet += f"body.body_cover {{\n	width: {str(width)}px;\n	height: {str(height)}px;\n	margin: 0;\n}}\ndiv.image_cover > img {{\n	position: absolute;\n	height: {str(height)}px;\n	top: 0px;\n	left: 0px;\n	margin: 0;\n	z-index: 0;\n}}\n"
        if len(settings["chapters"]) == 0: navigation += "\n                <li>\n                    <a href=\"cover.xhtml\">Cover</a>\n                </li>\n"
        manifestXHTML += f"      <item id=\"cover\" href=\"cover.xhtml\" media-type=\"application/xhtml+xml\"/>\n      <item id=\"cover-image\" properties=\"cover-image\" href=\"images/{imgs[i]}\" media-type=\"image/{mediatype}\"/>\n"
        spine += "      <itemref idref=\"cover\" linear=\"yes\"/>\n"
        if page_num < 1:
            pagelist.append(roman(page_num+settings["pageStart"]+1))
        else:
            pagelist.append(str(page_num))
    elif page_num < 1:
        title = f"Page {roman(page_num+settings['pageStart']+1)}"
        file_name = f"pg_{roman(page_num+settings['pageStart']+1)}.xhtml"
        xhtml_code = f"<body class=\"body_{roman(page_num+settings['pageStart']+1)}\">\n    <div class=\"image_{roman(page_num+settings['pageStart']+1)}\">\n        <img src=\"images/{imgs[i]}\" width=\"{str(width)}\" height=\"{str(height)}\" alt=\"Page {roman(page_num+settings['pageStart']+1)}\" />\n    </div>\n</body>"
        stylesheet += f"body.body_{str(page_num)} {{	width: {str(width)}px; height: {str(height)}px;	margin: 0; }}\nimg.image_{str(page_num)} {{	position: absolute;	height: {str(height)}px;	top: 0px; left: 0px; margin: 0;	z-index: 0; }}\n\n"
        manifestXHTML += f"      <item id=\"xhtml_{str(i)}\" href=\"{file_name}\" media-type=\"application/xhtml+xml\"/>\n      <item id=\"{imgs[i]}\" href=\"images/{imgs[i]}\" media-type=\"image/{mediatype}\"/>\n"
        spine += f"      <itemref idref=\"xhtml_{str(i)}\" linear=\"yes\"/>\n"
        pagelist.append(roman(page_num+settings["pageStart"]+1))
    else:
        title = "Page "+str(page_num)
        file_name = f"pg_{str(page_num)}.xhtml"
        xhtml_code = f"<body class=\"body_{str(page_num)}\">\n    <div class=\"image_{str(page_num)}\">\n        <img src=\"images/{imgs[i]}\" width=\"{str(width)}\" height=\"{str(height)}\" alt=\"{str(page_num)}\" />\n    </div>\n</body>"
        stylesheet += f"body.body_{str(page_num)} {{	width: {str(width)}px; height: {str(height)}px;	margin: 0; }}\nimg.image_{str(page_num)} {{	position: absolute;	height: {str(height)}px;	top: 0px; left: 0px; margin: 0;	z-index: 0; }}\n\n"
        manifestXHTML += f"      <item id=\"xhtml_{str(i)}\" href=\"{file_name}\" media-type=\"application/xhtml+xml\"/>\n      <item id=\"{imgs[i]}\" href=\"images/{imgs[i]}\" media-type=\"image/{mediatype}\"/>\n"
        spine += f"      <itemref idref=\"xhtml_{str(i)}\" linear=\"yes\"/>\n"
        pagelist.append(str(page_num))
    xhtml_code = f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:epub=\"http://www.idpf.org/2007/ops\">\n\n<head>\n<meta charset=\"UTF-8\"/>\n<meta name=\"viewport\" content=\"width={str(width)}, height={str(height)}\" />\n<title>{title}</title>\n<link href=\"stylesheet.css\" type=\"text/css\" rel=\"stylesheet\" />\n</head>\n{xhtml_code}\n</html>"
    file_path = os.path.join(settings["epub_path"], settings["filename"], "OEBPS", file_name)
    pageImg.close()
    create_file(file_path, xhtml_code)

## STYLESHEET.CSS

create_file(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","stylesheet.css"), stylesheet)

## NAVIGATION DOCUMENT (NAV.XHTML)
for i in range(len(settings["chapters"])): navigation += f"\n            <li>\n                <a href=\"pg_{settings['chapters'][i]}.xhtml\">{settings['chapterNames'][i]}</a>\n            </li>\n"

navigation += "\n        </ol>\n    </nav>\n    <nav xmlns:epub=\"http://www.idpf.org/2007/ops\" role=\"doc-pagelist\" epub:type=\"page-list\" id=\"page-list\">\n        <ol>\n"

for i in range(len(pagelist)):
    if i == 0: navigation += f"          <li><a href=\"cover.xhtml\">{pagelist[i]} of {(len(pagelist)-settings['pageStart'])-1}</a></li>\n"
    else: navigation += f"          <li><a href=\"pg_{pagelist[i]}.xhtml\">{pagelist[i]} of {(len(pagelist)-settings['pageStart'])-1}</a></li>\n"

navigation += "       </ol>\n    </nav>\n</body>\n</html>"

create_file(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","nav.xhtml"), navigation)

## CONTAINER

create_file(os.path.join(settings["epub_path"], settings["filename"],"META-INF","container.xml"), "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">\n    <rootfiles>\n        <rootfile \n            full-path=\"OEBPS/content.opf\" \n            media-type=\"application/oebps-package+xml\"/>\n   </rootfiles>\n</container>\n")

## APPLE COMPATABILITY

create_file(os.path.join(settings["epub_path"], settings["filename"],"META-INF","com.apple.ibooks.display-options.xml"), "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<display_options>\n	<platform name=\"*\">\n		<option name=\"fixed-layout\">true</option>\n		<option name=\"open-to-spread\">true</option>\n	</platform>\n</display_options>\n")

## TABLE OF CONTENTS/NCX (LEGACY)

if settings["legacy"] == "y":
    ncxLegacy = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<ncx version=\"2005-1\" xml:lang=\"en-US\" xmlns=\"http://www.daisy.org/z3986/2005/ncx/\">\n    <head>\n        <meta name=\"dtb:uid\" content=\"{settings['identifier']}\"/>\n        <meta name=\"dtb:depth\" content=\"{len(pagelist)-settings['pageStart']}\"/>\n        <meta name=\"dtb:totalPageCount\" content=\"{len(pagelist)-settings['pageStart']}\"/>\n        <meta name=\"dtb:maxPageNumber\" content=\"{len(pagelist)-settings['pageStart']}\"/>\n    </head>\n    <docTitle>\n        <text>{settings['title']}</text>\n    </docTitle>\n    <navMap>\n"
    if len(settings["chapters"]) == 0:
        ncxLegacy += "        <navPoint id=\"cover\" playOrder=\"1\">\n            <navLabel>\n                <text>Cover</text>\n            </navLabel>\n            <content src=\"cover.xhtml\"/>\n        </navPoint>\n"
    else:
        for i in range(len(pagelist)):
            for j in range(len(settings["chapters"])):
                if pagelist[i] == settings["chapters"][j]:
                    ncxLegacy += f"        <navPoint id=\"chapter_{j+1}\" playOrder=\"{i-int(settings['pageStart'])}\">\n            <navLabel>\n                <text>{settings['chapterNames'][j]}</text>\n            </navLabel>\n            <content src=\"pg_{pagelist[i]}.xhtml\"/>\n        </navPoint>\n"
    ncxLegacy += "    </navMap>\n    <pageList>\n        <navLabel>\n            <text>Pages</text>\n        </navLabel>\n"

    if len(settings["chapters"]) != 0:
        ncxLegacy += "        <pageTarget type=\"normal\" id=\"cover_page\" value=\"0\" playOrder=\"1\">\n            <navLabel>\n                <text>Cover</text>\n            </navLabel>\n            <content src=\"cover.xhtml\"/>\n        </pageTarget>\n"
    for i in range(len(pagelist)):
        if pagelist[i] not in settings["chapters"] and i != 0: 
            ncxLegacy += f"        <pageTarget type=\"normal\" id=\"pg_{pagelist[i]}\" value=\"{i+1}\" playOrder=\"{i+1}\">\n            <navLabel>\n                <text>{pagelist[i]} of {(len(pagelist)-settings['pageStart'])-1}</text>\n            </navLabel>\n            <content src=\"pg_{pagelist[i]}.xhtml\"/>\n        </pageTarget>\n"
    ncxLegacy += "   </pageList>\n</ncx>"

    create_file(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","toc.ncx"), ncxLegacy)

## PACKAGE DOCUMENT (CONTENT.OPF)

package = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<package xmlns=\"http://www.idpf.org/2007/opf\" version=\"3.0\" unique-identifier=\"pub-id\" xml:lang=\"{settings['lang']}\" dir=\"{settings['dir']}\">\n    <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\">\n        <meta name=\"cover\" content=\"cover-image\" />\n        <dc:identifier id=\"pub-id\">{settings['identifier']}</dc:identifier>\n        <dc:language>{settings['lang']}</dc:language>\n        <meta property=\"dcterms:modified\">{settings['dateMod']}</meta>\n        <dc:title id=\"title\">{settings['title']}</dc:title>\n        <meta property=\"rendition:layout\">pre-paginated</meta>\n        <meta property=\"rendition:spread\">both</meta>\n"

if settings["optionalMeta"] == "y":
    if settings["titleSort"] != "": package += f"<meta property=\"file-as\" refines=\"#title\">{settings['titleSort']}</meta>\n"
        
    if len(settings["authors"]) > 0:
        for i in range(len(settings["authors"])):
            authorPkg = f"        <dc:creator id=\"creator_{str(i)}\">{settings['authors'][i]}</dc:creator>\n        <meta refines=\"#creator_{str(i)}\" property=\"file-as\">{settings['authorSort'][i]}</meta>\n"
            if settings['authorAltScript'][i] != "": authorPkg += f"       <meta refines=\"#creator_{str(i)}\" property=\"alternate-script\" xml:lang=\"{(settings['authorAltScript'][i]).split(',')[1]}\">{(settings['authorAltScript'][i]).split(',')[0]}</meta>\n"
            package += authorPkg

    if len(settings["contributors"]) > 0:
        for i in range(len(settings["contributors"])):
            contributorPkg = f"       <dc:contributor id=\"contributor_{str(i)}\">{settings['contributors'][i]}</dc:contributor>\n        <meta refines=\"#contributor_{str(i)}\" property=\"file-as\">{settings['contributorSort'][i]}</meta>\n"
            if settings['contributorAltScript'][i] != "": contributorPkg += f"      <meta refines=\"#contributor_{str(i)}\" property=\"alternate-script\" xml:lang=\"{(settings['contributorAltScript'][i]).split(',')[1]}\">{(settings['contributorAltScript'][i]).split(',')[0]}</meta>\n"
            package += contributorPkg

    if settings["pubdate"] != "": package += f"     <dc:date>{settings['pubdate']}</dc:date>\n"
    if settings["publisher"] != "": package += f"     <dc:publisher>{settings['publisher']}</dc:publisher>\n"

    if settings["desc"] != "": package += f"     <dc:description>\n{settings['desc']}\n</dc:description>\n"
    
package += "  </metadata>\n    <manifest>\n"

package += f"      <item id=\"toc\" properties=\"nav\" href=\"nav.xhtml\" media-type=\"application/xhtml+xml\"/>\n      <item id=\"style\" href=\"stylesheet.css\" media-type=\"text/css\"/>\n{manifestXHTML}\n"

if(settings["legacy"]) == "y": package += f"  <item id=\"ncx\" href=\"toc.ncx\" media-type=\"application/x-dtbncx+xml\"/>\n  </manifest>\n  <spine toc=\"ncx\" page-progression-direction=\"{settings['dir']}\">\n"
else: package += f"  </manifest>\n  <spine page-progression-direction=\"{settings['dir']}\">\n"

package += spine + "  </spine>\n</package>"

create_file(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","content.opf"), package)

### COMPILE TO EPUB
endLoadPrint("\nFiles Created!\n")

startLoadPrint("Creating ePub")

try:
    with zipfile.ZipFile(settings["epub_path"]+"\\"+settings["filename"]+".epub", 'w') as epub:
        epub.write(os.path.join(settings["epub_path"], settings["filename"], "mimetype"), "mimetype")
        for file in os.listdir(os.path.join(settings["epub_path"], settings["filename"], "META-INF")):
            epub.write(os.path.join(settings["epub_path"], settings["filename"], "META-INF", file), "META-INF\\"+file)
        for file in os.listdir(os.path.join(settings["epub_path"], settings["filename"], "OEBPS")):
            epub.write(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", file), "OEBPS\\"+file)
        for file in os.listdir(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", "images")):
            epub.write(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", "images", file), "OEBPS\\images\\"+file)
        if debug != True: shutil.rmtree(os.path.join(settings["epub_path"],settings["filename"]))
except Exception as error:
    print (f"File {os.path.join(settings['epub_path'], settings['filename'])}.epub can't be created. Reason: {error}")
    quit()

endLoadPrint(f"\nePub created at {settings['epub_path']}!")
quit()