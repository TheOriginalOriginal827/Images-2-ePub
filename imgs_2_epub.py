import os
import shutil
from PIL import Image
from datetime import datetime, timezone
import uuid
import zipfile

### PREP

debug = False

settings={}

## DEFINE PATHS

while True:
    print(f"\nCurrent Path - {os.path.dirname(os.path.realpath(__file__))}")

    #GET EPUB PATH
    while True:
        settings.update({"epub_path": input("\nWhere do you want the file to be created? (Leave blank for current path): ")})
        if(settings["epub_path"] == ""):
            settings.update({"epub_path": os.path.dirname(os.path.realpath(__file__))})
            break
        elif (os.path.exists(settings["epub_path"]) == False):
            if debug is True: print("INPUT FAIL "+settings["epub_path"])
            print("\nPath is invalid!")
        else:
            break

    if debug is True: print("INPUT SUCCEED "+settings["epub_path"])
    
    ## GET IMAGE PATH

    while True:
        settings.update({"img_path": input("\nWhere are your images stored? (Leave blank for current path): ")})
        if(settings["img_path"] == ""):
            settings.update({"img_path": os.path.dirname(os.path.realpath(__file__))})
            break
        elif (os.path.exists(settings["img_path"]) == False):
            if debug is True: print("INPUT FAIL "+settings["img_path"])
            print("\nPath is invalid!")
        else:
            break

    if debug is True: print("INPUT SUCCEED "+settings["img_path"])

    ## DETECT IMAGES

    print("\nSearching for images...")

    if debug is True: print("FOUND TOTAL FILES "+str(os.listdir(settings["img_path"])))
    
    imgs = [f for f in os.listdir(settings["img_path"]) if (f[:-4].replace(".", "").replace("img_", "")).isdigit()]

    if len(imgs) == 0:
        print("\nCould not find any images! Make sure your images are in the image path.")
        quit()

    else:
        if debug is True: print("IMGS "+str(imgs))

        imgs.sort(key=lambda f: int(f[:-4].replace(".", "").replace("img_", "")))
        
        if debug is True: print("IMGS SORTED: "+str(imgs))
        
        print("\n"+str(len(imgs)) + " images found!")
    
    print(f"\nPaths set to:\nFile Path - {settings['epub_path']}\nImage Path - {settings['img_path']}")
    break

## METADATA

while True:
    settings.update({"filename": (input("\nEPUB File Name (Ex: 'My_Book', 'scott_pilgrim_1.epub'): ").replace(".epub", "")).replace("'", "")})
    if settings["filename"] != "":
        break
    else:
        print("\File name cannot be blank. Please provide a file name.")

if debug is True: print("FILENAME "+ settings["filename"])

while True:
    settings.update({"title": input("\nWhat's the title of your book (Ex: Scott Pilgrim, Vol. 1: Precious Little Life): ")})
    if settings["title"] != "":
        break
    else:
        print("\nTitle cannot be blank. Please provide a title.")

if debug is True: print("TITLE "+settings["title"])

settings.update({"lang": input("\nWhat language is your book in? MUST be well-formed language tag.\n(Look here for tags: https://r12a.github.io/app-subtags/) (Leave blank for default, 'en-US'): ")})
if settings["lang"] == "":
    settings.update({"lang":"en-US"})

if debug is True: print("INPUT SUCCEED "+settings["lang"])

