#======================================================================================================================================================================
#========================================================   PROJECT TITLE: P2P FILE SHARING APPLICATION   =============================================================
#======================================================================================================================================================================
#========================================================    CSE 5344-002 - COMPUTER NETWORKS , PA3B      =============================================================
#======================================================================================================================================================================
#========================================================                     AUTHORS                     =============================================================
#                                                              1. Amit Anand Ramanand (1001084548)
#                                                              2. Arpitha Patel B.S (1001104361)
#                                                              3. Divya Nityanand (1001112716)
#                                                              4. Rakhee Barkur (1001096946)
#======================================================================================================================================================================
#========================================================        SUBMISSION DATE: 24 - APRIL - 2015       =============================================================
#======================================================================================================================================================================
from Tkinter import *
from ttk import *
import socket
import thread
import threading
from tkFileDialog import askopenfilename
import tkFileDialog
import os
import ntpath
import time

class ChatClient(Frame):
  
  def __init__(self, root):
    Frame.__init__(self, root)
    self.root = root
    self.initUI()
    self.serverSoc = None
    self.serverStatus = 0
    self.buffsize = 1024
    self.allClients = {}
    self.counter = 0
  
  def initUI(self):
    self.root.title("Simeple P2P File sharing system")
    ScreenSizeX = self.root.winfo_screenwidth()
    ScreenSizeY = 0self.root.winfo_screenheight()
    self.FrameSizeX  = 800
    self.FrameSizeY  = 600
    FramePosX   = (ScreenSizeX - self.FrameSizeX)/2
    FramePosY   = (ScreenSizeY - self.FrameSizeY)/2
    self.root.geometry("%sx%s+%s+%s" % (self.FrameSizeX,self.FrameSizeY,FramePosX,FramePosY))
    self.root.resizable(width=True, height=True)
    
    padX = 10
    padY = 10
    parentFrame = Frame(self.root)
    parentFrame.grid(padx=padX, pady=padY, stick=E+W+N+S)
    
    ipGroup = Frame(parentFrame)
    serverLabel = Label(ipGroup, text="Configure: ")
    self.nameVar = StringVar()
    self.nameVar.set("Server")
    nameField = Entry(ipGroup, width=10, textvariable=self.nameVar)
    self.serverIPVar = StringVar()
    self.serverIPVar.set("192.168.1.236")
    serverIPField = Entry(ipGroup, width=15, textvariable=self.serverIPVar)
    self.serverPortVar = StringVar()
    self.serverPortVar.set("8090")
    serverPortField = Entry(ipGroup, width=5, textvariable=self.serverPortVar)
    serverSetButton = Button(ipGroup, text="Set", width=10, command=self.handleSetServer)
    addClientLabel = Label(ipGroup, text="Add next Peer: ")
    self.clientIPVar = StringVar()
    self.clientIPVar.set("192.168.1.244")
    clientIPField = Entry(ipGroup, width=15, textvariable=self.clientIPVar)
    self.clientPortVar = StringVar()
    self.clientPortVar.set("8091")
    clientPortField = Entry(ipGroup, width=5, textvariable=self.clientPortVar)
    clientSetButton = Button(ipGroup, text="Add", width=10, command=self.handleAddClient)
    serverLabel.grid(row=0, column=0)
    nameField.grid(row=0, column=1)
    serverIPField.grid(row=0, column=2)
    serverPortField.grid(row=0, column=3)
    serverSetButton.grid(row=0, column=4, padx=5)
    addClientLabel.grid(row=0, column=5)
    clientIPField.grid(row=0, column=6)
    clientPortField.grid(row=0, column=7)
    clientSetButton.grid(row=0, column=8, padx=5)
    
    readChatGroup = Frame(parentFrame)
    
    self.friends = Listbox(readChatGroup, bg="white", width=30, height=30)
    self.friends.grid(row=0, column=2, sticky=E+N+S)
    self.scrollbar = Scrollbar(readChatGroup)
    self.scrollbar.grid( row=0, column=1, sticky=W+N+S, padx = (0,10) )
    self.receivedChats = Listbox(readChatGroup, bg="white", width=60, height=30,yscrollcommand=self.scrollbar.set)
    self.receivedChats.grid(row=0, column=0, sticky=W+N+S, padx = (0,10))
    self.scrollbar.config(command=self.receivedChats.yview)
    

    browseGroup = Frame(parentFrame)

    
    
    
    browseButton = Button(browseGroup, text="Add File", width=10, command=self.PopulateList)
    browseButton.grid(row=0, column=1, padx=5)
    DownloadButton = Button(browseGroup, text="Download", width=10, command=self.onDownload)
    DownloadButton.grid(row=0, column=2, padx=5)
    self.browseVar = StringVar()
    self.browseField = Entry(browseGroup, width=80, textvariable=self.browseVar)
    self.browseField.grid(row=1, column=0, sticky=W)
    searchbutton = Button(browseGroup, text="Search", width=10, command=self.search_button)
    searchbutton.grid(row=1, column=1, padx=5)

    


    self.statusLabel = Label(parentFrame)

    
    
    ipGroup.grid(row=0, column=0)
    readChatGroup.grid(row=1, column=0)
    browseGroup.grid(row=2, column=0, pady=10)
    
    self.statusLabel.grid(row=3, column=0)
    
    
  def handleSetServer(self):
    if self.serverSoc != None:
        self.serverSoc.close()
        self.serverSoc = None
        self.serverStatus = 0
    serveraddr = (self.serverIPVar.get().replace(' ',''), int(self.serverPortVar.get().replace(' ','')))
    Fileserveraddr = (self.serverIPVar.get().replace(' ',''), 9000)
    try:
        self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSoc.bind(serveraddr)
        self.serverSoc.listen(5)

        self.FileserverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.FileserverSoc.bind(Fileserveraddr)
        self.FileserverSoc.listen(5)
        self.setStatus("Server listening on %s:%s" % serveraddr)
        self.setStatus(" File Server listening on %s:%s" % Fileserveraddr)
        thread.start_new_thread(self.listenClients,())
        thread.start_new_thread(self.listenFileClients,())
        
        
        self.serverStatus = 1
        self.name = self.nameVar.get().replace(' ','')
        if self.name == '':
            self.name = "%s:%s" % serveraddr
    except:
        self.setStatus("Error setting up server")
    
  def listenClients(self):
    while 1:
      clientsoc, clientaddr = self.serverSoc.accept()
      self.setStatus("Client connected from %s:%s" % clientaddr)
      self.addClient(clientsoc, clientaddr)

      thread.start_new_thread(self.handleIncomingFilePaths, (clientsoc, clientaddr))

      
      
    self.serverSoc.close()

  def listenFileClients(self):
    while 1:
      c, addr = self.FileserverSoc.accept()
      self.setStatus("Client connected from %s:%s" % addr)
      t = threading.Thread(target = self.RetrFile, args=("retrThread" , c))
      t.start()
      

    self.FileserverSoc.close()



      
  def handleAddClient(self):
    if self.serverStatus == 0:
      self.setStatus("Set server address first")
      return
    clientaddr = (self.clientIPVar.get().replace(' ',''), int(self.clientPortVar.get().replace(' ','')))
    try:
        clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsoc.connect(clientaddr)
    
        self.setStatus("Connected to client on %s:%s" % clientaddr)
        self.addClient(clientsoc, clientaddr)
        thread.start_new_thread(self.handleIncomingFilePaths, (clientsoc, clientaddr))
        
        
    except:
        self.setStatus("Error connecting to client")







  def handleIncomingFilePaths(self, clientsoc, clientaddr):
    while 1:
      try:
        path = clientsoc.recv(self.buffsize)
        
        if not path:
            break
        self.addReceivedPath("%s:%s" % clientaddr, path)
      except:
          break
    self.removeClient(clientsoc, clientaddr)
    clientsoc.close()
    self.setStatus("Client disconnected from %s:%s" % clientaddr)
  
    

  def addReceivedPath(self, client, msg):
    
    
    self.receivedChats.insert("end",client+": "+msg+"\n")
    
    
    
  
  def addClient(self, clientsoc, clientaddr):
    self.allClients[clientsoc]=self.counter
    self.counter += 1
    self.friends.insert(self.counter,"%s:%s" % clientaddr)

  def PopulateList(self):

    filePath = tkFileDialog.askopenfilename()
    
    print filePath
    
    if filePath == '':
        return
    self.addReceivedPath("me", filePath)
    for client in self.allClients.keys():
      client.send(filePath)


    
      
  

  def onDownload(self):
    
      sels = self.receivedChats.curselection()
      if len(sels)==1:
         sel = self.receivedChats.get(sels[0])
         name=sel.split(' ',1)
         filename=name[1]
         filename=filename.strip()
         Addr=name[0]
         Addr=Addr.strip()
      self.downloadFile(Addr,filename)
      
      
      
      
      
      
      
      

  def downloadFile(self,host,filename):
    hostport=host.split(':')
    port=int(hostport[1])+5
    FileHost=hostport[0]
    
    
    s=socket.socket()
    try:
      
      s.connect((FileHost,9000))
      t=time.time()
      
      if filename != 'q':
          s.send(filename)
          data = s.recv(1024)
          if data[:6] == 'EXISTS':
              filesize = long(data[6:])
              message = raw_input("file Exists. " + str(filesize) + "Bytes, download ? (Y/N)? ->")
              if message == 'y':
                  
                  s.send('OK')
                  directoryFilename = filename.split('/')
                  f= open(os.path.join('C:\Users\Rakhee R\Desktop\Downloads', directoryFilename[len(directoryFilename)-1]) , 'wb')
                  data = s.recv(1024)
                  totalRecv = len(data)
                  f.write(data)
                  while totalRecv < filesize:
                      data = s.recv(1024)
                      totalRecv += len(data)
                      f.write(data)

                  downloadTime=(time.time()-t)
                  print "Download Complete!"
                  print "Download time in seconds:", downloadTime
              else:
                  print " Request Canceled !!"
                  
          else:
              print "File Does not exist!"

      
    
    except:
      print "Peer disconnected and file cannot be downloaded"
    s.close()

  def RetrFile(self,name, sock):
        fName = sock.recv(1024)
        
        filename = ntpath.basename(fName)
        

        
        sub_dir = ''
        directoryArray = fName.split('/')
        
        directoryLen= len(directoryArray)
        size = 0
        while size < directoryLen - 1:
               sub_dir +=  directoryArray[size] + '/'
               size = size+1
        
        
        
              
                              
        filefoundBit = 0

        filepath = os.path.join(sub_dir, filename)
        if os.path.isfile(filepath):
              filefoundBit = 1
              fileSize = os.path.getsize(filepath)
               

                      

       
        
        if filefoundBit:
            sock.send("EXISTS " + repr(fileSize))
            userResponse = sock.recv(1024)
            if userResponse[:2] == 'OK':
                
               
                
                
                with open(filepath, "rb") as f:
                    
                    bytesToSend = f.read()
                    
                    sock.send(bytesToSend)
                    while bytesToSend != "":
                        bytesToSend = f.read()
                        sock.send(bytesToSend)
                        
        else:
            sock.send("ERR")
        print ' File transfer complete! '
        sock.close()
  
      
      


    
  #after retrieve
        
  def search_button(self):
    try:
        var = self.receivedChats.get(0, END)
        var1 = self.browseField.get()
        a=[str(x) for x in var]
        names=[]
        
        for j in a:
          b = j.strip()
          c = ntpath.basename(b)
          names.append(c)
          
          
          if var1 == c:
              
              i=names.index(var1)
              print "success"
              print "file found"
        self.receivedChats.selection_clear(0, END)
        self.receivedChats.selection_set(i, last=None)
         
    except:
      print "File not on the list"

    

   #end of code
 
  def removeClient(self, clientsoc, clientaddr):
      print self.allClients
      self.friends.delete(self.allClients[clientsoc])
      del self.allClients[clientsoc]
      print self.allClients
  
  def setStatus(self, msg):
    self.statusLabel.config(text=msg)
    print msg
      
def main():  
  root = Tk()
  app = ChatClient(root)
  root.mainloop()  

if __name__ == '__main__':
  main()
