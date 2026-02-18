from panda3d.core import Point3, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, CollisionBox, ClockObject, WindowProperties, BitMask32, TextNode, Texture
from panda3d.core import PerlinNoise2
from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.InputStateGlobal import inputState
from direct.gui.OnscreenText import OnscreenText


class Game(ShowBase):
    def __init__(self):
        super().__init__()

        self.disableMouse()

        
        props = WindowProperties()
        props.setSize(1920,1080 )
        props.setFullscreen(True)
        props.setTitle("Minecraft")
        props.setIconFilename("logo.ico")
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)


        self.center_mouse()

        self.camera.setPos(5, -15, 3)

        self.blocks = {}

        self.block_model = self.loader.loadModel("block.egg")
        self.block_tex = self.loader.loadTexture("dirt.png")
        self.block_tex.setMinfilter(Texture.FTNearest) 
        self.block_tex.setMagfilter(Texture.FTNearest)
        self.block_tex.setAnisotropicDegree(1)
        self.block_model.setTexture(self.block_tex, 1)

        self.place_block(Point3(0, 0, 0))

        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()

        self.picker_node = CollisionNode('mouseRay')
        self.picker_node.setFromCollideMask(BitMask32.bit(1))
        self.picker_node.setIntoCollideMask(BitMask32.allOff())

        self.picker_np = self.camera.attachNewNode(self.picker_node)

        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)

        self.picker.addCollider(self.picker_np, self.pq)

        self.accept('mouse1', self.break_block)
        self.accept('mouse3', self.add_block)

        self.noise = PerlinNoise2()

        self.terrain_scale = 0.1  
        self.terrain_height = 5   

#movimiento
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('backward', 's')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('right', 'd')

        self.speed = 10
        self.sensitivity = 0.15

        self.crosshair = OnscreenText(
            text="+",
            pos=(0, 0),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ACenter,
            mayChange=False
        )
        self.paused = False
        self.pause_menu = DirectFrame(frameColor=(0, 0, 0, 0.7),frameSize=(-0.5, 0.5, -0.3, 0.3),pos=(0, 0, 0))
        self.resume_button = DirectButton(text="Continuar",scale=0.07,command=self.toggle_pause,pos=(0, 0, 0.1),parent=self.pause_menu)
        self.quit_button = DirectButton(text="Salir",scale=0.07,command=self.userExit,pos=(0, 0, -0.1),parent=self.pause_menu)
        self.pause_menu.hide()
        self.accept('escape', self.toggle_pause)



        self.taskMgr.add(self.update_task, "updateTask")
        self.terrain_size = 30 
        for x in range(-self.terrain_size, self.terrain_size):
            for y in range(-self.terrain_size, self.terrain_size):
                z = int((self.noise(x * self.terrain_scale, y * self.terrain_scale) + 1) / 2 * self.terrain_height)
                self.place_block(Point3(x, y, z))

#bloques
    def place_block(self, pos):
        key = (int(pos.x), int(pos.y), int(pos.z))
        if key in self.blocks:
            return
    
        new_block = self.block_model.copyTo(self.render)
        new_block.setPos(key)
    
        cnode = CollisionNode('block_cnode')
        cnode.addSolid(CollisionBox(Point3(0, 0, 0), 0.5, 0.5, 0.5))
        cnode.setIntoCollideMask(BitMask32.bit(1))
        cnode.setFromCollideMask(BitMask32.allOff())
    
        new_block.attachNewNode(cnode)
    
        self.blocks[key] = new_block
    
    def break_block(self):
        hit = self.get_mouse_hit()
        if hit:
            pos, normal = hit
            key = (int(pos.x), int(pos.y), int(pos.z))
            if key in self.blocks:
                self.blocks[key].removeNode()
                del self.blocks[key]

    def add_block(self):
        hit = self.get_mouse_hit()
        if hit:
            pos, normal = hit
            new_pos = pos + normal
            self.place_block(new_pos)

#mouse
    def get_mouse_hit(self):
        if not self.mouseWatcherNode.hasMouse():
            return None

        mpos = self.mouseWatcherNode.getMouse()
        self.picker_ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())

        self.picker.traverse(self.render)

        if self.pq.getNumEntries() > 0:
            self.pq.sortEntries()
            entry = self.pq.getEntry(0)

            point = entry.getSurfacePoint(self.render)
            normal = entry.getSurfaceNormal(self.render)

            block_pos = Point3(int(round(point.x - normal.x * 0.01)),int(round(point.y - normal.y * 0.01)),int(round(point.z - normal.z * 0.01)))

            normal = Point3(int(round(normal.x)),int(round(normal.y)),int(round(normal.z)))

            return block_pos, normal

        return None

    def update_task(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        if not self.paused:
            self.update_mouse()
            self.update_movement(dt)
        return Task.cont


    def center_mouse(self):
        self.win.movePointer(
            0,
            self.win.getXSize() // 2,
            self.win.getYSize() // 2
        )

    def update_mouse(self):
        if self.paused:  
            return

        if not self.mouseWatcherNode.hasMouse():
            return

        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        center_x = self.win.getXSize() // 2
        center_y = self.win.getYSize() // 2

        dx = x - center_x
        dy = y - center_y

        if dx != 0 or dy != 0:
            h = self.camera.getH() - dx * self.sensitivity
            p = self.camera.getP() - dy * self.sensitivity
            p = max(-90, min(90, p))
            self.camera.setHpr(h, p, 0)

        
            if not self.paused:
                self.center_mouse()

    def update_movement(self, dt):
        forward = self.camera.getQuat().getForward()
        right = self.camera.getQuat().getRight()

        move = Point3(0, 0, 0)

        if inputState.isSet('forward'):
            move += forward
        if inputState.isSet('backward'):
            move -= forward
        if inputState.isSet('left'):
            move -= right
        if inputState.isSet('right'):
            move += right

        move.setZ(0)

        if move.lengthSquared() > 0:
            move.normalize()
            self.camera.setPos(self.camera.getPos() + move * self.speed * dt)


    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_menu.show()
            props = WindowProperties()
            props.setCursorHidden(False)  
            props.setMouseMode(WindowProperties.M_absolute)  
            self.win.requestProperties(props)
        else:
            self.pause_menu.hide()
            props = WindowProperties()
            props.setCursorHidden(True)  
            props.setMouseMode(WindowProperties.M_relative) 
            self.win.requestProperties(props)
            self.center_mouse()




app = Game()
app.run()
