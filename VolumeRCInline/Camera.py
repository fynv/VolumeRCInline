import glm
import math
import VkInline as vki
from VkInline.SVCombine import *

class Camera(vki.ShaderViewable):
	def __init__(self, width, height, origin, lookat, vup, vfov, aperture=0.0, focus_dist=1.0):
		theta = vfov * math.pi / 180.0
		half_height = math.tan(theta*0.5)*focus_dist
		size_pix = half_height * 2.0 / height
		half_width = size_pix * width *0.5
		axis_z = glm.normalize(origin - lookat)
		axis_x = glm.normalize(glm.cross(vup, axis_z))
		axis_y = glm.cross(axis_z, axis_x)
		plane_center = origin - axis_z * focus_dist
		upper_left = plane_center - axis_x * half_width + axis_y * half_height
		ux = size_pix * width * axis_x
		uy = -size_pix * height * axis_y
		lens_radius = aperture * 0.5

		self.d_origin = vki.SVVec3(origin)
		self.d_upper_left = vki.SVVec3(upper_left)
		self.d_ux = vki.SVVec3(ux)
		self.d_uy = vki.SVVec3(uy)
		self.d_lens_radius = vki.SVFloat(lens_radius)
		self.m_cptr = SVCombine_Create({'origin':  self.d_origin, 'upper_left': self.d_upper_left, 'ux': self.d_ux, 'uy':self.d_uy, 'lens_radius': self.d_lens_radius}, '')
