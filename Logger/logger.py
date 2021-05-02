from pySql import *
from pyqt5Custom import *

class Action(ChildButton):
    def __init__(self, action, toolTip = None):
        ChildButton.__init__(self)
        self.setObjectName(action)
        border = self.getText("border")["border"]
        if toolTip is None:
            toolTip = action.capitalize()
        border.setToolTip(toolTip)
        self.addText(border)
        self.addTextToGrid("border")
        self.setFixedWidth(30)
        self.currentColor = self.defaultColor()
        
    def defaultColor(self):
        return self.backgroundColor if self.entered else self.hoverColor
                
    def findPoint(self, x, p1, p2):
        slope = (p2.y()-p1.y()) / (p2.x()-p1.x())
        intercept = p1.y()-slope*p1.x()
        return QPoint(x, int(slope*x + intercept))
    
    def paint(self, p):  
        return p  
    
    def paintEvent(self, QPaintEvent):
        p = QPainter()
        p.begin(self)
        self.currentColor = self.defaultColor()
        p.setPen(QPen(self.currentColor, 2, Qt.SolidLine))
        p = self.paint(p)
        p.end()
        
class Refresh(Action):
    def __init__(self, logger):
        self.__logger = logger
        Action.__init__(self, "refresh")
        border = self.getText("border")["border"]
        s = Style(border.styleSheet())
        s.setAttribute("border", "0")
        border.setStyleSheet(s.css())
        self.addText(border)
        self.addTextToGrid("border")
        self.setFixedHeight(30)
        self.setUsers(None)
        self.setObjectName("refresh")
        
    def paint(self, p):
        w, h = (self.width(), self.height())
        i = 14
        start = i//2
        s = start//2
        p.drawArc(start, start, w-i, h-i, 30*16, 300*16)
        a = QPoint(w-i, h-i-s)
        b = QPoint(w-i+start+s, start)
        c = self.findPoint(b.x()-2, a, b)
        c.setY(c.y()+start)
        p.setBrush(self.currentColor)
        p.drawPolygon(QPolygon([a, b, c]))
        return p
    
    def mouseLeftReleased(self, QMouseEvent):
        Action.mouseLeftReleased(self, QMouseEvent)
        if self.checkUsers():
            if self.__users.getCurrentEditorId() > 0:
                self.__users.refreshItems(self.__users.getCurrentEditorId())
            else:
                self.__users.refreshItems()
        else:
            self.__logger.refreshLogger()
            
    def checkUsers(self):
        return not self.__users is None
    
    def setUsers(self, users):
        self.__users = users
        
class ItemCell(ChildButton):
    def __init__(self, text, child, column, user, users):
        self.__users = users
        self.__user = user
        self.__column = column
        buttonText = ButtonText(text, "text")
        buttonText.setAlignment(Qt.AlignCenter)
        buttonText.textHoverColor = Qt.white
        self.__buttonText = buttonText
        ChildButton.__init__(self, buttonText)
        child = child(text)
        child.setFixedHeight(0)
        s = Style(child.styleSheet())
        s.setAttribute("background-color", "transparent")
        s.setAttribute("color", "white")
        child.setStyleSheet(s.css())
        self.__child = child
        self.addChildren(child)
        self.addTextToGrid("text", Qt.AlignCenter)
        self.addChildToGrid(child, Qt.AlignCenter)
        self.setObjectName(str(column))
        self.installEventFilter(self)
        
    def autoSize(self):
        if self.isVisible():
            width = self.getUserHeader(self.__column-1).width()
            if self.width() != width:
                self.setFixedWidth(width)
                self.__buttonText.setFixedWidth(width)
                self.__child.setFixedWidth(width)
                
    def eventFilter(self, QObject, QEvent):
        self.autoSize()
        return ChildButton.eventFilter(self, QObject, QEvent)
                
    def getUserHeader(self, column = None):
        h = self.__users.getHeaders(self.__user)
        if column is None:
            return h
        return h[column]
    
    def mousePressEvent(self, QMouseEvent):
        ChildButton.mousePressEvent(self, QMouseEvent)

    def enterCell(self):
        self.__buttonText.setVisible(False)
        self.__child.setFixedHeight(self.height())
    
    def leaveCell(self):
        self.__buttonText.setVisible(True)
        self.__child.leaveCell()
        self.__child.setFixedHeight(0)
        self.__buttonText.setText(self.__child.result())
        