settings.update({"dateMod" : input("\nWhen is the 'last modified' date? (Time must be in UTC format!) (Leave blank for current time): ")})
if settings["dateMod"] == "":
    settings.update({"dateMod": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")})

if debug is True: print("INPUT SUCCEED "+str(settings["dateMod"]))

settings.update({"identifier": input("\nPlease provide a unique identifier for your EPUB (Ex: UUID, DOI, ISBN)\nFor custom identifiers, include the type at the beginning of the identifier (EX: isbn:#####) (Leave blank for random UUID): ")})
if settings["identifier"] == "":
    settings.update({"identifier": "uuid:"+ str(uuid.uuid4())})

if debug is True: print("INPUT SUCCEED "+str(settings["identifier"]))

while True:
    settings.update({"pageAfterCover": input("\nAfter the cover page, should it continue with Page 1, or Page 2? (Answer with 1/2): ")})
    if settings["pageAfterCover"] == "1" or settings["pageAfterCover"] == "2":
        break
    else:
        print("Invalid Input!")

if debug is True: print("INPUT SUCCEED "+settings["pageAfterCover"])

while True:
    settings.update({"legacy": input("\nWould you like to enable legacy compatability? (May be needed for old ePub readers) (y/n): ")})
    if settings["legacy"] != "y" and settings["legacy"] != "n":
        print("Invalid Input!")
    else:
        break

if debug is True: print("INPUT SUCCEED "+settings["legacy"])

while True:
    settings.update({"toc": input("\nWould you like a table of contents? (y/n): ")})
    if settings["toc"] != "y" and settings["toc"] != "n":
        print("Invalid Input!")
    else:
        break

if debug is True: print("INPUT SUCCEED "+settings["toc"])

settings.update({"chapters": []})
if settings["toc"] == "y":
    while True:
        while True:
            chapter = input("\nWhat page does your (next) chapter start? (Leave blank to end): ")
            if chapter != "":
                if chapter.isdigit():
                    settings["chapters"].append(chapter)
                    if debug is True: print("INPUT SUCCEED "+chapter)
                else:
                    print("Invalid page!")
            else:
                break
        break
    if debug is True: print("INPUTS SUCCEED "+str(settings["chapters"]))

while True:
    settings.update({"dir": input("\nWhich way should your ePub be read? (Left-to-right for english and similar languages) (ltr/rtl): ")})
    if settings["dir"] != "ltr" and settings["dir"] != "rtl":
        print("Invalid Input!")
    else:
        break
    
if debug is True: print("INPUT SUCCEED "+settings["dir"])

while True:
    settings.update({"optionalMeta": input("\nWould you like to include additional metadata, such as authors?\n(It is heavily reccommended to add this metadata in in a seperate app like Calibre or Sigil instead) (y/n): ")})
    if settings["optionalMeta"] != "y" and settings["optionalMeta"] != "n":
        print("Invalid Input!")
    else:
        break

if debug is True: print("INPUT SUCCEED "+settings["optionalMeta"])

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
    settings.update({"tilteSort": input("\nHow should your title be sorted? (Ex: The Lord of the Rings -> Lord of the Rings, The) (Leave blank to skip): ")})
    while True:
        auth = input("\nWho is an author of the book? (Person/Company that played a primary role in the creation of the book) (Leave blank to skip/end): ")
        if auth == "":
            break
        else:
            settings["authors"].append(auth)
    if len(settings["authors"]) > 0:
        for i in range(len(settings["authors"])):
            while True:
                settings["authorSort"].append(input("\nFor each author, provide a sort name (Ex: Brian Lee O'Malley -> O'Malley, Bryan Lee)\nCurrent Author is "+ str(settings["authors"][i]) + ": "))
                if settings["authorSort"] == "":
                    print("\nPlease provide an author sort.")
                else:
                    break
    if len(settings["authors"]) > 0:
        for i in range(len(settings["authors"])):
            while True:
                altScript = input("\nFor each author, you may provide an alt script (Ex: Hirohiko Araki, en -> 荒木 飛呂彦, jp) (Leave blank to skip author): ").replace(" ", "")
                if "," in altScript != True:
                    print("Invalid Alt-Script!")
                else:
                    settings["authorAltScript"].append(altScript)
                    break
            
    while True:
        contributor = input("\nIs there a contributor of the book? (Person/Company that played a secondary role in book creation) (Leave blank to skip/end): ")
        if contributor == "":
            break
        else:
            settings["contributors"].append(contributor)
    if len(settings["contributors"]) > 0:
        for i in range(len(settings["contributors"])):
            while True:
                settings["contributorSort"].append(input("\nFor each contributor, provide a sort name (Ex: Brian Lee O'Malley -> O'Malley, Bryan Lee)\nCurrent Contributor is "+ str(settings["contributors"][i]) + ": "))
                if settings["contributorSort"] == "":
                    print("\nPlease provide an contributor sort.")
                else:
                    break
    if len(settings["contributors"]) > 0:
        for i in range(len(settings["contributors"])):
            while True:
                altScript = input("\nFor each contributor, you may provide an alt script (Ex: Hirohiko Araki, en -> 荒木 飛呂彦, jp) (Leave blank to skip contributor): ").replace(" ", "")
                if "," in altScript != True:
                    print("Invalid Alt-Script!")
                else:
                    settings["contributorAltScript"].append(altScript)
                    break
            
    settings.update({"pubdate": input("\nWhat was the publication date of your book? (Please write in UTC format) (Leave blank to skip): ")})

    settings.update({"publisher": input("\nDoes your book have a publisher? (Leave blank to skip): ")})   
    
    settings.update({"desc": input("\nIf you would like to add a description, write it here (Leave blank to skip): ")})
    
### CREATE DIRECTORIES
print("Creating Directories")

## MAIN DIRECTORY

def create_directory(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"\nDirectory {path} created!")
        except OSError as error:
            print(f"\nDirectory {path} can't be created. Reason: {error}")
            quit()
    else:
        print(f"\n{path} already exists!")

create_directory(os.path.join(settings["epub_path"], settings["filename"]))

## MIMETYPE

try:
    with open(os.path.join(settings["epub_path"], settings["filename"],"mimetype"), "a") as mimetype:
        mimetype.write("application/epub+zip")
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\mimetype created!")
except OSError as error:
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\mimetype can't be created. Reason: {error}")
    quit()

create_directory(os.path.join(settings["epub_path"], settings["filename"], "META-INF"))
create_directory(os.path.join(settings["epub_path"], settings["filename"], "OEBPS"))
create_directory(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", "images"))

print("Directories Created!")

### COPY IMAGES/

print("Copying Images")

for i in range(len(imgs)):
    shutil.copy(os.path.join(settings["img_path"],imgs[i]), os.path.join(settings["epub_path"], settings["filename"],"OEBPS","images"))
    print(f"\nImage `{imgs[i]}` copied.")

print("Images Copied!")

### FILES

## XHTML FILES + DYNAMIC CODE FOR OTHERS

stylesheet = """body {background-color: #fff;}\n\n"""
navigation = f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{settings["title"]}</title>
    <link rel="stylesheet" href="stylesheet.css" type="text/css"/>
    <meta charset="utf-8"/>
</head>
    <body>
        <nav xmlns:epub="http://www.idpf.org/2007/ops" role="doc-toc" epub:type="toc" id="toc">
            <ol>"""
pagelist = []
manifestXHTML = """"""
spine = """"""
print("Creating XHTML Files...")

for i in range(len(imgs)):
    print(imgs[i])
    if imgs[i].endswith((".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi")):
        mediatype = "jpeg"
    elif imgs[i].endswith((".png")):
        mediatype = "png"
    elif imgs[i].endswith((".gif")):
        mediatype = "gif"
    elif imgs[i].endswith(("webp")):
        mediatype = "webp"
    page_num = i
    width, height = Image.open(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","images",imgs[i])).size
    if settings["pageAfterCover"] == "1":
        page_num -= 1
    if i == 0:
        title = "Cover"
        file_name = "cover.xhtml"
        xhtml_code = f"""<body class="body_cover">
    <div class="image_cover">
        <img src="images/{imgs[i]}" alt="Cover)"/>
    </div>
</body>"""
        stylesheet += """body.body_cover {
	width: """+str(width)+"""px;
	height: """+str(height)+"""px;
	margin: 0;
}
div.image_cover > img {
	position: absolute;
	height: """+str(height)+"""px;
	top: 0px;
	left: 0px;
	margin: 0;
	z-index: 0;
}
"""
        if len(settings["chapters"]) == 0:
            navigation += """
                    <li>
                        <a href="cover.xhtml">Cover</a>
                    </li>
"""
        manifestXHTML += f"""      <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
      <item id="cover-image" properties="cover-image" href="images/{imgs[i]}" media-type="image/{mediatype}"/>
"""
        spine += """      <itemref idref="cover" linear="yes"/>
"""
        pagelist.append("Cover")
    else:
        title = "Page "+str(page_num)
        file_name = f"pg_{str(i)}.xhtml"
        xhtml_code = f"""<body class="body_{str(i)}">
    <div class="image_{str(i)}">
        <img src="images/{imgs[i]}" width="{str(width)}" height="{str(height)}" alt="{str(page_num)}" />
    </div>
</body>"""
        f'<img src="images/{imgs[i]}" width="{str(width)}" height="{str(height)}" alt="{file_name}" />'
        stylesheet += """body.body_"""+str(i)+""" {	width: """+str(width)+"""px; height: """+str(height)+"""px;	margin: 0; }
img.image_"""+str(i)+""" {	position: absolute;	height: """+str(height)+"""px;	top: 0px; left: 0px; margin: 0;	z-index: 0; }

"""
        manifestXHTML += f"""      <item id="xhtml_{str(i)}" href="{file_name}" media-type="application/xhtml+xml"/>
      <item id="{imgs[i]}" href="images/{imgs[i]}" media-type="image/{mediatype}"/>
"""
        spine += f"""      <itemref idref="xhtml_{str(i)}" linear="yes"/>
"""
        pagelist.append(str(page_num))
    xhtml_code = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">

<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width={str(width)}, height={str(height)}" />
<title>{title}</title>
<link href="stylesheet.css" type="text/css" rel="stylesheet" />
</head>

{xhtml_code}
</html>"""

    try:
        file_path = os.path.join(settings["epub_path"], settings["filename"], "OEBPS", file_name)
        with open(file_path, "a") as xhtml:
            xhtml.write(xhtml_code)
            print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\{file_name} created!")
    except OSError as error:
        print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\{file_name} can't be created. Reason: {error}")
        quit()

## STYLESHEET.CSS

try:
    with open((os.path.join(settings['epub_path'], settings['filename'],"OEBPS","stylesheet.css")), "a") as css:
        css.write(stylesheet)
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\stylesheet.css created!")
except OSError as error:
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\stylesheet.css can't be created. Reason: {error}")
    quit()

## NAVIGATION DOCUMENT (NAV.XHTML)
for i in range(len(settings["chapters"])):
    navigation += f"""
                <li>
                    <a href="pg_{settings["chapters"][i]}.xhtml">Chapter {i+1}</a>
                </li>
"""

navigation += """
            </ol>
        </nav>
        <nav xmlns:epub="http://www.idpf.org/2007/ops" role="doc-pagelist" epub:type="page-list" id="page-list">
            <ol>
"""

for i in range(len(pagelist)):
    if i == 0:
        navigation += f"""                <li><a href="cover.xhtml">{pagelist[i]}</a></li>
"""
    else:
        navigation += f"""                <li><a href="pg_{i}.xhtml">{pagelist[i]}</a></li>
"""

navigation += """           </ol>
        </nav>
    </body>
</html>"""

try:
    with open(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","nav.xhtml"), "a") as nav:
        nav.write(navigation)
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\nav.xhtml created!")
except OSError as error:
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\nav.xhtml can't be created. Reason: {error}")
    quit()

## CONTAINER

try:
    with open(os.path.join(settings["epub_path"], settings["filename"],"META-INF","container.xml"), "a") as container:
        container.write("""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile 
            full-path="OEBPS/content.opf" 
            media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
""")
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\META-INF\\container.xml created!")
except OSError as error:
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\META-INF\\container.xml can't be created. Reason: {error}")
    quit()
    

## APPLE COMPATABILITY
try:
    with open(os.path.join(settings["epub_path"], settings["filename"],"META-INF","com.apple.ibooks.display-options.xml"), "a") as apple:
        apple.write("""<?xml version="1.0" encoding="UTF-8"?>
<display_options>
	<platform name="*">
		<option name="fixed-layout">true</option>
		<option name="open-to-spread">true</option>
	</platform>
</display_options>
""")
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\META-INF\\container.xml created!")
except OSError as error:
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\META-INF\\container.xml can't be created. Reason: {error}")
    quit()

## TABLE OF CONTENTS/NCX (LEGACY)

if settings["legacy"] == "y":
    ncxLegacy = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd/">
<ncx version="2005-1" xml:lang="en-US" xmlns="http://www.daisy.org/z3986/2005/ncx/">
    <head>
        <meta name="dtb:uid" content="{settings['identifier'].split(":")[1]}"/>
        <meta name="dtb:depth" content="{1 + len(settings["chapters"])}"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{settings['title']}</text>
    </docTitle>
    <navMap>
        <navPoint id="cover" playOrder="1">
            <navLabel>
                <text>Cover</text>
            </navLabel>
            <content src="cover.xhtml"/>
        </navPoint>
"""
    for i in range(len(settings["chapters"])):
        ncxLegacy += f"""       <navPoint id="chapter_{i}" playOrder="{str(i+2)}">
            <navLabel>
                <text>Chapter {str(i+1)}</text>
            </navLabel>
            <content src="pg_{settings["chapters"][i]}.xhtml"/>
        </navPoint>
    """
    ncxLegacy += """    </navMap>
    <pageList>
        <navLabel>
            <text>Pages</text>
        </navLabel>
"""

    for i in range(len(pagelist)):
        if i == 0:
            ncxLegacy += f"""        <pageTarget type="normal" id="coverPage" value="{str(i)}" playOrder="{str(i+1)}">
            <navLabel>
                <text>Cover</text>
            </navLabel>
            <content src="cover.xhtml"/>
        </pageTarget>
"""
        else:
            ncxLegacy += f"""        <pageTarget type="normal" id="pg_{str(i)}" value="{str(i)}" playOrder="{str(i+1)}">
            <navLabel>
                <text>{str(i)}</text>
            </navLabel>
            <content src="pg_{str(i)}.xhtml"/>
        </pageTarget>
"""
    ncxLegacy += """   </pageList>
</ncx>"""

    try:
        with open(os.path.join(settings['epub_path'], settings['filename'],"OEBPS","toc.ncx"), "a") as ncx:
            ncx.write(ncxLegacy)
        print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\toc.ncx created!")
    except OSError as error:
        print (f"\nFile {settings[os.path.join(settings['epub_path'], settings['filename'])]}\\OEBPS\\toc.ncx can't be created. Reason: {error}")
        quit()

## PACKAGE DOCUMENT (CONTENT.OPF)

package = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="{settings["lang"]}" dir="{settings["dir"]}">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <meta name="cover" content="cover-image" />
        <dc:identifier id="pub-id">{settings["identifier"]}</dc:identifier>
        <dc:language>{settings["lang"]}</dc:language>
        <meta
            property="dcterms:modified">
            {settings['dateMod']}
        </meta>
        <dc:title id="title">{settings["title"]}</dc:title>
        <meta property="rendition:layout">pre-paginated</meta>
        <meta property="rendition:spread">both</meta>
"""

if settings["optionalMeta"] == "y":
    if settings["titleSort"] != "":
        package += f"""<meta
            property="file-as"
            refines="#title">
            {settings["titleSort"]}
            </meta>
"""
        
    if len(settings["authors"]) > 0:
        for i in range(len(settings["authors"])):
            authorPkg = f"""        <dc:creator 
            id="creator_{str(i)}">
            {settings["authors"][i]}
        </dc:creator>
        <meta
            refines="#creator_{str(i)}"
            property="file-as">
            {settings["authorSort"][i]}
        </meta>
"""
            if settings['authorAltScript'][i] != "":
                authorPkg += f"""       <meta
            refines="#creator_{str(i)}"
            property="alternate-script"
            xml:lang="{(settings["authorAltScript"][i]).split(",")[1]}">
            {(settings["authorAltScript"][i]).split(",")[0]}
        </meta>
"""
            package += authorPkg

    if len(settings["contributors"]) > 0:
        for i in range(len(settings["contributors"])):
            contributorPkg = f"""       <dc:contributor 
            id="contributor_{str(i)}">
            {settings["contributors"][i]}
        </dc:contributor>
        <meta
            refines="#contributor_{str(i)}"
            property="file-as">
            {settings["contributorSort"][i]}
        </meta>
"""
            if settings['contributorAltScript'][i] != "":
                contributorPkg += f"""      <meta
            refines="#contributor_{str(i)}"
            property="alternate-script"
            xml:lang="{(settings["contributorAltScript"][i]).split(",")[1]}">
            {(settings["contributorAltScript"][i]).split(",")[0]}
        </meta>
"""
            package += contributorPkg

    if settings["pubdate"] != "":
        package += f"""     <dc:date>
            {settings['pubdate']}
        </dc:date>
"""
    if settings["publisher"] != "":
        package += f"""     <dc:publisher>
            {settings['publisher']}
        </dc:publisher>
"""

    if settings["desc"] != "":
        package += f"""     <dc:description>
            {settings['desc']}
        </dc:description>
"""
    
package += """  </metadata>
    <manifest>
"""

if settings["legacy"] == "y":
    package += """  <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>"""

package += """      <item id="toc" properties="nav" href="nav.xhtml" media-type="application/xhtml+xml"/>
      <item id="style" href="stylesheet.css" media-type="text/css"/>
""" + manifestXHTML + """   </manifest>
"""

if(settings["legacy"]) == "y":
    package += f"""  <spine toc="ncx" page-progression-direction="{settings["dir"]}">
"""
else:
    package += f"""  <spine page-progression-direction="{settings["dir"]}">
"""

package += spine + """  </spine>
</package>"""

try:
    with open(os.path.join(settings["epub_path"], settings["filename"],"OEBPS","content.opf"), "a") as opf:
        opf.write(package)
    print (f"\nFile {os.path.join(settings['epub_path'], settings['filename'])}\\OEBPS\\content.opf created!")
except OSError as error:
    print (f"\nFile {settings['epub_path']}\\OEBPS\\content.opf can't be created! Reason: {error}")
    quit()

### COMPILE TO EPUB

print("\nCreating ePub (This may take a while)...")


try:
    with zipfile.ZipFile(settings["epub_path"]+"\\"+settings["filename"]+".zip", 'w') as zip:
        zip.write(os.path.join(settings["epub_path"], settings["filename"], "mimetype"), "mimetype")
        
        for file in os.listdir(os.path.join(settings["epub_path"], settings["filename"], "META-INF")):
            zip.write(os.path.join(settings["epub_path"], settings["filename"], "META-INF", file), "META-INF\\"+file)
        
        for file in os.listdir(os.path.join(settings["epub_path"], settings["filename"], "OEBPS")):
            zip.write(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", file), "OEBPS\\"+file)
        
        for file in os.listdir(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", "images")):
            zip.write(os.path.join(settings["epub_path"], settings["filename"], "OEBPS", "images", file), "OEBPS\\images\\"+file)
    if debug != True:
        shutil.rmtree(os.path.join(settings["epub_path"],settings["filename"]))
    shutil.move(settings["epub_path"]+"\\"+settings["filename"]+".zip", settings["epub_path"]+"\\"+settings["filename"]+".epub")
except OSError as error:
    print (f"File {os.path.join(settings['epub_path'], settings['filename'])}.epub can't be created. Reason: {error}")
    quit()

print(f"\nePub created at {settings['epub_path']}!\n")
quit()