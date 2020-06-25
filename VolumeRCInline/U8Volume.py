import glm
import VkInline as vki
from VkInline.SVCombine import *

VK_FORMAT_R8_SRGB = 15

class U8Volume(vki.ShaderViewable):
    def __init__(self, ray_caster, h_vol, spacings=(1.0, 1.0, 1.0)):
        self.dims = [h_vol.shape[2], h_vol.shape[1], h_vol.shape[0]]
        self.spacings = spacings
        self.tex = vki.Texture3D(self.dims[0], self.dims[1], self.dims[2], VK_FORMAT_R8_SRGB)
        self.tex.upload(h_vol)
        self.d_texId = vki.SVUInt32(ray_caster.add_volume(self))
        self.d_dims = vki.SVIVec3(glm.ivec3(self.dims))
        self.d_spacings = vki.SVVec3(glm.vec3(spacings))
        self.m_cptr = SVCombine_Create({'texId':  self.d_texId, 'dims': self.d_dims, 'spacings': self.d_spacings}, 
'''
float get_intensity(in Comb_#hash# vol, vec3 pos)
{
	pos = pos/(vec3(vol.dims)*vol.spacings) + 0.5;	
	return texture(arr_tex3d[vol.texId], pos).x;
}
''')