class Description(ChildLineBox):
    def __init__(self, text):
        ChildLineBox.__init__(self, text, message=None)
        self.setAlignment(Qt.AlignCenter)
        
    def leaveCell(self):
        self.deselect()
        
    def result(self):
        return self.text()
    
class TimeSpent(ChildComboBox):
    def __init__(self, text):
        ChildComboBox.__init__(self, text)
        self.setCurrentText(text)
        self.setArrowButton(None)
        #self.getCombo().backgroundColor = Qt.transparent
        
    def leaveCell(self):
        pass
    
    def result(self):
        return self.currentText()
    
class Item(ScrollButton):
    def __init__(self, index, row, itemId, user, users, items):
        self.__row = row
        self.__itemId = itemId
        self.__user = user
        self.__users = users
        self.__items = items
        ScrollButton.__init__(self, index)
        self.setObjectName("{}_{}".format(user, itemId))
        cells = {}
        for i in range(1, 5):
            cell = self.createCell("hi"+str(itemId), i)
            cells[cell.objectName()] = cell
        self.addChildren(*list(cells.values()))
        boxLayout = BoxLayout(Qt.Horizontal, *list(cells.keys()))
        self.addBoxLayoutToGrid(boxLayout)
        self.clickColor = None
        self.hoverColor = Qt.gray
        self.setFixedHeight(50)
        
    def createCell(self, text, column):
        return ItemCell(text, Description, column, self.__user, self.__users)
        
    def getItemsScroll(self):
        return self.__items.getItemsScroll()
    
    def getCells(self, *columns):
        columns = [str(c) for c in columns]
        return tuple(self.getChildren("buttons", *columns).values())
    
    def checkEditorId(self):
        return self.__users.getCurrentEditorId() > 0
    
    def enter(self, QMouseEvent):
        if self.checkEditorId():
            ScrollButton.enter(self, QMouseEvent)
            for c in self.getCells():
                c.enterCell()
            
    def leave(self, QMouseEvent):
        if self.checkEditorId():
            ScrollButton.leave(self, QMouseEvent)
            for c in self.getCells():
                c.leaveCell()
    
    def mouseMove(self, QMouseEvent):
        self.getItemsScroll().mouseMove(QMouseEvent)
            
    def mouseLeftPressed(self, QMouseEvent):
        ScrollButton.mouseLeftPressed(self, QMouseEvent)
        self.getItemsScroll().mouseLeftPressed(QMouseEvent)
                
    def mouseLeftReleased(self, QMouseEvent):
        h = self.hoverColor
        self.hoverColor = None
        ScrollButton.mouseLeftReleased(self, QMouseEvent)
        self.hoverColor = h
        self.getItemsScroll().mouseLeftReleased(QMouseEvent)
        
    def getRow(self):
        return self.__row
    
    def getItemId(self):
        return self.__itemId
               
class Items(Form):
    def __init__(self, user, userId, users, logger):
        self.__user = user
        self.__userId = userId
        self.__users = users
        self.__logger = logger
        self.__index = 1
        Form.__init__(self)
        self.tablelize(True).setWaitScreen("")
        self.setColumnSize(1).setRowsPerChunk(4)
        self.queryItems()
        self.setAddingItems(True)
        
    def refresh(self):
        print("refreshing", self.__user, ":", self.__userId)
        self.clearForm()
        self.__index = 1
        self.queryItems()
        self.__logger.loadChunks(self.getItemsScroll())
        
    def loadChunk(self):
        if self.__logger.getCurrentEditorId() < 1:
            Form.loadChunk(self)
        
    def createItem(self, itemId):
        return Item(self.__index, self.newFormRow(), itemId, self.__user, self.__users, self)
        
    def queryItems(self):
        for i in range(1, 61):
            self.addButton(self.createItem(i), self.getFont())
            self.__index += 1
           
    def getRows(self, *rowNumbers):
        if self.formSize() > 0:
            search = SearchForm().searchClasses(Item)
            rows = self.searchObjects(search).mergeResults().results
            rows = tuple(rows.values())
            if len(rowNumbers) > 0:
                rows = tuple([r for r in rows if r.getRow() in rowNumbers])
            return rows
        return ()
        
    def getItemsScroll(self):
        return self.getParent()

    def getUser(self):
        return self.__user

    def getUserId(self):
        return self.__userId
    
