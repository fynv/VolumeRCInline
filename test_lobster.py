import numpy as np 
from PIL import Image
import VkInline as vki
import VolumeRCInline as vrc

VK_FORMAT_R8G8B8A8_SRGB = 43

raw_cthead = np.fromfile('lobster.raw', dtype=np.uint8)
raw_cthead = np.reshape(raw_cthead, (56, 324, 301))

ray_caster = vrc.SimpleMIP()
gpuvol = vrc.U8Volume(ray_caster, raw_cthead, (1.0, 1.0, 1.4))
ray_caster.set_camera((150.0, 200.0, 100.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 45.0)

colorBuf = vki.Texture2D(640, 480, VK_FORMAT_R8G8B8A8_SRGB)
ray_caster.render(colorBuf)

image_out = np.empty((480, 640, 4), dtype=np.uint8)
colorBuf.download(image_out)
Image.fromarray(image_out, 'RGBA').save('output.png')


