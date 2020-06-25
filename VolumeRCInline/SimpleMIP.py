from .Camera import *
import VkInline as vki

rp = vki.Rasterizer(['volume','camera', 'k', 'b', 'step'])

rp.add_draw_call(vki.DrawCall(
'''
layout (location = 0) out vec2 vUV;
void main() 
{
    vec2 grid = vec2((gl_VertexIndex << 1) & 2, gl_VertexIndex & 2);
    vec2 vpos = grid * vec2(2.0f, 2.0f) + vec2(-1.0f, -1.0f);
    gl_Position = vec4(vpos, 1.0f, 1.0f);
    vUV = grid;
}
''',
'''
layout (location = 0) in vec2 vUV;
layout (location = 0) out vec4 outColor;

#define FLT_MAX 3.402823466e+38

void main() 
{
    vec3 pos_pix = camera.upper_left + vUV.x * camera.ux + vUV.y * camera.uy;
    vec3 ray_origin = camera.origin;
    vec3 direction =  normalize(pos_pix - ray_origin);

    float half_x = float(volume.dims.x-1) * 0.5 * volume.spacings.x;
    float half_y = float(volume.dims.y-1) * 0.5 * volume.spacings.y;
    float half_z = float(volume.dims.z-1) * 0.5 * volume.spacings.z;

    float tmin = 0.0;
    float tmax = FLT_MAX;

    if (direction.x!=0.0)
    {
        float t0 = min((-half_x - ray_origin.x)/direction.x, (half_x - ray_origin.x)/direction.x);
        float t1 = max((-half_x - ray_origin.x)/direction.x, (half_x - ray_origin.x)/direction.x);
        tmin = max(t0, tmin);
        tmax = min(t1, tmax);
    }

    if (direction.y!=0.0)
    {
        float t0 = min((-half_y - ray_origin.y)/direction.y, (half_y - ray_origin.y)/direction.y);
        float t1 = max((-half_y - ray_origin.y)/direction.y, (half_y - ray_origin.y)/direction.y);
        tmin = max(t0, tmin);
        tmax = min(t1, tmax);
    }

    if (direction.z!=0.0)
    {
        float t0 = min((-half_z - ray_origin.z)/direction.z, (half_z - ray_origin.z)/direction.z);
        float t1 = max((-half_z - ray_origin.z)/direction.z, (half_z - ray_origin.z)/direction.z);
        tmin = max(t0, tmin);
        tmax = min(t1, tmax);
    }

    if (tmax<=tmin)
        discard;

    float max_intensity = 0.0;
    for (float t = tmin; t<=tmax; t+=step)
    {
        vec3 pos = ray_origin + t * direction;
        float intensity = get_intensity(volume, pos);
        if (intensity > max_intensity)
            max_intensity = intensity;
    }
    max_intensity = clamp(k * max_intensity + b, 0.0, 1.0);
    outColor = vec4(max_intensity, max_intensity, max_intensity, 1.0);    
}
'''))


class SimpleMIP:
    def __init__(self):
        self.vol = None
        self.origin = glm.vec3()
        self.lookat = glm.vec3()
        self.vup = glm.vec3()
        self.vfov = 45.0
        self.aperture = 0.0
        self.focus_dist = 1.0
        self.window_width = 1.0
        self.window_center = 0.5
        self.step = 0.85

    def add_volume(self, vol):
        self.vol = vol
        return 0

    def set_camera(self, lookfrom, lookat, vup, vfov):
        self.origin = glm.vec3(lookfrom)
        self.lookat = glm.vec3(lookat)
        self.vup = glm.vec3(vup)
        self.vfov = vfov

    def set_window(self, window_width, window_center):
        self.window_width = window_width
        self.window_center = window_center

    def set_step(self, step):
        self.step = step

    def render(self, target):
        d_camera = Camera(target.width(), target.height(), self.origin, self.lookat, self.vup, self.vfov, self.aperture, self.focus_dist)
        d_k = vki.SVFloat(1.0/self.window_width)
        d_b = vki.SVFloat(0.5-self.window_center/self.window_width)
        d_step = vki.SVFloat(self.step)
        rp.launch([3], [target], None, [0.0, 0.0, 0.0, 1.0], 1.0, [self.vol, d_camera, d_k, d_b, d_step], tex3ds=[self.vol.tex])