class ItemsScroll(ScrollArea):
    def __init__(self, user, userId, users, logger):
        self.__user = user
        self.__userId = userId
        self.__users = users
        self.__logger = logger
        ScrollArea.__init__(self, Items(user, userId, users, logger).group())
        self.setBackground(str(userId))
        self.setDraggable(True)
        self.setScrollBarVisibility(False, Qt.Vertical)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                
    def verticalScrollValueChanged(self):
        value, getBar = ScrollArea.verticalScrollValueChanged(self)
        self.synchronizeScrolls(value)
        return (value, getBar)
    
    def synchronizeScrolls(self, value):
        if self.__users.getCurrentEditorId() < 1:
            for s in self.__users.getItemsScroll():
                if not s is self:
                    v = Qt.Vertical
                    s.scrollBarValues[v] = value
                    s.scrollBars[v].setValue(value)
         
    def getUsersScroll(self):
        return self.__users.getUsersScroll()
    
    def getItems(self):
        return self.getWidgetOrLayout().getForm()
    
    def getUsers(self):
        return self.__users
    
    def mouseMove(self, QMouseEvent):
        ScrollArea.mouseMove(self, QMouseEvent)
        self.getUsersScroll().mouseMove(QMouseEvent)
           
    def mouseLeftPressed(self, QMouseEvent):
        ScrollArea.mouseLeftPressed(self, QMouseEvent)
        self.getUsersScroll().mouseLeftPressed(QMouseEvent)
               
    def mouseLeftReleased(self, QMouseEvent):
        ScrollArea.mouseLeftReleased(self, QMouseEvent)
        self.getUsersScroll().mouseLeftReleased(QMouseEvent)
        
class Leader(Action):
    def __init__(self, userId, users):
        self.setLeader(False)
        self.__userId = userId
        self.__users = users
        Action.__init__(self, "leader", "Set leader")
        if self.checkLeaderId():
            self.setLeader(True)
            self.__users.setCurrentLeaderButton(self)
        
    def paint(self, p):
        i, j, k = (18, 5, 2)
        w, h = (self.width()-i, self.height()-i)
        p.drawEllipse(9, j, w, h)
        start = QPoint(j+k, i)
        w += j
        h -= k
        p.drawArc(start.x(), start.y(), w, h, 0*16, 180*16)
        start.setY(start.y()+h-j+1)
        end = QPoint(start.x()+w, start.y())
        p.drawLine(start, end)
        return p
    
    def defaultColor(self):
        if self.isLeader():
            return self.backgroundColor
        return Action.defaultColor(self)
    
    def paintEvent(self, QPaintEvent):
        Action.paintEvent(self, QPaintEvent)
        if self.isLeader():
            self.setColor(self, self.backgroundRole(), self.hoverColor)
        border = self.getText("border")["border"]
        s = Style(border.styleSheet())
        s.setAttribute("border", "1px solid black")
        border.setStyleSheet(s.css())
        self.addText(border)
        self.addTextToGrid("border")
    
    def getCurrentLeaderId(self):
        return self.__users.getCurrentLeaderId()
    
    def checkLeaderId(self):
        return self.__userId == self.getCurrentLeaderId()
    
    def setLeader(self, isLeader):
        self.__isLeader = isLeader
        
    def isLeader(self):
        return self.__isLeader
    
    def getUserId(self):
        return self.__userId
    
    def getUsersScroll(self):
        return self.__users.getUsersScroll()
       
    def mouseLeftReleased(self, QMouseEvent):
        s = self.startPosition
        Action.mouseLeftReleased(self, QMouseEvent)
        if not self.isLeader():
            if s == QMouseEvent.pos():
                self.setLeader(True)
                self.__users.setCurrentLeader(self.__userId)
                self.__users.setCurrentLeaderButton(self)
        self.leave(QMouseEvent)
        self.getUsersScroll().mouseLeftReleased(QMouseEvent)
        
    def mouseMove(self, QMouseEvent):
        if not self.isLeader():
            self.leaveOnMove(QMouseEvent)
        self.getUsersScroll().mouseMoveEvent(QMouseEvent)
        
    def mouseLeftPressed(self, QMouseEvent):
        Action.mouseLeftPressed(self, QMouseEvent)
        self.getUsersScroll().mouseLeftPressed(QMouseEvent)
          
