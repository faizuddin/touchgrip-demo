# Prediction server for N9
# Author: Faiz (noorm@dcs.gla.ac.uk)
#!/usr/bin/python

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib
import numpy as np
import getopt, sys, csv

from rungp import NumpyGP

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class RPCN9Server:
    
    #screen size (px)
    SCREENSIZE = [854,480]

    # maximum capacitive value
    MAX_CAP = 65535
    
    # Back-in-time kernel stuff
    BIT_SECS = 0.5
    USER_KERNEL = 12
    
    def __init__(self, port_num):            
        self.port = port_num
        self.hand = 1
        
        # create GP object
        self.gp = NumpyGP(None,None,None,None)

        # gp hyper-parameters [xcov1 xcov2 ycov1 ycov2 xlik ylik]
        self.hpars = []
        
        # horizontal kernel
        self.xK = []
        
        # vertical kernel
        self.yK = []
        
        # sensor values used to train kernel
        self.traininput = []
        
        # touch targets used to train kernel
        self.traintarget = []
        
        self.xiK = []
        self.yiK = []
        
        # load computed kernel stuff (from MATLAB)
        hyp_filename = 'usermodel/hyperpars/user%d-%dsecs-%d.csv' % (self.USER_KERNEL,self.BIT_SECS,self.hand)
        xK_filename = 'usermodel/kernels/xk-user%d-%dsecs-%d.csv' % (self.USER_KERNEL,self.BIT_SECS,self.hand)
        yK_filename = 'usermodel/kernels/yk-user%d-%dsecs-%d.csv' % (self.USER_KERNEL,self.BIT_SECS,self.hand)
        input_filename = 'usermodel/traininput/sensor-user%d-%dsecs-%d.csv' % (self.USER_KERNEL,self.BIT_SECS,self.hand)
        touch_target_filename = 'usermodel/touchtargets/target-user%d-%dsecs-%d.csv' % (self.USER_KERNEL,self.BIT_SECS,self.hand)
        self.loadcsv(xK_filename,yK_filename,hyp_filename,input_filename,touch_target_filename)
        
        # Create server
        self.server = SimpleXMLRPCServer(("", int(self.port)), requestHandler=RequestHandler, allow_none=True)
        self.server.register_introspection_functions()
        
        # register server functions               
        self.server.register_function(self.predict, 'predict')
        
        #print '# training samples = %d' % (np.matrix(self.traininput).shape)
        #print hyp_filename
        #print ' hypx.cov1 = %.6f\n hypx.cov2 = %.6f\n hypy.cov1 = %.6f\n hypy.cov2 = %.6f\n hypx.lik = %.6f\n hypy.lik = %.6f\n' % (self.hpars[0,0], self.hpars[0,1], self.hpars[0,2], self.hpars[0,3], self.hpars[0,4], self.hpars[0,5])
                
        self.hpars = np.array(self.hpars)
        self.xcov = self.hpars[:][:,0:2]
        self.ycov = self.hpars[:][:,2:4]
        self.xlik = self.hpars[:][:,4]
        self.ylik = self.hpars[:][:,5]
        
        self.xcov = np.array(self.xcov)[0].tolist()
        self.ycov = np.array(self.ycov)[0].tolist()
        self.xlik = np.array(self.xlik)[0].tolist()
        self.ylik = np.array(self.ylik)[0].tolist()
        
        self.xK = np.array(self.xK)
        self.yK = np.array(self.yK)
        self.traintarget = np.array(self.traintarget)
        
        self.gpmultiplier()
                  
    def runserver(self):
        # Run the server's main loop
        print 'N9 touch prediction server listening at port:%s' % self.port
        self.server.serve_forever()
    
    def predict(self,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,c24):
        #n9cap_mat = [];
        
        n9cap_mat = np.matrix([c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,c24])
        n9cap_mat = self.scalecap(n9cap_mat)
        print n9cap_mat        
        (x,y) = self.gpxy(n9cap_mat)
        
        return xmlrpclib.FloatType(x),xmlrpclib.FloatType(y)
        
    def loadcsv(self, xK_filename, yK_filename, hyp_filename, traininput_filename, target_filename):
        with open(xK_filename, 'rb') as csvfile:
            rdr = csv.reader(csvfile)
            for row in rdr:
                self.xK.append(map(float, row))
        
        with open(yK_filename, 'rb') as csvfile:
            rdr = csv.reader(csvfile)
            for row in rdr:
                self.yK.append(map(float, row))
        
        with open(hyp_filename, 'rb') as csvfile:
            rdr = csv.reader(csvfile)
            for row in rdr:
                self.hpars.append(map(float, row))
                
        with open(traininput_filename, 'rb') as csvfile:
            rdr = csv.reader(csvfile)
            for row in rdr:
                self.traininput.append(map(float, row))

        with open(target_filename, 'rb') as csvfile:
            rdr = csv.reader(csvfile)
            for row in rdr:
                self.traintarget.append(map(float, row))                
                
    def scalecap(self, cap_signal):
        scaled_values = np.divide(cap_signal, self.MAX_CAP, dtype=np.float32)
        return scaled_values
        
    def gpmultiplier(self):
        tmpx = self.xK + (self.xlik * np.eye(len(self.xK)))
        self.xiK = np.linalg.inv(tmpx)
        
        tmpy = self.yK + (self.ylik * np.eye(len(self.yK)))
        self.yiK = np.linalg.inv(tmpy)
        
    def gpxy(self, realtimeinput):
        # compute x and y test kernel from real time sensor values coming from the N9
        testxK = self.gp.__gauss__(np.matrix(realtimeinput), np.matrix(self.traininput), self.xcov)
        testyK = self.gp.__gauss__(np.matrix(realtimeinput), np.matrix(self.traininput), self.ycov)
                
        # predict target       
        x = np.dot(testxK * self.xiK, self.traintarget[:,0:1])
        y = np.dot(testyK * self.yiK, self.traintarget[:,1:2])

        # rescale x
        x = np.add(x, 0.5, dtype=np.float32)
        x = np.multiply(x, self.SCREENSIZE[0], dtype=np.float32)
        
        # rescale y       
        y = np.add(y, 0.5, dtype=np.float32)
        y = np.multiply(y, self.SCREENSIZE[1], dtype=np.float32)  
        
        return (x,y)

def main(argv):
    port_num = None    
    
    try:
        opts, operands = getopt.getopt(sys.argv[1:],'p:')
        
        if len(sys.argv) < 2:
            print "Please use the correct arguments"
            sys.exit()
        else:
            for option, value in opts:
                if option == "-p":
                    if int(value) > 0 or isinstance(value,(int)):
                        port_num = value
                    else:
                        print "Invalid argument: %s " % value
                        sys.exit()
                        
    except getopt.GetoptError,err:
        print str(err)
        sys.exit()
    
    #server object
    app = RPCN9Server(port_num)

    app.runserver()
    #app.runplotter()
    
if __name__ == "__main__":
    main(sys.argv)