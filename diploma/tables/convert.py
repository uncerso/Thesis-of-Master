import re

def checkValid(table):
    if len(table) == 0:
        print("table is empty")
        assert(False)

    ncols = len(table[0])
    for row in table:
        if len(row) != ncols:
            print("len(row) != ncols, len(row): ", len(row), ", ncols: ", ncols, sep="")
            print(*row)
            assert(False)

def addName(data, name):
    if name.startswith("GCF_"):
        name = re.search("GCF_(\d+.\d)", name)[1]

    data.append([name.replace("_complete_genome", "")
                     .replace("_draft_genome", "")
                     .replace("_", "\\_")])

def makeColoredValue(value, r, g, b):
    return "\cellcolor[RGB]{" + r + ", " + g + ", " + b + "} " + value

def addValue(data, match):
    data[-1].append(makeColoredValue(match[1], "255", "255", "255"))

def addColoredValue(data, match):
    data[-1].append(makeColoredValue(match[1], match[2], match[3], match[4]))

def readAndParse(filename):
    otherBlockStarterPatten = """data-original-title="(.*) &lt;span&gt;"""
    mismatchesBlockStarterPatten = """data-original-title="# mismatches &lt;span&gt;"""
    indelsBlockStarterPatten = """data-original-title="# indels &lt;span&gt;"""
    namePattern = """class="metric-name secondary">(.*)</span>"""
    valuePattern = """<td number="(.+)" style="background: rgb\((.+), (\d+), (\d+)\) none repeat scroll 0% 0%;"""
    headerValuePattern = """<td number="(.+)\""""
    otherValuePattern = """<td number="(.+)"><span>.+</span></td>"""

    with open(filename, encoding="utf-8") as inp:
        lines = [line.rstrip() for line in inp]

    mismatches = []
    indels = []
    currentPtr = None

    pos = 0
    while True:
        if pos == len(lines):
            break

        line = lines[pos]
        pos += 1

        match = re.search(mismatchesBlockStarterPatten, line)
        if match is not None:
            currentPtr = mismatches
            continue

        match = re.search(indelsBlockStarterPatten, line)
        if match is not None:
            currentPtr = indels
            continue

        match = re.search(otherBlockStarterPatten, line)
        if match is not None:
            currentPtr = None
            continue

        if currentPtr is None:
            continue

        match = re.search(namePattern, line)
        if match is not None:
            addName(currentPtr, match[1])
            continue

        if len(currentPtr) == 0:
            # skip all values within starter blocks
            continue

        match = re.search(valuePattern, line)
        if match is not None:
            addColoredValue(currentPtr, match)
            continue

        match = re.search(otherValuePattern, line)
        if match is not None:
            addValue(currentPtr, match)
            continue

        match = re.search(headerValuePattern, line)
        if match is not None:
            line = line + " " + lines[pos].lstrip()
            pos += 1
            match = re.search(valuePattern, line)
            if match is not None:
                addColoredValue(currentPtr, match)
                continue

    checkValid(mismatches)
    checkValid(indels)
    return (mismatches, indels)

def printTable(table, file):
    nrows = len(table)
    ncols = len(table[0])

    print("\\begin{tabular}{|l||" + "c|"*(ncols-1) + "}", sep="", file=file)
    print("\\hline", file=file)

    print("&", " & ".join([str(i) for i in range(1, ncols)]), "\\\\", file=file)

    print("\\hline", file=file)
    print("\\hline", file=file)

    for row in table:
        assert(len(row) == ncols)
        for i in range(ncols):
            endSep = " \\\\" if i + 1 == ncols else " & "
            print(row[i], end=endSep, file=file)
        print("\n\\hline", file=file)

    print("\\end{tabular}", file=file)

def writeToFile(originFile, newSuffix, data):
    with open(filename.replace(".html", "." + newSuffix + ".tex"), "w") as file:
        printTable(data, file)

### ================================================= ###

filenames = ["base20.html", "bmock12.html", "mix.html", "zymo.html"]

for filename in filenames:
    mismatches, indels = readAndParse(filename)
    writeToFile(filename, "mismatches", mismatches)
    writeToFile(filename, "indels", indels)