class Edit(Action):
    def __init__(self, user, userId, users):
        self.setClicked(False)
        self.setLeader(None)
        self.__userId = userId
        self.__user = user
        self.__users = users
        Action.__init__(self, "edit")
        if self.checkEditorId():
            self.setClicked(True)
        
    def setClicked(self, isClicked):
        self.__isClicked = isClicked
        
    def setLeader(self, leader):
        self.__leader = leader
        
    def paint(self, p):
        h, w = (8, self.width())
        p.drawLine(4, h, w-18, h)
        p.drawLine(w-4, h, w-6, h)
        h += 8
        p.drawLine(4, h, w-23, h)
        p.drawLine(w-4, h, w-5, h)
        h += 8
        p.drawLine(4, h, w-24, h)
        p.drawLine(w-4, h, w-10, h)
        a = QPoint(w-12, 4)
        b = QPoint(10, h-8)
        i = 7
        c = QPoint(b.x(), b.y()+i+3)
        d = QPoint(b.x()+i, b.y()+i)
        e = QPoint(a.x()+i, a.y()+i)
        p.drawPolygon(QPolygon([a, b, c, d, e]))
        p.drawLine(b, d)
        i = 3
        f = self.findPoint(a.x()-i, a, b)
        g = self.findPoint(e.x()-i, e, d)
        p.drawLine(f, g)
        return p
    
    def __switchColors(self):
        b = self.backgroundColor
        self.backgroundColor = self.hoverColor
        self.hoverColor = b
    
    def paintEvent(self, QPaintEvent):
        Action.paintEvent(self, QPaintEvent)
        if self.__isClicked:
            self.setClicked(False)
            self.setColor(self, self.backgroundRole(), self.hoverColor)
            self.__switchColors()
            self.__users.setEditorView(self.__user, self.__userId)
            self.__leader.setEnabled(not self.__leader.isEnabled())
        border = self.getText("border")["border"]
        s = Style(border.styleSheet())
        s.setAttribute("border", "1px solid black")
        border.setStyleSheet(s.css())
        self.addText(border)
        self.addTextToGrid("border")
        
    def getUsersScroll(self):
        return self.__users.getUsersScroll()
       
    def mouseLeftReleased(self, QMouseEvent):
        s = self.startPosition
        Action.mouseLeftReleased(self, QMouseEvent)
        if s == QMouseEvent.pos():
            self.setClicked(True)
        self.leave(QMouseEvent)
        self.getUsersScroll().mouseLeftReleased(QMouseEvent)
        
    def mouseMove(self, QMouseEvent):
        self.leaveOnMove(QMouseEvent)
        self.getUsersScroll().mouseMoveEvent(QMouseEvent)
        
    def mouseLeftPressed(self, QMouseEvent):
        Action.mouseLeftPressed(self, QMouseEvent)
        self.getUsersScroll().mouseLeftPressed(QMouseEvent)
           
    def getLastEditorId(self):
        return self.__users.getLastEditorId()
    
    def checkEditorId(self):
        return self.__userId == self.getLastEditorId()
      
class Header(ButtonText):
    def __init__(self, text, user, userId, users):
        self.__users = users
        text = " {} ".format(text)
        attribute = "{}_{}_{}".format(text.lower().replace(" ", "_"), user, userId)
        ButtonText.__init__(self, text, attribute, "1px solid black")
        self.setAlignment(Qt.AlignCenter)
        self.textClickColor = None
        self.textHoverColor = None
        self.setFixedHeight(35)
        s = Style()
        s.setWidget("QLabel")
        s.setAttribute("background-color", "gray")
        s.setAttribute("color", "white")
        s.setAttribute("border", "1px solid black")
        self.setStyleSheet(s.css())
        
    def getUsersScroll(self):
        return self.__users.getUsersScroll()

    def mouseMove(self, QMouseEvent):
        self.getUsersScroll().mouseMoveEvent(QMouseEvent)
        
    def mouseLeftPressed(self, QMouseEvent):
        self.getUsersScroll().mouseLeftPressed(QMouseEvent)
            
    def mouseLeftReleased(self, QMouseEvent):
        self.getUsersScroll().mouseLeftReleased(QMouseEvent)
    
