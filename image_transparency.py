# Copyright (c) 2011, Andy Mutz and Adam Sah
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging, struct

# to test:
#for fn in glob.glob("*gif"):
#  print "%s: %s" % (fn, str(bool(it.is_gif_transparent(open(fn).read()))))

def pack_bits(bits):
  '''convert a bit (bool or int) tuple into a int'''
  packed = 0
  level = 0
  for bit in bits:
    if bit:
      packed += 2 ** level    
    level += 1
  return packed

def get_bits(flags, reverse=False, bits=8):
  '''return a list with $bits items, one for each enabled bit'''
  mybits = [ 1 << x for x in range(bits) ]
  ret = []
  for bit in mybits:
    ret.append(flags & bit != 0)
  if reverse:
    ret.reverse()
  return ret

def is_png_transparent(img_bytes):
  # TODO: support palette transparency
  keyvalue = struct.unpack('<B', img_bytes[25:26])
  return (keyvalue[0] & 4)

def is_gif_transparent(img_bytes):
  # select color table info byte of the GIF header
  headerkeys = struct.unpack('<B', img_bytes[10:11])
  headerflags = get_bits(headerkeys[0])
  global_color_table_flag = headerflags[7]
  logging.info("gif: global colorf table flag=%d", global_color_table_flag)
  if global_color_table_flag: 
    # GIF header has a global color table, so the offset to the
    # transparency byte is len+16 and the offset to 0xf9 is len+13
    color_table_length = 3* 2 ** (pack_bits(headerflags[:3]) + 1)
    logging.info("gif: global color table len=%d", color_table_length)
  else: 
    # GIF uses a local color table, so we doesn't need to calculate
    # offset to the transparency byte; it's 16.
    color_table_length = 0
  xparent_offset = 16 + color_table_length
  logging.info("transparency byte offset=%d", xparent_offset)
  graphic_control_label = struct.unpack('<B', img_bytes[xparent_offset -2:xparent_offset -1])
  logging.info("char which should be 0xf9=%x"+hex(graphic_control_label[0]))
  graphicflags = struct.unpack('<B', img_bytes[xparent_offset:xparent_offset+1])
  is_alpha = get_bits(graphicflags[0])[0]
  logging.info("transparency flag=%d", is_alpha)
  return bool(is_alpha)

