import zlib
from time import time
from json import dumps
import struct
import base64
from numpy import array

void = None

class StreamEntry:
  def __init__(self, compressionFunc, ttd, ttmi, image):
    self.setCompressionFunc(compressionFunc)
    self._ttd = ttd
    self._ttmi = ttmi
    self.output = self.create(image)
    return self.output
  
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
    import sys
    buf = struct.pack('%sf' % len(image), *image)
    return base64.b64encode(self.compressionFunc(buf, level = 1)).decode('ascii')

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
    return dumps(entry)

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
  times = 20
  import cv2
  cap = cv2.VideoCapture(0)
  
  import sys
  frames = []
  print("taking frames")
  for i in range(times):
    ret, frame = cap.read()
    frames.append(frame)
  print("starting entries")
  st = time()
  for i in range(times):
    eg = StreamEntry("zlib", 2, 300, frames[i].flatten())
    if i % 10 == 0:
      print(sys.getsizeof(eg.output)/1000000)
  print(times/(time() - st))