class User(Button):        
    def __init__(self, name, userId, users):
        self.__users = users
        self.__usersScroll = None
        user = ButtonText(name, name)
        user.textHoverColor = None
        space = ButtonText(attribute="space")
        Button.__init__(self, user, space)
        self.setObjectName(name)
        leader, edit = (Leader(userId, users), Edit(name, userId, users))
        self.addChildren(leader, edit)
        leader.setButton(None)
        edit.setButton(None)
        edit.setLeader(leader)
        boxLayout = BoxLayout(Qt.Horizontal, name, "space", leader.objectName(), edit.objectName())
        self.addBoxLayoutToGrid(boxLayout, Qt.AlignCenter)
        self.clickColor = None
        self.hoverColor = None
        
    def checkUsersScroll(self):
        return not self.__usersScroll is None
    
    def getUsersScroll(self):
        return self.__users.getUsersScroll()
        
    def mouseMove(self, QMouseEvent):
        self.getUsersScroll().mouseMoveEvent(QMouseEvent)
        
    def mouseLeftPressed(self, QMouseEvent):
        self.getUsersScroll().mouseLeftPressed(QMouseEvent)
            
    def mouseLeftReleased(self, QMouseEvent):
        self.getUsersScroll().mouseLeftReleased(QMouseEvent)
        
class Users(Form):
    def __init__(self, logger, deliverable):
        self.__logger = logger
        Form.__init__(self)
        search = SearchForm().searchNames("deliverable")
        deliverable = deliverable.searchObjects(search).mergeResults().results
        deliverable = tuple(deliverable.values())[0]
        self.__deliverable = deliverable
        self.tablelize(True)
        logger.db.query("select get_user(user_id) as user, user_id from user order by user_id")
        users = logger.db.results[2]
        users = dict([tuple(user.values()) for user in users])
        for u in users:
            self.addButton(User(u, users[u], self), self.getFont(16))
        self.addRow()
        headers = ("Start Date", "End Date", "Description", "Time Spent")
        for u in users:
            for h in headers:
                self.addButtonText(font = self.getFont(12), buttonText = Header(h, u, users[u], self))
        self.addRow()
        for u in users:   
            self.addScrollArea(ItemsScroll(u, users[u], self, logger))
        self.addRow() 
        
    def getLogger(self):
        return self.__logger
        
    def getUsers(self, *names):
        search = SearchForm().searchClasses(User)
        users = self.searchObjects(search).mergeResults().results
        if len(names) > 0:   
            u = []
            for n in names:
                if n in users:
                    u.append(users[n])      
            return tuple(u)
        return tuple(users.values())
        
    def getHeaders(self, *users):
        search = SearchForm().searchClasses(Header)
        headers = self.searchObjects(search).mergeResults().results
        if len(users) > 0:
            userHead = []
            for u in users:
                for h in headers:
                    if u in h:
                        userHead.append(headers[h])
            return tuple(userHead)
        return tuple(headers.values())
         
    def getItemsScroll(self, *userIds):
        search = SearchForm().searchClasses(ScrollArea)
        scrolls = self.searchObjects(search).mergeResults().results
        u, s = (len(userIds), len(scrolls))          
        if u > 0 and u < s:
            removeIds = [i+1 for i in range(s)]
            removeIds = list(set(removeIds)-set(userIds))
            for r in removeIds:
                scrolls.pop(str(r))
        return tuple(scrolls.values())
     
    def getItems(self, *userIds):
        return tuple([s.getWidgetOrLayout().getForm() for s in self.getItemsScroll(*userIds)])
     
    def refreshItems(self, *userIds):
        for i in self.getItems(*userIds):
            i.refresh()
    
    def getUsersScroll(self):
        return self.getParent()
        
    def setEditorView(self, user, userId):
        if self.__currentLeader.getUserId() != userId:
            if self.__currentLeader.isLeader():
                self.__leaveLeader()
            else:
                self.__currentLeader.setLeader(True)
        search = SearchForm().searchClasses(User, Header)
        users = self.searchObjects(search).mergeResults().results
        users = tuple(users.values())
        for u in users:
            if not user in u.objectName():
                u.setVisible(not u.isVisible())
                if u.isVisible():
                    if isinstance(u, User):
                        leader, edit = tuple(u.getChildren("buttons").values())
                        if not leader.isLeader():
                            leader.leave(QMouseEvent)
                        edit.leave(QMouseEvent)
        for s in self.getItemsScroll():
            if s.objectName() != str(userId):
                s.setVisible(not s.isVisible())
        self.updateCurrentEditor(userId)
        if self.getCurrentEditorId() < 1:
            self.refreshItems(userId)
            
    def setCurrentLeaderButton(self, leader):
        self.__currentLeader = leader
        self.__logger.db.query("select deliverable_id, deliverable from deliverable where user_id = get_current_leader_id()")
        d = self.__logger.db.results[2][0]
        num, d = tuple(d.values())
        self.__deliverable.setText("Deliverable #{}: {}".format(num, d))
        
    def __leaveLeader(self):
        self.__currentLeader.setLeader(False)
        self.__currentLeader.leave(QMouseEvent)
        
    def setCurrentLeader(self, userId):
        self.__leaveLeader()
        self.updateCurrentLeader(userId)
    
    def getCurrentLeaderId(self):
        return self.__logger.getCurrentLeaderId()
  
    def getCurrentEditorId(self):
        return self.__logger.getCurrentEditorId()
  
    def getLastEditorId(self):
        return self.__logger.getLastEditorId()
  
    def updateCurrentLeader(self, userId):
        return self.__logger.updateCurrentLeader(userId)
        
    def updateCurrentEditor(self, userId):
        return self.__logger.updateCurrentEditor(userId)
        
    def updateLastEditor(self):
        return self.__logger.updateLastEditor()
        
