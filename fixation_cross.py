def fixation_cross(self):
    
    size = pixel_to_degrees(self.settings.monitor_height, self.settings.monitor_distance, 1920, 128)
    
    outer = visual.Circle(win=self.mywindow, units='degrees', radius=size,
                            fillcolor='black', opacity=1)
    inner = visual.Circle(win=self.mywindow, units='degrees', radius=size/3,
                            fillcolor='black', opacity=1)
    cross = visual.ShapeStim(
        win=self.mywindow, vertices='cross',
        units='degrees', size=(size, size),
        ori=0.0, pos=(0, 0), anchor='center',
        lineWidth=1.0, colorSpace='rgb',  lineColor='white', fillColor='white',
        opacity=None, depth=-8.0, interpolate=True)
    
    outer.draw()
    cross.draw()
    inner.draw()
