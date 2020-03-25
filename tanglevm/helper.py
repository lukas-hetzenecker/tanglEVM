from iota import TryteString
from math import floor

# https://github.com/vbakke/trytes

TRYTE_CHARS = '9ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def encodeBytesAsTryteString(bytes):
    trytes = TryteString(b'')
    for value in bytes:
        value = int(value)
        firstValue = value % 27
        secondValue = int((value - firstValue) / 27)
        trytes += TRYTE_CHARS[firstValue] + TRYTE_CHARS[secondValue]
    return trytes


def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)]*n)


def decodeBytesFromTryteString(inputTrytes):
    if len(inputTrytes) % 2:
        return

    ba = bytearray(len(inputTrytes) % 2)

    for trytes in grouped(inputTrytes, 2):
        firstValue = TRYTE_CHARS.index(trytes[0])
        secondValue = TRYTE_CHARS.index(trytes[1])

        value = firstValue + secondValue * 27
        ba.append(value)

    return bytes(ba)

def encodeTryteStringAsBytes(tryte3Str):
    tryte3Values = convertTryte3CharsToValues(tryte3Str)
    tryte5Values = _shiftTrytes(tryte3Values, 3, 5)

    #return bytearray(tryte5Values)
    return bytes(tryte5Values)


def convertTryte3CharsToValues(tryte3Str):
    tryte3Values = [None] * len(tryte3Str)
    for i in range(len(tryte3Str)):
        value = TRYTE_CHARS.index(tryte3Str[i])
        if value < 0:
            return None
        tryte3Values[i] = value
    return tryte3Values


POWEROF3 = [1, 3, 9, 27, 3 * 27, 9 * 27, 27 * 27]
def _shiftTrytes(fromArray, sizeFrom, sizeTo):
    toArray = []
    trits = 0
    tmpTryte = 0
    padding = 0

    for i in range(len(fromArray)):
        if fromArray[i] > POWEROF3[sizeFrom]:
            padding = fromArray[i]
            break

        # Add new trits into the tryte
        factor = POWEROF3[trits]
        trits += sizeFrom
        tmpTryte += fromArray[i] * factor

        while trits >= sizeTo:
            tryte = tmpTryte % POWEROF3[sizeTo]
            tmpTryte = (tmpTryte - tryte) // POWEROF3[sizeTo]
            trits -= sizeTo
            toArray.append(tryte)

    while trits > 0:
        newTryte = tmpTryte % POWEROF3[sizeTo]
        tmpTryte = (tmpTryte - newTryte) // POWEROF3[sizeTo]
        trits -= sizeTo
        toArray.append(newTryte)

    if sizeTo > sizeFrom:
        # If going up in size, a padding code may be added at the end
        if trits < 0:
            toArray.append(POWEROF3[sizeTo] - floor(trits / sizeFrom))

    else:
        # When going down in size, check if any padding characters should be removed
        if padding != 0:
            skip = padding - POWEROF3[sizeFrom]
            #//console.log("skip last ", (skip), "chars");
            toArray = toArray[0:-skip]

    #//console.log('Converted '+fromArray+' from ' + sizeFrom + '-' + sizeTo + ': Length: ' + fromArray.length + '-' + toArray.length + ': Remaining trits: ' + trits);
    return toArray


def decodeTryteStringFromBytes(bytes):
    tryte3Values = _shiftTrytes(bytes, 5, 3)

    tryte3Str = convertTryte3ValuesToChars(tryte3Values)
    return tryte3Str


def convertTryte3ValuesToChars(tryte3Values):
    tryte3Str = ""
    value = 0
    for value in tryte3Values:
        if value < 0 or value >= len(TRYTE_CHARS):
            return None
        tryte3Str += TRYTE_CHARS[value]
    return tryte3Str