class UsersScroll(ScrollArea):
    def __init__(self, users, logger):
        self.__logger = logger
        self.beginWait(False)
        ScrollArea.__init__(self, users.group())
        self.setDraggable(True)
        self.setScrollBarVisibility(False, Qt.Horizontal)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def beginWait(self, beginWait):
        self.__beginWait = beginWait

    def horizontalScrollValueChanged(self):
        value, getBar = ScrollArea.horizontalScrollValueChanged(self)
        self.__logger.updateHorizontalScroll(value)
        return (value, getBar)
    
    def defaultHorizontalScrollValue(self):
        ScrollArea.defaultHorizontalScrollValue(self)
        return self.__logger.getHorizontalScrollValue()

    def checkEditorId(self):
        editorId = self.__logger.getCurrentEditorId()
        if editorId is None:
            return False
        return editorId < 1
    
    def mouseMoveEvent(self, QMouseEvent):
        if self.checkEditorId():
            ScrollArea.mouseMoveEvent(self, QMouseEvent)
            
    def mousePressEvent(self, QMouseEvent):
        if self.checkEditorId():
            ScrollArea.mousePressEvent(self, QMouseEvent)
            
    def mouseReleaseEvent(self, QMouseEvent):
        if self.checkEditorId():
            ScrollArea.mouseReleaseEvent(self, QMouseEvent)
            
class Deliverable(Form):
    def __init__(self, logger):
        Form.__init__(self, logger)
        self.addButtonText("", "deliverable", font = self.getFont(18)).addRow(Qt.AlignCenter)
        self.addButton(Refresh(logger)).addRow(Qt.AlignCenter)
    
