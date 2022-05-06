import re

def checkValid(table):
    if len(table) == 0:
        print("table is empty")
        assert(False)

    ncols = len(table[0])
    for row in table:
        if len(row) != ncols:
            print("len(row) != ncols, len(row): ", len(row), ", ncols: ", ncols, sep="")
            print("============[ row ]============")
            print(*row)
            print("============[ table ]============")
            print(*table)
            assert(False)

def checkValidRow(table):
    if len(table) != 1:
        print("table is not a row; len(table):", len(table))
        print(table)
        assert(False)
    if len(table[0]) <= 1:
        print("there is no data in the row:")
        print(table[0])
        assert(False)


def addName(data, name):
    if name.startswith("GCF_"):
        name = re.search("GCF_(\d+.\d)", name)[1]

    data.append([name.replace("_complete_genome", "")
                     .replace("_draft_genome", "")
                     .replace("_", " ")])

def makeColoredValue(value, r, g, b, makeWhiteTextColor):
    dotPos = value.find('.')
    if dotPos != -1 and len(value) - dotPos > 3:
        value = value[:-1]
    if makeWhiteTextColor:
        value = "\white{" + value + "}"
    return "\cellcolor[RGB]{" + r + ", " + g + ", " + b + "} " + value

def addValue(data, match):
    data[-1].append(makeColoredValue(match[1], "255", "255", "255", False))

def addColoredValue(data, match, makeWhiteTextColor):
    data[-1].append(makeColoredValue(match[1], match[2], match[3], match[4], makeWhiteTextColor))

def readAndParse(filename):
    hasWhiteColorPattern = "color: white"

    blockStarterHead = "data-original-title=\""
    blockStarterTail = " &lt;span&gt;"

    otherBlockStarterPatten = blockStarterHead + "(.*)" + blockStarterTail

    mismatchesBlockStarterPatten = blockStarterHead + "# mismatches" + blockStarterTail
    indelsBlockStarterPatten = blockStarterHead + "# indels" + blockStarterTail

    mismatchesPer100kbpBlockStarterPatten = blockStarterHead + "# mismatches per 100 kbp" + blockStarterTail
    indelsPer100kbpBlockStarterPatten = blockStarterHead + "# indels per 100 kbp" + blockStarterTail
    genFracBlockStarterPatten = blockStarterHead + "Genome fraction \(%\)" + blockStarterTail
    misassembliesBlockStarterPatten = blockStarterHead + "# misassemblies" + blockStarterTail

    namePattern = """class="metric-name secondary">(.*)</span>"""
    valuePattern = """<td number="(.+)" style="background: rgb\((.+), (\d+), (\d+)\) none repeat scroll 0% 0%;"""
    headerValuePattern = """<td number="(.+)\""""
    otherValuePattern = """<td number="(.+)"><span>.+</span></td>"""

    with open(filename, encoding="utf-8") as inp:
        lines = [line.rstrip() for line in inp]

    mismatches = []
    indels = []

    mismatchesPer100kbp = [["Замены на 100kbp"]]
    indelsPer100kbp = [["Вставки и удаления на 100kbp"]]
    misassemblies = [["Структурные ошибки"]]
    genFrac = [["Покрытие генома"]]

    readOnlyStarterBlock = False
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
            readOnlyStarterBlock = False
            continue

        match = re.search(indelsBlockStarterPatten, line)
        if match is not None:
            currentPtr = indels
            readOnlyStarterBlock = False
            continue

        match = re.search(genFracBlockStarterPatten, line)
        if match is not None:
            currentPtr = genFrac
            readOnlyStarterBlock = True
            continue

        match = re.search(misassembliesBlockStarterPatten, line)
        if match is not None:
            currentPtr = misassemblies
            readOnlyStarterBlock = True
            continue

        match = re.search(mismatchesPer100kbpBlockStarterPatten, line)
        if match is not None:
            currentPtr = mismatchesPer100kbp
            readOnlyStarterBlock = True
            continue

        match = re.search(indelsPer100kbpBlockStarterPatten, line)
        if match is not None:
            currentPtr = indelsPer100kbp
            readOnlyStarterBlock = True
            continue

        match = re.search(otherBlockStarterPatten, line)
        if match is not None:
            currentPtr = None
            continue

        if currentPtr is None:
            continue

        match = re.search(namePattern, line)
        if match is not None:
            if readOnlyStarterBlock:
                currentPtr = None
            else:
                addName(currentPtr, match[1])
            continue

        if not readOnlyStarterBlock and len(currentPtr) == 0:
            # skip all values within starter blocks
            continue

        match = re.search(valuePattern, line)
        if match is not None:
            makeWhiteTextColor = re.search(hasWhiteColorPattern, line) is not None
            addColoredValue(currentPtr, match, makeWhiteTextColor)
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
                makeWhiteTextColor = re.search(hasWhiteColorPattern, line) is not None
                addColoredValue(currentPtr, match, makeWhiteTextColor)
                continue

    checkValid(mismatches)
    checkValid(indels)
    checkValidRow(mismatchesPer100kbp)
    checkValidRow(indelsPer100kbp)
    checkValidRow(genFrac)
    checkValidRow(misassemblies)
    generalInfo = [genFrac[0], misassemblies[0], mismatchesPer100kbp[0], indelsPer100kbp[0]]
    checkValid(generalInfo)
    return mismatches, indels, generalInfo

def printTable(table, file):
    nrows = len(table)
    ncols = len(table[0])

    print("\\begin{adjustbox}{center}", file=file)
    # print("\\begin{tabularx}{\\textwidth}{|X||" + "c|"*(ncols-1) + "}", sep="", file=file)
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
    print("\\end{adjustbox}", file=file)

def writeToFile(originFile, newSuffix, data, useResizebox=False):
    with open(filename + "." + newSuffix + ".tex", "w") as file:
        if useResizebox:
            print("\\resizebox{0.8\\columnwidth}{!}{", file=file)
        printTable(data, file)
        if useResizebox:
            print("}", file=file)

def dropLastColumn(data):
    for line in data:
        line.pop()
### ================================================= ###

filenames = ["base20", "bmock12", "mix", "zymo"]

for filename in filenames:
    mismatches, indels, generalInfo = readAndParse(filename + ".html")
    writeToFile(filename, "mismatches", mismatches)
    writeToFile(filename, "indels", indels)
    writeToFile(filename, "general", generalInfo)
    if filename == "mix":
        dropLastColumn(mismatches)
        dropLastColumn(indels)
        writeToFile(filename, "mismatches_for_preso", mismatches)
        writeToFile(filename, "indels_for_preso", indels)
    else:
        writeToFile(filename, "general_for_preso", generalInfo, True)
