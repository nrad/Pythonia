##\example test_visual_prism.py 
# Video
# \n
# \n@htmlonly<iframe width="640" height="360" src="http://www.youtube.com/embed/OMB93RVrFMg?feature=player_detailpage" frameborder="0" allowfullscreen></iframe>@endhtmlonly
# \n
#\n\n <small>Click on each function for more detail </small>\n
#
#

import peacevisual
import random
import gl
def callback():
	peacevisual.beginDraw(gl.GL_LINES)
	for i in xrange(200):
		peacevisual.setColor4f(random.random(),random.random(),random.random(),0.2)
		peacevisual.drawVertex2f(-0.9,0)
		peacevisual.drawVertex2f(0.9,random.uniform(-1,1))
	peacevisual.endDraw()
	return 1

peacevisual.init_peacevisual(800,600)
print peacevisual.setCallback(callback),"callback set"#Important order
peacevisual.setLineWidth(10000.0)
peacevisual.start()