class Logger(ParentWindow):    
    def __init__(self):
        app = QApplication(sys.argv)
        self.__autoSize = False
        try:
            self.db = AccessSql(True, accessType=AccessSql.PY_ACCESS)
            self.__start = True
        except SystemExit as e:
            self.db = str(e)
            self.__start = False
        super().__init__()
        sys.exit(app.exec_())  
        
    def checkDb(self):
        return not type(self.db) is str
    
    def refreshLogger(self):
        pass
      
    def setupWindow(self):
        ParentWindow.setupWindow(self)
        self.setWindowTitle("CSC 450 Music Sharing Logger")
        if self.checkDb():
            vbox = QVBoxLayout(self)
            self.__deliverable = Deliverable(self)
            self.__users = Users(self, self.__deliverable)
            vbox.addLayout(self.__deliverable.layout())
            self.__usersScroll = UsersScroll(self.__users, self)
            vbox.addWidget(self.__usersScroll)
            self.center()
        else:
            error = MessageBox(self.db, MessageBox.CRITICAL_ICON)
            error.setWindowTitle("Connection Error")
            error.center()
            self.addChildWindows(error)
        isMaximized = self.getWindowStateMaximized()
        if not isMaximized is None:
            if isMaximized:
                self.showMaximized()
        self.installEventFilter(self)
        
    def changeEvent(self, QEvent):
        ParentWindow.changeEvent(self, QEvent)
        if self.isVisible():
            if self.__start:
                if self.checkDb():
                    search = SearchForm().searchNames("refresh")
                    refresh = self.__deliverable.searchObjects(search).mergeResults().results["refresh"]
                    refresh.setUsers(self.__users)
                    search = SearchForm().searchClasses(ScrollArea)
                    scrolls = self.__users.searchObjects(search).mergeResults().results
                    scrolls = tuple(scrolls.values())
                    for s in scrolls:
                        self.loadChunks(s)
                self.__start = False
                
    def loadChunks(self, scroll):
        chunks = 0
        size = scroll.getWidgetOrLayoutRowCount()
        if self.isMaximized():
            if size < 20:
                chunks = int((20 - size) / scroll.getWidgetOrLayoutRowsPerChunk())
        else:
            if size < 8:
                chunks = 1
        if chunks > 0:
            for _ in range(chunks):
                scroll.widgetOrLayoutLoadChunk()
                 
    def eventFilter(self, QObject, QEvent):
        if self.isVisible():
            if self.__autoSize:
                self.__autoSize = False
                scrolls = self.__users.getItemsScroll()
                for s in scrolls:
                    if s.isVisible():
                        rows = s.getItems().getRows()
                        if len(rows) > 0:
                            for r in rows:
                                cells = r.getCells()
                                for c in cells:
                                    c.autoSize()
                        self.loadChunks(s)
        return ParentWindow.eventFilter(self, QObject, QEvent)
                 
    def maximizeEvent(self, QEvent):
        self.updateWindowStateMaximized(True)
        self.__autoSize = True
        
    def restoreEvent(self, QEvent):
        self.updateWindowStateMaximized(False)
        self.__autoSize = True

    def closeEvent(self, QEvent):
        ParentWindow.closeEvent(self, QEvent)
        if self.checkDb():
            self.db.callProcedure(None, "update_last_editor")
            self.db.query("select user_id, get_user(user_id) as user from last_editor")
            self.db.close()
    
    def __getId(self, table):
        if self.checkDb():
            self.db.query("select get_{}_id() as id".format(table))
            return self.db.results[2][0]["id"]
        return None
    
    def __updateTable(self, table, userId):
        if self.checkDb():
            if userId is None:
                self.db.callProcedure(None, "update_{}".format(table))
            else:
                self.db.callProcedure(None, "update_{}".format(table), userId)
            self.db.query("select user_id, get_user(user_id) as user from {}".format(table))
            return self.db.results[2][0]
        return None
            
    def getCurrentLeaderId(self):
        return self.__getId("current_leader")
  
    def getCurrentEditorId(self):
        return self.__getId("current_editor")
  
    def getLastEditorId(self):
        return self.__getId("last_editor")
  
    def updateCurrentLeader(self, userId):
        return self.__updateTable("current_leader", userId)
        
    def updateCurrentEditor(self, userId):
        return self.__updateTable("current_editor", userId)
        
    def updateLastEditor(self):
        return self.__updateTable("last_editor", None)
    
    def updateWindowStateMaximized(self, isMaximized):
        if self.checkDb():
            self.db.callProcedure(None, "update_logger_window_maximized", isMaximized)
            self.db.query("select get_logger_window_maximized() as maximized")
            return bool(self.db.results[2][0]["maximized"])
        return None
    
    def getWindowStateMaximized(self):
        if self.checkDb():
            self.db.query("select get_logger_window_maximized() as maximized")
            return bool(self.db.results[2][0]["maximized"])
        return None
        
    def updateHorizontalScroll(self, value):
        editorId = self.getCurrentEditorId()
        if not editorId is None:
            if editorId < 1:
                self.db.callProcedure(None, "update_users_horizontal_scroll", value)
                self.db.query("select horizontal from users_scroll")
                return self.db.results[2][0]["horizontal"]
        return None
            
    def getHorizontalScrollValue(self):
        editorId = self.getCurrentEditorId()
        if not editorId is None:
            if editorId < 1:
                self.db.query("select horizontal from users_scroll")
                return self.db.results[2][0]["horizontal"]
        return None

if __name__ == "__main__":
    Logger()
#     QtWorkbenchSql()