import zlib
from time import time
from json import dumps
import struct
import base64
from numpy import array

void = None

class StreamEntry:
  def __init__(self, compressionFunc, ttd, image):
    self.setCompressionFunc(compressionFunc)
    self._ttd = ttd
    self.output = self.create(image)
  
  def _flatten(self, container):
    l = []
    for i in container:
      if isinstance(i, (list, tuple)):
        for j in self._flatten(i):
          l.append(j)
      else:
        l.append(i)
    return l

  def imageToCompressedVector(self, image) -> bytes:
    """
    image to compressed and flattened format

    Args:
      image (list): image as a list of floats

    Returns:
      bytes: compressed bytes
    """
    FlattenedImage = self._flatten(image)
    buf = struct.pack('%sf' % len(FlattenedImage), *FlattenedImage)
    return base64.b64encode(self.compressionFunc(buf)).decode('ascii')

  def setCompressionFunc(self, compressionFunc):
    if isinstance(compressionFunc, str):
      self.__setCompressionFromStr(compressionFunc)
    else:
      self.compressionFunc = compressionFunc
  
  def __setCompressionFromStr(self, CompressionName : str) -> void:
    compressionFunctions = {
      "zlib": zlib.compress
    }
    self.compressionFunc = compressionFunctions[CompressionName]
  
  def setttd(self, ttd: float) -> void:
    """
    set time until dead

    Args:
      ttd (float): time until dead in seconds
    """
    self._ttd = ttd
  
  def create(self, data) -> str:
    """
    convert entry data to json format

    Args:
      data (list): data, here it's an image to stream.

    Returns:
      str: entry data in json format
    """
    import base64
    entry = {}
    entry.update({"data":self.imageToCompressedVector(data)}) # compressed data
    entry.update({"timestamp":time()}) # time stamp
    entry.update({"ttd":self._ttd}) # time until dead
    entry.update({"shape":array(data).shape}) # shape - used to reconstruct video client side
    return json.dumps(entry)

def random_image(x, y):
  import random
  d = []
  for i in range(x):
    xs = []
    for j in range(y):
      xs.append(random.random())
    d.append(xs)
  return d

if __name__ == "__main__":
  d = random_image(3, 5)
  eg = StreamEntry("zlib", 2, d)
  print(eg.output)