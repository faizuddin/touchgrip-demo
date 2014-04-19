# Author: Faiz
# Email: noorm@dcs.gla.ac.uk 

import pygame, struct, os, sys, getopt, socket, xmlrpclib, random

class Demo:
    
    # Constants
    X = 854
    Y = 480
    
    #            R    G    B
    GRAY     = (100, 100, 100)
    NAVYBLUE = ( 60,  60, 100)
    WHITE    = (255, 255, 255)
    RED      = (255,   0,   0)
    GREEN    = (  0, 255,   0)
    BLUE     = (  0,   0, 255)
    YELLOW   = (255, 255,   0)
    ORANGE   = (255, 128,   0)
    PURPLE   = (255,   0, 255)
    CYAN     = (  0, 255, 255)
    BLACK    = (  0,   0,   0)

    #colour
    TEXTCOL = (255,255,255)
    TARGETCOL = (0,255,0)
    
    #font size
    LABELFONTSIZE = 18
    BUTTONFONTSIZE = 40
    
    # delay before next prediction (ms)
    DELAY = 1000

    def __init__(self, server_ip_addr, port_num, split_type):
        
        self.server_host = server_ip_addr
        self.port = port_num
        self.hand = 1
        self.split_type = split_type
        
        svrstring = "http://%s:%s/RPC2" % (self.server_host,self.port)
        
        self.svr = xmlrpclib.ServerProxy(svrstring)
        
        #initialise app
        pygame.init()
        pygame.display.set_caption('Demo')
        self.screen = pygame.display.set_mode((Demo.X,Demo.Y), pygame.FULLSCREEN)
        self.screen.fill((0,0,0))
        
        canvasrect = self.screen.get_rect()
        self.canvas = self.screen.subsurface((canvasrect))
        
        # main loop control flag
        self.done = False
        
        # yep, split the screen        
        if self.split_type == 1:
            (self.right_rect, self.right_screen, self.left_rect, self.left_screen) = self.splithorz()
        elif self.split_type == 2:
            (self.top_rect, self.top_screen, self.bot_rect, self.bot_screen) = self.splitvert()
        elif self.split_type == 3:
            (self.topright_rect, self.topright_screen, self.botright_rect, self.botright_screen, self.topleft_rect, self.topleft_screen, self.botleft_rect, self.botleft_screen) = self.splitquad()

        # check extcap sensor
        if not os.path.exists("/dev/extcap"):
            print 'No /dev/extcap found, using random values instead!'
            self.extcap = None
        else:
            self.extcap = open('/dev/extcap', 'r')
            self.extcap_data = [0 for x in range(24)]
            self.extcap_struct = struct.Struct("<" + "H" * 24)
        
        # pause at start
        self.pause = True
    
    def run(self):        
        while not self.done:           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print 'Screen touched'
            
            # get touch state
            self.touchstate = pygame.mouse.get_pressed()
            self.touchpos = pygame.mouse.get_pos()

            # start button
            if self.pause:
                self.screen.fill((0,0,0))             
                self.drawbutton(self.canvas, (0,255,0), 2)
            else:
                # get capacitive values            
                capdata = self.readcap()
                
                c1 = xmlrpclib.FloatType(capdata[0])
                c2 = xmlrpclib.FloatType(capdata[1])
                c3 = xmlrpclib.FloatType(capdata[2])
                c4 = xmlrpclib.FloatType(capdata[3])
                c5 = xmlrpclib.FloatType(capdata[4])
                c6 = xmlrpclib.FloatType(capdata[5])
                c7 = xmlrpclib.FloatType(capdata[6])
                c8 = xmlrpclib.FloatType(capdata[7])
                c9 = xmlrpclib.FloatType(capdata[8])
                c10 = xmlrpclib.FloatType(capdata[9])
                c11 = xmlrpclib.FloatType(capdata[10])
                c12 = xmlrpclib.FloatType(capdata[11])
                c13 = xmlrpclib.FloatType(capdata[12])
                c14 = xmlrpclib.FloatType(capdata[13])
                c15 = xmlrpclib.FloatType(capdata[14])
                c16 = xmlrpclib.FloatType(capdata[15])
                c17 = xmlrpclib.FloatType(capdata[16])
                c18 = xmlrpclib.FloatType(capdata[17])
                c19 = xmlrpclib.FloatType(capdata[18])
                c20 = xmlrpclib.FloatType(capdata[19])
                c21 = xmlrpclib.FloatType(capdata[20])
                c22 = xmlrpclib.FloatType(capdata[21])
                c23 = xmlrpclib.FloatType(capdata[22])
                c24 = xmlrpclib.FloatType(capdata[23])
                
                (x, y) = self.svr.predict(c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22, c23, c24)
                
                print("x = %d, y = %d" % (x, y))

                #highlight quadrant
                self.hlquadrant(x, y)

            pygame.display.update()
                 
    def readcap(self):
        if self.extcap:
            ed = self.extcap.read(self.extcap_struct.size)            
            if ed and len(ed) == self.extcap_struct.size:
                extcap_data = self.extcap_struct.unpack(ed)
                #self.capcounter += 1
        else:
            print 'ext_cap is not available'
            extcap_data = [random.randint(0, 65536) for x in range(24)]
               
        return extcap_data

    def splitvert(self):
        top_rect = self.screen.get_rect()
        top_rect.width = self.screen.get_rect().width / 2
        top_screen = self.screen.subsurface(top_rect)
        
        bot_rect = top_rect.move(top_rect.width, 0)
        bot_screen = self.screen.subsurface(bot_rect)

        return top_rect, top_screen, bot_rect, bot_screen
    
    def splithorz(self):
        right_rect = self.screen.get_rect()
        right_rect.height = right_rect.height / 2
        right_screen = self.screen.subsurface(right_rect)

        left_rect = right_rect.move(0, right_rect.height)
        left_screen = self.screen.subsurface(left_rect)

        return right_rect, right_screen, left_rect, left_screen

    def splitquad(self):
        (right_rect, right_screen, left_rect, left_screen) = self.splithorz()
        #(top_rect, top_screen, bot_rect, bot_screen) = self.splitvert()

        topleft_rect = left_rect
        topright_rect = right_rect

        topright_rect.width = right_rect.width / 2
        topleft_rect.width = left_rect.width / 2

        botright_rect = topright_rect.move(topright_rect.width, 0)
        botleft_rect = topleft_rect.move(topleft_rect.width, 0)

        topright_screen = self.screen.subsurface(topright_rect)
        topleft_screen = self.screen.subsurface(topleft_rect)
        botright_screen = self.screen.subsurface(botright_rect)
        botleft_screen = self.screen.subsurface(botleft_rect)

        return topright_rect, topright_screen, botright_rect, botright_screen, topleft_rect, topleft_screen, botleft_rect, botleft_screen

    def hlquadrant(self, x,y):
        if not self.pause:
            if self.split_type == 2: #vertical
                if self.top_rect.collidepoint(x,y):
                    self.top_screen.fill((255,0,0))
                else:
                    self.top_screen.fill((0,0,0))
        
                if self.bot_rect.collidepoint(x,y):
                    self.bot_screen.fill((0,0,255))
                else:
                    self.bot_screen.fill((0,0,0))
            
            elif self.split_type == 1: #horizontal
                if self.left_rect.collidepoint(x,y):
                    self.left_screen.fill((255,0,0))
                else:
                    self.left_screen.fill((0,0,0))
            
                if self.right_rect.collidepoint(x,y):
                    self.right_screen.fill((0,0,255))
                else:
                    self.right_screen.fill((0,0,0))

            # quad split
            elif self.split_type == 3:
                if self.topleft_rect.collidepoint(x, y):
                    self.topleft_screen.fill(Demo.RED)
                else:
                    self.topleft_screen.fill(Demo.BLACK)

                if self.topright_rect.collidepoint(x, y):
                    self.topright_screen.fill(Demo.GREEN)
                else:
                    self.topright_screen.fill(Demo.BLACK)

                if self.botleft_rect.collidepoint(x, y):
                    self.botleft_screen.fill(Demo.BLUE)
                else:
                    self.botleft_screen.fill(Demo.BLACK)

                if self.botright_rect.collidepoint(x, y):
                    self.botright_screen.fill(Demo.YELLOW)
                else:
                    self.botright_screen.fill(Demo.BLACK)

    def drawlabel(self,surf,text,col,x,y,size):
        labelfont = pygame.font.SysFont("Arial",size)
        label = labelfont.render(text,0,col)
        rotatedLabel = pygame.transform.rotate(label,90)
        surf.blit(rotatedLabel,(x,y))
    
    def drawbutton(self,surf,col,thickness):
        # setup sound
        pausebeep = pygame.mixer.Sound('/usr/share/sounds/ui-tones/snd_message_fg.wav')
        
        # set up the label text
        pauseLabelFont = pygame.font.SysFont("Arial",40)
        
        # labels
        #if self.pause == True:
        centrexoffset = 20
        centreyoffset = 40
        pauseLabel = pauseLabelFont.render("Start", True, (255,255,255))
        
        #rotate the label
        rotatedPauseLabel = pygame.transform.rotate(pauseLabel, 90)
        
        #get the rectangle from text
        textRect = rotatedPauseLabel.get_rect()
        textRect.centerx = surf.get_rect().centerx
        textRect.centery = surf.get_rect().centery
        
        #create button rectangle
        buttonRect = pygame.Rect(textRect.left - 20, textRect.top - 20, textRect.width + 60, textRect.height + 80)
        
        #draw rectangle to screen
        pygame.draw.rect(surf, col, buttonRect, thickness)
        
        #blit button label to screen
        surf.blit(rotatedPauseLabel,(buttonRect.centerx - centrexoffset, buttonRect.centery - centreyoffset))
        
        # determine if touch point is within the rectangle
        if self.touchstate[0] == 1 and buttonRect.collidepoint(self.touchpos[0],self.touchpos[1]):
            pausebeep.play()
                        
            self.pause = False
                                
            pygame.time.delay(self.DELAY)
        
        #back to main loop
        return
        
def main(argv):
    server_ip_addr = None
    port_num = None
    split_type = None
    
    try:
        opts, operands = getopt.getopt(sys.argv[1:],'h:p:s:',["host=","port=","type="])
        
        if len(sys.argv) < 2:
            print "Not enough arguments..."
            sys.exit()
        else:
            for option, value in opts:
                
                if option == "-h":
                    try:
                        socket.inet_aton(value) # Validate IP address
                        server_ip_addr = value
                    except socket.error:                                      
                        print "Invalid IP address: %s " % value
                        sys.exit()
                elif option == "-p":
                    try:
                        port_num = int(value)
                    except ValueError:
                        print "Invalid port number: %s " % value
                        sys.exit()
                elif option == "-s":
                    try:
                        split_type = int(value)
                    except ValueError:
                        print "Invalid value: %s " % value
                        sys.exit()
                        
    except getopt.GetoptError,err:
        print str(err)
    
    #Demo object
    app = Demo(server_ip_addr,port_num,split_type)
    
    #run application
    app.run()

if __name__ == "__main__":
    main(sys.argv)